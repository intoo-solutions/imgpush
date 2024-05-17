import datetime
import json
import mimetypes
import time
import filetype
import os
import subprocess
import boto3
from abc import ABC, abstractmethod
import settings

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

class FileSystemStorage(Storage):
    def save(self, file, filename):
        file.save(os.path.join(settings.FILES_DIR, filename))

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
                extension = extension[1:] # remove dot from extension
                ps = subprocess.Popen(f"find {settings.FILES_DIR} -type f -name '*.{extension}' | wc -l", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                nbfiles = ps.communicate()[0].split()[0].decode('utf-8')
                size = subprocess.check_output([f'du -c {settings.FILES_DIR}/*.{extension} | tail -n 1 | cut -f 1'], shell=True).decode('utf-8').strip()
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

        last_execution_date = datetime.datetime.now().isoformat()
        metrics_str += f'last_execution_date{{service="imgpush-metrics-rebuilder", directory="{settings.FILES_DIR}"}} {last_execution_date}\n'
        metrics_str += f'last_execution_time_in_milliseconds{{service="imgpush-metrics-rebuilder", directory="{settings.FILES_DIR}"}} {total_time}\n'

        return metrics_str
    
    def __str__(self) -> str:
        return "Directory = %s" % settings.FILES_DIR


class S3Storage(Storage):
    def __init__(self):
        self.s3 = boto3.client('s3', 
            endpoint_url = settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY
        )

    def save(self, file, filename):
        file_size = file.seek(0, os.SEEK_END)
        file.seek(0)  # Reset the file pointer to the beginning to allow S3 to read the file

        mime_type = filetype.guess(file).mime

        self.s3.upload_fileobj(file, settings.S3_BUCKET_NAME, filename)
        update_metrics(file_size, mime_type)
        
    def delete(self, filename):
        try:
            # If the file does not exist, head_object will raise an exception
            object_info = self.s3.head_object(Bucket=settings.S3_BUCKET_NAME, Key=filename)
        except:
            return
        
        file_size, mime_type = object_info["ContentLength"], object_info["ContentType"]

        self.s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=filename)
        update_metrics(file_size, mime_type, remove=True)

    def exists(self, filename):
        try:
            self.s3.head_object(Bucket=settings.S3_BUCKET_NAME, Key=filename)
            return True
        except:
            return False

    def get(self, filename):
        # Should store the file in a temporary directory
        # and return the path to the file, as well as a function to delete the file

        tmp_path = f"/tmp/{filename}"
        self.s3.download_file(settings.S3_BUCKET_NAME, filename, tmp_path)

        return tmp_path, lambda: os.remove(tmp_path)
    
    def get_metrics(self):
        metrics_file = get_or_create_metrics_file()
        metrics = json.load(metrics_file)

        last_execution_date = metrics.get("last_execution_date", datetime.datetime.now().isoformat())
        last_execution_time_in_milliseconds = metrics.get("last_execution_time_in_milliseconds", 0)

        metrics_str = ""
        for mime_type in settings.ALLOWED_MIME_FILE_TYPES:
            data = metrics.get(mime_type, {"count": 0, "total_size": 0})
            
            count = data["count"]
            total_size_in_kilobytes = int(data["total_size"] / 1024)
            extension = mimetypes.guess_extension(mime_type)

            metrics_str += f'directory_size_in_kilobytes{{service="imgpush", extension="{extension}", mime_type="{mime_type}", directory="{settings.S3_BUCKET_NAME} Bucket"}} {total_size_in_kilobytes}\n'
            metrics_str += f'directory_count{{service="imgpush", extension="{extension}", mime_type="{mime_type}", directory="{settings.S3_BUCKET_NAME} Bucket"}} {count}\n'

        metrics_str += f'last_execution_date{{service="imgpush-metrics-rebuilder", directory="{settings.S3_BUCKET_NAME} Bucket"}} {last_execution_date}\n'
        metrics_str += f'last_execution_time_in_milliseconds{{service="imgpush-metrics-rebuilder", directory="{settings.S3_BUCKET_NAME} Bucket"}} {last_execution_time_in_milliseconds}\n'

        return metrics_str

    def __str__(self) -> str:
        return "Endpoint = %s\nBucket name = %s" % (settings.S3_ENDPOINT, settings.S3_BUCKET_NAME)

def get_storage():
    if settings.S3_ENDPOINT is not None:
        return S3Storage()
    else:
        return FileSystemStorage()
    
def get_or_create_metrics_file():
    if not os.path.exists('metrics.json'):
        print("[Metrics] File metrics.json does not exist. Creating it.")
        open('metrics.json', 'w').write('{}')

    return open('metrics.json')

def update_metrics(file_size, mime_type, remove=False):
    metrics_file = get_or_create_metrics_file()
    metrics = json.load(metrics_file)

    data = metrics.get(mime_type, {"count": 0, "total_size": 0})

    if remove:
        data["count"] -= 1
        data["total_size"] -= file_size
    else:
        data["count"] += 1
        data["total_size"] += file_size
    
    metrics[mime_type] = data
    
    metrics_file.close()

    metrics_file = open('metrics.json', 'w')
    json.dump(metrics, metrics_file)
    metrics_file.close()