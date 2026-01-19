import datetime
import fcntl
import json
import logging
import mimetypes
import tempfile
import time
import filetype
import os
import subprocess
import boto3
from botocore.exceptions import ClientError
from abc import ABC, abstractmethod
import settings

logger = logging.getLogger(__name__)


class Storage(ABC):
    @abstractmethod
    def save(self, file, filename):
        pass

    @abstractmethod
    def delete(self, filename):
        pass

    @abstractmethod
    def exists(self, filename):
        pass

    @abstractmethod
    def get(self, filename):
        """
        Should return the file-path to the temporary file, as well as a function to delete the temporary file
        """
        pass

    @abstractmethod
    def get_metrics(self):
        """
        Returns a Prometheus formatted string with the following metrics:
        - Number of files in the bucket grouped file extension
        - Total size of the files in the bucket grouped by file extension
        """
        pass

    @abstractmethod
    def validate_configuration(self):
        """
        Check that the configuration is valid for the storage provider
        """
        pass


class FileSystemStorage(Storage):
    def save(self, file, filename):
        with open(os.path.join(settings.FILES_DIR, filename), "wb") as f:
            f.write(file.read())

    def delete(self, filename):
        path = os.path.join(settings.FILES_DIR, filename)
        # dont allow to delete "."
        if (os.path.exists(path)) and (os.path.isfile(path)):
            os.remove(path)

    def exists(self, filename):
        return os.path.isfile(os.path.join(settings.FILES_DIR, filename))

    def get(self, filename):
        return os.path.join(settings.FILES_DIR, filename), lambda: None

    def get_metrics(self):
        metrics = {}
        start_time = time.time()

        for mime_type in settings.ALLOWED_MIME_FILE_TYPES:
            extension = mimetypes.guess_extension(mime_type)
            if extension:
                extension = extension[1:]  # remove dot from extension
                ps = subprocess.Popen(
                    f"find {settings.FILES_DIR} -type f -name '*.{extension}' | wc -l",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                nbfiles = ps.communicate()[0].split()[0].decode("utf-8")
                size = (
                    subprocess.check_output(
                        [
                            f"du -c {settings.FILES_DIR}/*.{extension} | tail -n 1 | cut -f 1"
                        ],
                        shell=True,
                    )
                    .decode("utf-8")
                    .strip()
                )
                metrics[mime_type] = {"count": nbfiles, "size": size}

        metrics_str = ""
        for mime_type, data in metrics.items():
            size_in_kilobytes = data["size"]
            file_count = data["count"]

            extension = mimetypes.guess_extension(mime_type)
            metrics_str += f'directory_size_in_kilobytes{{service="imgpush", extension="{extension}", mime_type="{mime_type}", directory="{settings.FILES_DIR}"}} {size_in_kilobytes}\n'
            metrics_str += f'directory_count{{service="imgpush", extension="{extension}", mime_type="{mime_type}", directory="{settings.FILES_DIR}"}} {file_count}\n'

        end_time = time.time()
        total_time = (end_time - start_time) * 1000

        last_execution_date = int(time.time())
        metrics_str += f'last_execution_date{{service="imgpush-metrics-rebuilder", directory="{settings.FILES_DIR}"}} {last_execution_date}\n'
        metrics_str += f'last_execution_time_in_milliseconds{{service="imgpush-metrics-rebuilder", directory="{settings.FILES_DIR}"}} {total_time}\n'

        return metrics_str

    def __str__(self) -> str:
        return "Directory = %s" % settings.FILES_DIR

    def validate_configuration(self):
        try:
            if not os.path.exists(settings.FILES_DIR):
                logger.warn(
                    f"Directory {settings.FILES_DIR} does not exist. Creating it."
                )
                os.makedirs(settings.FILES_DIR)
            if not os.path.exists(settings.CACHE_DIR):
                logger.warn(
                    f"Directory {settings.CACHE_DIR} does not exist. Creating it."
                )
                os.makedirs(settings.CACHE_DIR)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise ValueError("Error creating directories")

        is_writable = os.access(settings.FILES_DIR, os.W_OK)
        is_cache_writable = os.access(settings.CACHE_DIR, os.W_OK)

        if not is_writable or not is_cache_writable:
            logger.error(
                f"Directory {'FILES_DIR' if not is_writable else 'CACHE_DIR'} is not writable"
            )
            raise ValueError(
                f"Directory {'FILES_DIR' if not is_writable else 'CACHE_DIR'} is not writable"
            )


class S3Storage(Storage):
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
        )

        # Check that the settings are correct
        # The endpoint should be valid
        # The bucket should exist
        # The credentials should be valid
        try:
            self.s3.list_objects_v2(Bucket=settings.S3_BUCKET_NAME)
        except Exception as e:
            logger.error(f"Error connecting to S3: {e}")
            exit(1)

    def save(self, file, filename):
        file_size = file.seek(0, os.SEEK_END)
        file.seek(
            0
        )  # Reset the file pointer to the beginning to allow S3 to read the file

        mime_type = filetype.guess(file).mime

        self.s3.upload_fileobj(file, settings.S3_BUCKET_NAME, build_path(filename))
        update_metrics(file_size, mime_type)

    def delete(self, filename):
        try:
            # If the file does not exist, head_object will raise an exception
            object_info = self.s3.head_object(
                Bucket=settings.S3_BUCKET_NAME, Key=build_path(filename)
            )
        except ClientError:
            return

        file_size, mime_type = object_info["ContentLength"], object_info["ContentType"]

        self.s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=build_path(filename))
        update_metrics(file_size, mime_type, remove=True)

    def exists(self, filename):
        try:
            self.s3.head_object(
                Bucket=settings.S3_BUCKET_NAME, Key=build_path(filename)
            )
            return True
        except ClientError:
            return False

    def get(self, filename):
        """
        Should store the file in a temporary directory
        and return the path to the file, as well as a function to delete the file
        """
        # Extract extension to preserve it in the temp file (needed for image processing)
        _, extension = os.path.splitext(filename)
        # Use tempfile.mkstemp for secure temporary file creation
        fd, tmp_path = tempfile.mkstemp(suffix=extension)
        os.close(fd)  # Close the file descriptor, boto3 will open it

        self.s3.download_file(settings.S3_BUCKET_NAME, build_path(filename), tmp_path)

        return tmp_path, lambda: os.remove(tmp_path)

    def get_metrics(self):
        metrics_file = get_or_create_metrics_file()
        metrics = json.load(metrics_file)

        last_execution_date = metrics.get("last_execution_date", int(time.time()))

        last_execution_time_in_milliseconds = metrics.get(
            "last_execution_time_in_milliseconds", 0
        )

        metrics_str = ""
        for mime_type in settings.ALLOWED_MIME_FILE_TYPES:
            data = metrics.get(mime_type, {"count": 0, "total_size": 0})

            count = data["count"]
            total_size_in_kilobytes = int(data["total_size"] / 1024)
            extension = mimetypes.guess_extension(mime_type)

            metrics_str += f'directory_size_in_kilobytes{{service="imgpush", extension="{extension}", mime_type="{mime_type}", bucket_name="{settings.S3_BUCKET_NAME}", in_bucket_directory="{settings.S3_FOLDER_NAME}"}} {total_size_in_kilobytes}\n'
            metrics_str += f'directory_count{{service="imgpush", extension="{extension}", mime_type="{mime_type}", bucket_name="{settings.S3_BUCKET_NAME}", in_bucket_directory="{settings.S3_FOLDER_NAME}"}} {count}\n'

        metrics_str += f'last_execution_date{{service="imgpush-metrics-rebuilder", bucket_name="{settings.S3_BUCKET_NAME}", in_bucket_directory="{settings.S3_FOLDER_NAME}"}} {last_execution_date}\n'
        metrics_str += f'last_execution_time_in_milliseconds{{service="imgpush-metrics-rebuilder", bucket_name="{settings.S3_BUCKET_NAME}", in_bucket_directory="{settings.S3_FOLDER_NAME}"}} {last_execution_time_in_milliseconds}\n'

        return metrics_str

    def __str__(self) -> str:
        return "Endpoint = %s\nBucket name = %s" % (
            settings.S3_ENDPOINT,
            settings.S3_BUCKET_NAME,
        )

    def validate_configuration(self):
        # Check that the bucket exists, that credentials are correct, that the provided endpoint is valid, etc.
        try:
            self.s3.list_objects_v2(Bucket=settings.S3_BUCKET_NAME)
        except Exception as e:
            logger.error(f"Error connecting to S3: {e}")
            raise ValueError("Error connecting to S3")


