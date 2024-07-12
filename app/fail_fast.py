import os
import re
import settings
import storage
import logging
import mimetypes

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [Configuration] %(message)s"
)
logger = logging.getLogger(__name__)


def validate_general_settings():
    if not settings.FILES_DIR and not settings.S3_ENDPOINT:
        raise ValueError("FILES_DIR or S3_ENDPOINT must be set")

    if settings.ALLOWED_MIME_FILE_TYPES == []:
        raise ValueError("ALLOWED_MIME_FILE_TYPES must be set")
        
    if settings.RESIZABLE_MIME_FILE_TYPES == []:
        raise ValueError("RESIZABLE_MIME_FILE_TYPE must be set")

    mime_type_pattern = re.compile(r"^'[^']*'(,'[^']*')*$")
    allowed_mime_file_types = os.getenv("ALLOWED_MIME_FILE_TYPES") or ""
    resizable_mime_file_types = os.getenv("RESIZABLE_MIME_FILE_TYPES") or ""

    if not mime_type_pattern.match(allowed_mime_file_types):
        raise ValueError("ALLOWED_MIME_FILE_TYPES must be in the format: 'mime1', 'mime2'")

    if resizable_mime_file_types != "" and not mime_type_pattern.match(resizable_mime_file_types):
        raise ValueError("RESIZABLE_MIME_FILE_TYPES must be in the format: 'mime1', 'mime2'")
    
    # check that all mime types are valid (i.e. they are in mimetypes.types_map or mimetypes.common_types)
    known_mime_types = set(mimetypes.types_map.values()).union(set(mimetypes.common_types.values()))
    
    all_mime_types = []
    all_mime_types.extend(settings.ALLOWED_MIME_FILE_TYPES)
    all_mime_types.extend(settings.RESIZABLE_MIME_FILE_TYPES)
    
    for mime_type in all_mime_types:
        if mime_type not in known_mime_types:
            raise ValueError(f"{mime_type} is not a valid mime type")    
    
    if settings.NAME_STRATEGY not in ["randomstr", "uuidv4"]:
        raise ValueError("NAME_STRATEGY must be either 'randomstr' or 'uuidv4'")

    if settings.MAX_SIZE_MB < 1:
        raise ValueError("MAX_SIZE_MB must be greater than 0")

    if settings.RESIZE_TIMEOUT < 1:
        raise ValueError("RESIZE_TIMEOUT must be greater than 0")

    if settings.MAX_TMP_FILE_AGE < 1:
        raise ValueError("MAX_TMP_FILE_AGE must be greater than 0")

    if settings.MAX_UPLOADS_PER_MINUTE < 1:
        raise ValueError("MAX_UPLOADS_PER_MINUTE must be greater than 0")

    if settings.MAX_UPLOADS_PER_HOUR < 1:
        raise ValueError("MAX_UPLOADS_PER_HOUR must be greater than 0")

    if settings.MAX_UPLOADS_PER_DAY < 1:
        raise ValueError("MAX_UPLOADS_PER_DAY must be greater than 0")


if __name__ == "__main__":
    # Check that general settings are valid
    try:
        validate_general_settings()
    except ValueError as e:
        logger.error(f"General settings are invalid: {str(e)}")
        exit(1)

    # Check that the configuration is valid for the storage provider
    storage_provider = storage.get_storage()
    try:
        storage_provider.validate_configuration()
    except ValueError as e:
        logger.error(f"Storage provider configuration is invalid: {str(e)}")
        exit(1)

    exit(0)
