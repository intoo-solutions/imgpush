#!/bin/bash

# This is to prevent logs from not showing up in the docker logs command
export PYTHONUNBUFFERED=1

python3 fail_fast_if_configuration_is_invalid.py
if [ "$?" != "0" ]; then
    exit 1
fi

if [ "$REBUILD_METRICS" = "1" ]; then
    python3 rebuild_metrics.py
    exit 0
fi

nginx
gunicorn --bind unix:imgpush.sock wsgi:app --access-logfile -
