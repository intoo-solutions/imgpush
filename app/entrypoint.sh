#!/bin/bash

# This is to prevent logs from not showing up in the docker logs command
export PYTHONUNBUFFERED=1

echo "Checking validity of the configuration..."
python3 fail_fast.py

if [ "$?" != "0" ]; then
    echo "Configuration is invalid. Exiting..."
    exit 1
fi

echo "Configuration is valid."

if [ "$REBUILD_METRICS" = "1" ]; then
    python3 rebuild_metrics.py
    exit 0
fi

nginx
gunicorn --bind unix:imgpush.sock wsgi:app --access-logfile -
