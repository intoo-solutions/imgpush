import mimetypes
import os
import datetime
import logging
import time
from storage import S3Storage, get_storage
import settings
from collections import defaultdict
import json

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [Metrics] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Fetching storage provider
storage = get_storage()
if storage.__class__.__name__ == "FileSystemStorage":
    logger.error("Cannot rebuild metrics with FileSystemStorage")
    exit(1)

storage: S3Storage = storage

logger.info("Rebuilding from S3 bucket")
for line in storage.__str__().split("\n"):
    logger.info(line)


# The method that will process each object
def process_object(object, metrics):
    try:
        filename = object["Key"]
        size = object["Size"]

        # Skip if it's a folder
        if filename.endswith("/"):
            return

        file_extension = filename.split(".")[-1]
        mime_type = mimetypes.types_map.get(f".{file_extension}", "others")

        # Update the metrics
        metrics[mime_type]["count"] += 1
        metrics[mime_type]["total_size"] += size
    except Exception as e:
        logger.error(f"Error processing object {object['Key']}: {str(e)}")


metrics = defaultdict(lambda: {"count": 0, "total_size": 0})

# Fetch all objects from the S3 bucket
all_objects = []
paginator = storage.s3.get_paginator("list_objects_v2")
start_time = time.time()

logger.info("Fetching all objects from S3 bucket...")

try:
    for index, page in enumerate(
        paginator.paginate(
            Bucket=settings.S3_BUCKET_NAME, Prefix=settings.S3_FOLDER_NAME
        )
    ):
        try:
            page_content = page["Contents"]
            object_count = len(page_content)

            logger.info(
                f"Fetched {object_count} {'more ' if index > 0 else ''}objects... ({index + 1}/{'?' if object_count == 1000 else index + 1})"
            )
            all_objects.extend(page["Contents"])
        except Exception as e:
            logger.error(f"Error fetching objects: {str(e)}")
except Exception as e:
    logger.error(f"Error listing objects: {str(e)}")
    exit(1)

logger.info(f"Got {len(all_objects)} objects to process. Calculating metrics now")

# Process the objects
last_time = time.time()
for object in all_objects:
    process_object(object, metrics)
end_time = time.time()

# Calculate time metrics
total_time = end_time - start_time
average_time = total_time / len(all_objects) if len(all_objects) > 0 else 0

# Storing the metrics
metrics["last_execution_time_in_milliseconds"] = int(total_time * 1000)
metrics["last_execution_date"] = int(time.time())

logger.info(
    f"Metrics rebuilt in {total_time:.2f}s (average of {average_time:.4f}s per object)"
)
logger.info(f"Saving file to {settings.METRICS_FILE_PATH}")

# Saving the metrics to a file
# if the file doesn't exist, create it
try:
    os.makedirs(os.path.dirname(settings.METRICS_FILE_PATH), exist_ok=True)
    with open(settings.METRICS_FILE_PATH, "w") as f:
        json.dump(metrics, f)
    logger.info("Metrics saved!")
except Exception as e:
    logger.error(f"Error saving metrics: {str(e)}")

logger.info("Goodbye!")
