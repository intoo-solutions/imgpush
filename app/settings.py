import os as operating_system  # Rename to avoid potential overwrites
import logging
#########################################
######          STORAGE             #####
#########################################

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [Settings] %(message)s")
logger = logging.getLogger(__name__)

# If this option is set to None, FILES_DIR will be used. Otherwise, imgpush will try establish a connection to the S3 endpoint
S3_ENDPOINT = ""
S3_ACCESS_KEY_ID = ""
S3_SECRET_ACCESS_KEY = ""
S3_BUCKET_NAME = ""
S3_FOLDER_NAME = ""

# The directory in which to store the files
FILES_DIR = None
# The directory in which to store "cached" resized imges
CACHE_DIR = "/cache/"
# This is the path to the metrics file, used by the metrics endpoint for the S3Storage class
METRICS_FILE_PATH = "/metrics/metrics.json"
# Convert the files to this type when uploading
# NOTE: This will only apply to file extensions from the RESIZABLE_MIME_FILE_TYPES setting
OUTPUT_TYPE = None

#########################################
######          LIMITS              #####
#########################################

MAX_UPLOADS_PER_DAY = 1000
MAX_UPLOADS_PER_HOUR = 100
MAX_UPLOADS_PER_MINUTE = 20
MAX_TMP_FILE_AGE = 5 * 60
RESIZE_TIMEOUT = 5
MAX_SIZE_MB = 16

#########################################
######          OTHERS              #####
#########################################

ALLOWED_ORIGINS = ["*"]
# Possible values: randomstr, uuidv4
NAME_STRATEGY = "randomstr"
VALID_SIZES = []

#########################################
######          File types          #####
#########################################

# Those files will be treated as images, meaning
# they will be resized if the query parameters are present
RESIZABLE_MIME_FILE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/tiff",
    "image/webp",
    "image/svg+xml",
]

# Those files will be allowed to be uploaded
ALLOWED_MIME_FILE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/tiff",
    "image/webp",
    "image/svg+xml",
    "application/pdf",
]

def _redact(name, value):
    if any(key in name for key in ["SECRET", "PASSWORD", "KEY", "TOKEN"]):
        return "<redacted>"
    return repr(value)


for variable in [item for item in globals() if item.isupper()]:
    default_value = globals()[variable]
    env_raw = operating_system.getenv(variable)
    if env_raw is None:
        logger.info(
            "%s not set; using default: %s", variable, _redact(variable, default_value)
        )
        continue

    env_var = env_raw.strip()
    # Treat empty values as unset so defaults remain in effect
    if env_var == "":
        logger.info(
            "%s set empty; using default: %s", variable, _redact(variable, default_value)
        )
        continue

    try:
        env_val = eval(env_var)
    except Exception:
        env_val = env_var

    logger.info(
        "%s overridden from env; value: %s", variable, _redact(variable, env_val)
    )
    globals()[variable] = env_val
