import os
import datetime
import logging
import time
import concurrent.futures
from storage import get_storage
import settings
from collections import defaultdict
from threading import Lock

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] [Metrics] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Fetching storage provider
storage = get_storage()
if storage.__class__.__name__ == "FileSystemStorage":
    logger.error("Cannot rebuild metrics with FileSystemStorage")
    exit(1)

logger.info("Rebuilding from S3 bucket")
for line in storage.__str__().split("\n"):
    logger.info(line)

# The method that will process each object
def process_object(object, metrics, lock):
    try:
        filename = object["Key"]
        size = object["Size"]

        # Skip if it's a folder
        if filename.endswith('/'):
            return

        object_info = storage.s3.head_object(Key=filename, Bucket=settings.S3_BUCKET_NAME)

        mime_type = object_info.get("ContentType", "others")

        # Update the metrics
        with lock:
            metrics[mime_type]["count"] += 1
            metrics[mime_type]["total_size"] += size
    except Exception as e:
        logger.error(f"Error processing object {object['Key']}: {str(e)}")

metrics = defaultdict(lambda: {"count": 0, "total_size": 0})
lock = Lock()

# Fetch all objects from the S3 bucket
all_objects = []
paginator = storage.s3.get_paginator('list_objects')
start_time = time.time()

logger.info("Fetching all objects from S3 bucket...")

try:
    for index, page in enumerate(paginator.paginate(Bucket=settings.S3_BUCKET_NAME)):
        try:
            page_content = page["Contents"]
            object_count = len(page_content)

            logger.info(f"Fetched {object_count} {'more ' if index > 0 else ''}objects... ({index + 1}/{'?' if object_count == 1000 else index + 1})")
            all_objects.extend(page["Contents"])
        except Exception as e:
            logger.error(f"Error fetching objects: {str(e)}")
except Exception as e:
    logger.error(f"Error listing objects: {str(e)}")
    exit(1)

try:
    thread_count = int(os.getenv('THREAD_COUNT', 4))
except ValueError:
    logger.error("THREAD_COUNT environment variable is not a valid integer, defaulting to 4")
    thread_count = 4

logger.info(f"Got {len(all_objects)} objects to process. Starting {thread_count} threads!")

# Process the objects
last_time = time.time()
with concurrent.futures.ThreadPoolExecutor(thread_count) as executor:
    for i, _ in enumerate(executor.map(process_object, all_objects, [metrics]*len(all_objects), [lock]*len(all_objects))):
        now = time.time()
        if now - last_time > 5:
            logger.info(f'Progress: {i}/{len(all_objects)} ({i / len(all_objects) * 100:.2f}%)')
            last_time = now

end_time = time.time()

# Calculate time metrics
total_time = end_time - start_time
average_time = total_time / len(all_objects) if len(all_objects) > 0 else 0

# Storing the metrics
metrics["last_execution_time_in_milliseconds"] = int(total_time * 1000)
metrics["last_execution_date"] = datetime.datetime.now().isoformat()

logger.info(f"Metrics rebuilt in {total_time:.2f}s (average of {average_time:.2f}s per object)")
logger.info("Saving file metrics.json...")

import json

# Saving the metrics to a file
try:
    with open("metrics.json", "w") as f:
        json.dump(metrics, f)
    logger.info("Metrics saved!")
except Exception as e:
    logger.error(f"Error saving metrics: {str(e)}")

logger.info("Goodbye!")