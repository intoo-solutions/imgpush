import datetime
import logging
import time
import concurrent.futures
from storage import get_storage
import settings

metrics = {}
thread_count = 16
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [Metrics] %(message)s')


# Fetching storage provider
storage = get_storage()
if storage.__class__.__name__ == "FileSystemStorage":
    print("Cannot rebuild metrics with FileSystemStorage")
    exit(1)

print("Rebuilding from S3 bucket")
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

print("Fetching all objects from S3 bucket...")

for index, page in enumerate(paginator.paginate(Bucket=settings.S3_BUCKET_NAME)):

    page_content = page["Contents"]
    object_count = len(page_content)

    print(f"Fetched {object_count} {'more ' if index > 0 else ''}objects... ({index + 1}/?)")
    all_objects.extend(page["Contents"])
    
print(f"Got {len(all_objects)} objects to process. Starting {thread_count} threads!")

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

print(f"Metrics rebuilt in {total_time:.2f}s (average of {average_time:.2f}s per object)")
print(f"Saving file metrics.json...")

import json

# Saving the metrics to a file
with open("metrics.json", "w") as f:
    json.dump(metrics, f)

print(f"Metrics saved!")
print(f"Goodbye!")