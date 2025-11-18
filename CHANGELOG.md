# Changelog
All significant changes to the project will be kept in this file.

## v0.0.2
Added AWS S3 model upload/download functionality. Now models can be fetched from and stored in an S3 bucket, which better imitates a real-world deploymnt scenario which needs a centralized, reliable storage solution.

## v0.0.1
Initial version of the project, including:
* `/` (root) endpoint
* `health/` endpoint
* `model/` endpoint
* `predict/` endpoint

Also includes:
* Support for 8 different translation pairs
* Production Dockerfile
* Development Dockerfile and deployment instructions
* Customizable API behavior from `config.py`
* API exploration files
* Local model uploading
