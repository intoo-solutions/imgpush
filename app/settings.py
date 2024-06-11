import os

#########################################
######          STORAGE             #####
#########################################

# If this option is set to None, FILES_DIR will be used. Otherwise, imgpush will try establish a connection to the S3 endpoint
S3_ENDPOINT = ""
S3_ACCESS_KEY_ID = ""
S3_SECRET_ACCESS_KEY = ""
S3_BUCKET_NAME = ""
S3_FOLDER_NAME = ""

# The directory in which to store the files
FILES_DIR = "/files/"
# The directory in which to store "cached" resized imges
CACHE_DIR = "/cache/"
# This is the path to the metrics file, used by the metrics endpoint for the S3Storage class
METRICS_FILE_PATH = "/metrics/metrics.json"
# Convert the files to this type when uploading
# NOTE: This will only apply to file extensions from the RESIZABLE_MIME_FILE_TYPE setting
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
RESIZABLE_MIME_FILE_TYPE = [
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

for variable in [item for item in globals() if not item.startswith("__")]:
    NULL = "NULL"
    env_var = os.getenv(variable, NULL).strip()
    if env_var is not NULL:
        try:
            env_var = eval(env_var)
        except Exception:
            pass
    globals()[variable] = env_var if env_var is not NULL else globals()[variable]
