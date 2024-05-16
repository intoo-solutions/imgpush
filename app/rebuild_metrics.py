import datetime
import logging
import time
import concurrent.futures
from storage import get_storage
import settings

metrics = {}
thread_count = 16
logging.basicConfig(level=logging.INFO)

# Fetching storage provider
storage = get_storage()
if storage.__class__.__name__ == "FileSystemStorage":
    print("Cannot rebuild metrics with FileSystemStorage")
    exit(1)

print("[Metrics] Rebuilding from S3 bucket")
print(storage)

# The method that will process each object
def process_object(object):
    filename = object["Key"]
    size = object["Size"]

    object_info = storage.s3.head_object(Key=filename, Bucket=settings.S3_BUCKET_NAME)

    mime_type = object_info.get("ContentType", "others")

    # Update the metrics
    metrics[mime_type] = metrics.get(mime_type, {"count": 0, "total_size": 0})
    metrics[mime_type]["count"] += 1
    metrics[mime_type]["total_size"] += size

# Fetch all objects from the S3 bucket
all_objects = []
paginator = storage.s3.get_paginator('list_objects')
start_time = time.time()

for page in paginator.paginate(Bucket=settings.S3_BUCKET_NAME):
    all_objects.extend(page["Contents"])

# Process the objects
last_time = time.time()
with concurrent.futures.ThreadPoolExecutor(thread_count) as executor:
    for i, _ in enumerate(executor.map(process_object, all_objects)):
        now = time.time()
        if now - last_time > 5:
            print(f'Progress: {i}/{len(all_objects)} ({i / len(all_objects) * 100:.2f}%)')
            last_time = now

end_time = time.time()

# Calculate time metrics
total_time = end_time - start_time
average_time = total_time / len(all_objects) if len(all_objects) > 0 else 0

# Storing the metrics
metrics["last_execution_time_in_milliseconds"] = int(total_time * 1000)
metrics["last_execution_date"] = datetime.datetime.now().isoformat()

print(f"Rebuilt metrics from {len(all_objects)} objects in S3 bucket {settings.S3_BUCKET_NAME}")
print(f"It took {total_time:.2f}s to rebuild the metrics (average of {average_time:.2f}s per object)")

import json

# Saving the metrics to a file
with open("metrics.json", "w") as f:
    json.dump(metrics, f)