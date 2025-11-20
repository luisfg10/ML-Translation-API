# Changelog
All significant changes to the project will be kept in this file.

## v0.0.3
Added unit tests using `pytest` for:  
* all API endpoints under different scenarios  
* major model-related methods   

AWS functionalities ARE NOT covered as this is a secondary feature within the project.  This flow can be run manually from the CLI using `make run_tests`, as well as automatically whenever a pull Request is created via GitHub Actions.  
This functionality is technically non-essential to running the API, so it is left outside of the `requirements.txt` file in the interest of keeping dependencies minimal. To run these tests locally, use either a virtual environment or add them to the project's Docker image.

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
