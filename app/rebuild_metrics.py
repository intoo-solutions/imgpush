import logging
import time
import concurrent.futures
from storage import get_storage
import settings

metrics = {}
thread_count = 16
logging.basicConfig(level=logging.INFO)

def process_object(object):
    filename = object["Key"]
    size = object["Size"]

    object_info = storage.s3.head_object(Key=filename, Bucket=settings.S3_BUCKET_NAME)

    mime_type = object_info.get("ContentType", "others")

    # Update the metrics
    metrics[mime_type] = metrics.get(mime_type, {"count": 0, "total_size": 0})
    metrics[mime_type]["count"] += 1
    metrics[mime_type]["total_size"] += size
    logging.info(f"Processed object {object['Key']}")

storage = get_storage()
if storage.__class__.__name__ == "FileSystemStorage":
    print("Cannot rebuild metrics with FileSystemStorage")
    exit(1)

print("[Metrics] Rebuilding from S3 bucket")

print(storage)

paginator = storage.s3.get_paginator('list_objects')

objects = []

start_time = time.time()

# Create a ThreadPoolExecutor
with concurrent.futures.ThreadPoolExecutor(thread_count) as executor:
    # Iterate over each page of objects
    for page in paginator.paginate(Bucket=settings.S3_BUCKET_NAME):
        page_objects = page["Contents"]
        objects.extend(page_objects)

        # Use the executor to map the process_object function to the objects
        executor.map(process_object, page_objects)

end_time = time.time()
total_time = end_time - start_time
average_time = total_time / len(objects) if objects else 0

print(f"Rebuilt metrics from {len(objects)} objects in S3 bucket {settings.S3_BUCKET_NAME}")
print(f"It took {total_time:.2f}s to rebuild the metrics (average of {average_time:.2f}s per object)")

import json

with open("metrics.json", "w") as f:
    json.dump(metrics, f)