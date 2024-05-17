#!/bin/bash

if [ "$REBUILD_METRICS" = "true" ]; then
    export PYTHONUNBUFFERED=1
    python3 rebuild_metrics.py
    exit 0
fi

nginx
gunicorn --bind unix:imgpush.sock wsgi:app --access-logfile -
