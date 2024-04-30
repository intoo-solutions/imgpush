import os
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
    # This should return the file-path to the temporary file, as well as a function to delete the temporary file
    def get(self, filename):
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

def get_storage():
    if settings.USE_S3:
        return S3Storage()
    else:
        return FileSystemStorage()