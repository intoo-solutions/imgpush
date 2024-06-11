import settings
import storage
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [Configuration] %(message)s")
logger = logging.getLogger(__name__)

def validate_general_settings():
    if not settings.FILES_DIR and not settings.S3_ENDPOINT:
        raise ValueError("FILES_DIR or S3_ENDPOINT must be set")

    if settings.ALLOWED_MIME_FILE_TYPES == []:
        raise ValueError("ALLOWED_MIME_FILE_TYPES must be set")
    
    if settings.NAME_STRATEGY not in ['randomstr', 'uuidv4']:
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
    
    if settings.S3_METRICS_REBUILDER_THREAD_COUNT < 1:
        raise ValueError("S3_METRICS_REBUILDER_THREAD_COUNT must be greater than 0")
    

if __name__ == "__main__":
    # Check that general settings are valid
    try:
        validate_general_settings()
    except ValueError as e:
        logger.error(f"General settings are invalid: {str(e)}")
        exit(1)

    # Check that the configuration is valid for the storage provider
    storage_provider = storage.get_storage()
    storage_provider.validate_configuration()

    logger.info("Configuration is valid")
    exit(0)
