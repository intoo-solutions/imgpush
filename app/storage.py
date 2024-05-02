import json
import mimetypes
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
            extension = mimetypes.guess_extension(mime_type)
            metrics_str += f'directory_size{{service="imgpush", extension="{extension}", mime_type="{mime_type}", directory="{settings.FILES_DIR}"}} {data["size"]}\n'
            metrics_str += f'directory_count{{service="imgpush", extension="{extension}", mime_type="{mime_type}", directory="{settings.FILES_DIR}"}} {data["count"]}\n'

        return metrics_str


class S3Storage(Storage):
    def __init__(self):
        self.s3 = boto3.client('s3', 
            endpoint_url = settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY
        )

    def save(self, file, filename):
        self.s3.upload_fileobj(file, settings.S3_BUCKET_NAME, filename)

    def delete(self, filename):
        self.s3.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=filename)

    def exists(self, filename):
        try:
            self.s3.head_object(Bucket=settings.S3_BUCKET_NAME, Key=filename)
            return True
        except:
            return False

    def get(self, filename):
        # Should store the file in a temporary directory
        # and return the path to the file, as well as a function to delete the file

        tmp_path = f"/temporary/{filename}"
        self.s3.download_file(settings.S3_BUCKET_NAME, filename, tmp_path)

        # print content of /tmp directory
        print("Content of /temporary directory:")
        for file in os.listdir("/temporary"):
            print(file)

        return tmp_path, lambda: os.remove(tmp_path)
    
    def get_metrics(self):
        metrics_file = open('metrics.json')
        metrics = json.load(metrics_file)

        metrics_str = ""
        for mime_type in settings.ALLOWED_MIME_FILE_TYPES:
            data = metrics.get(mime_type, {"count": 0, "total_size": 0})
            
            count = data["count"]
            total_size = data["total_size"]
            extension = mimetypes.guess_extension(mime_type)

            metrics_str += f'directory_size{{service="imgpush", extension="{extension}", mime_type="{mime_type}", directory="{settings.FILES_DIR}"}} {total_size}\n'
            metrics_str += f'directory_count{{service="imgpush", extension="{extension}", mime_type="{mime_type}", directory="{settings.FILES_DIR}"}} {count}\n'

        return metrics_str
            
        

def get_storage():
    if settings.USE_S3:
        return S3Storage()
    else:
        return FileSystemStorage()