def get_storage():
    if settings.S3_ENDPOINT is not None and settings.S3_ENDPOINT != "":
        return S3Storage()
    else:
        return FileSystemStorage()


def build_path(filename):
    return os.path.join(settings.S3_FOLDER_NAME, filename)


def get_or_create_metrics_file():
    # Create the metrics folder if it does not exist
    if not os.path.exists(os.path.dirname(settings.METRICS_FILE_PATH)):
        os.makedirs(os.path.dirname(settings.METRICS_FILE_PATH))
        logger.info(
            f"Directory {os.path.dirname(settings.METRICS_FILE_PATH)} does not exist. Creating it."
        )

    # Create the metrics file if it does not exist
    if not os.path.exists(settings.METRICS_FILE_PATH):
        logger.info(f"File {settings.METRICS_FILE_PATH} does not exist. Creating it.")
        open(settings.METRICS_FILE_PATH, "w").write("{}")

    return open(settings.METRICS_FILE_PATH)


def update_metrics(file_size, mime_type, remove=False):
    try:
        # Ensure the metrics file exists
        get_or_create_metrics_file().close()

        # Open file for read/write and acquire exclusive lock
        with open(settings.METRICS_FILE_PATH, "r+") as metrics_file:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(metrics_file.fileno(), fcntl.LOCK_EX)

            try:
                metrics = json.load(metrics_file)
            except json.JSONDecodeError:
                metrics = {}

            data = metrics.get(mime_type, {"count": 0, "total_size": 0})

            if remove:
                data["count"] -= 1
                data["total_size"] -= file_size
            else:
                data["count"] += 1
                data["total_size"] += file_size

            metrics[mime_type] = data

            # Rewrite the file from the beginning
            metrics_file.seek(0)
            metrics_file.truncate()
            json.dump(metrics, metrics_file)

            # Lock is automatically released when file is closed
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")
        return
