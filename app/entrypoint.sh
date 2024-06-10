#!/bin/bash

# This is to prevent logs from not showing up in the docker logs command
export PYTHONUNBUFFERED=1

if [ "$REBUILD_METRICS" = "1" ]; then
    python3 rebuild_metrics.py
    exit 0
fi

nginx
gunicorn --bind unix:imgpush.sock wsgi:app --access-logfile -
