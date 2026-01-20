# ➿ `imgpush` Changelog

This document contains the list of versions of imgpush and their respective changes.

## 0.2.0

### ➕ Added

- S3 Support
- Local stack to work with metrics, with 4 imgpush instances, Prometheus, Prometheus Alert Manager and Grafana
- Grafana dashboards to visualize those metrics
- S3 Metrics Rebuilder whose purpose is to rebuild the metrics from the S3 bucket upon startup
- Fail fast mechanism for invalid configurations
- `/info` endpoint which returns the current version and storage provider

### ✍️ Changed

- Better logging using Python's logging library
- Improved documentation

### 🚨 Breaking changes

1. The fail-fast mechanism will now raise an exception if the configuration is invalid
   This includes missing or invalid values for the following keys:
   | Key | Description |
   | --- | --- |
   | `FILES_DIR` | The directory where the files are stored. Previously defaulted to `files/` |
   | `S3_*` | S3 configuration. It will also check that the authentication tokens are valid, and that the bucket exists and is accessible with the given credentials |

## 0.1.0

### ➕ Added

- Support for storing files other than images
- Metrics per file extension
- Configurable allowed file extensions and resizable image formats

### ✍️ Changed

- Bump Python base Docker image to python:3.12.3-slim
- Small improvements in Dockerfile
- Bump Python modules versions, including Flask (from 1.1.1 to 3.0.3)

### 🚨 Breaking changes

1. The `IMAGES_DIR` environment variable has been renamed to `FILES_DIR` to reflect the new functionality of storing files other than images
