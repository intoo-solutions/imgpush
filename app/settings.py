import os

FILES_DIR = "/files/"
CACHE_DIR = "/cache/"
OUTPUT_TYPE = None
MAX_UPLOADS_PER_DAY = 1000
MAX_UPLOADS_PER_HOUR = 100
MAX_UPLOADS_PER_MINUTE = 20
ALLOWED_ORIGINS = ["*"]
NAME_STRATEGY = "randomstr"
MAX_TMP_FILE_AGE = 5 * 60
RESIZE_TIMEOUT = 5

VALID_SIZES = []

MAX_SIZE_MB = 16

# Those files will be treated as images, meaning
# they will be resized if the query parameters are present
RESIZABLE_MIME_FILE_TYPE = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/tiff',
    'image/webp',
    'image/svg+xml',
]

# Those files will be allowed to be uploaded
ALLOWED_MIME_FILE_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/tiff',
    'image/webp',
    'image/svg+xml',
    'application/pdf',
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
