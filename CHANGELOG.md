# Changelog
All significant changes to the project will be kept in this file.

## v0.0.6
Updated the API to generate performance-related metrics using `prometheus-fastapi-instrumentator` (this creates a new `/metrics` endpoint not meant for direct user interaction), and collect and store them using `Prometheus`. The following metrics are now tracked:
* Request count per endpoint and HTTP method
* Request latency per endpoint
* Request latency times
* CPU and memory usage of the container running the API service  
These metrics can be visualized in a dedicated `dashboard/` endpoint, which is built using `Grafana`.

## v0.0.5  
Refactored the `predict/` endpoint into `predict/{translation_pair}`, meaning each translation pair now has its own dedicated endpoint. This has several desirable properties:
* Simplifies the endpoint request body, not needing to specify source and target languages anymore
* Improves the organization of the API structure, as different translation models are no longer mixed into a single endpoint
* Allows for more detailed logging and monitoring of individual translation pairs, a feature which will be added in future versions

## v0.0.4
Added the option to scale the API service using `nginx` as a reverse proxy and load balancer. This feature is implemented entirely from Docker, using `docker-compose.yml` to orchestrate multiple instances of the API service behind a single `nginx` container. Instructions of use are included in the `README.md` file, section 3.

## v0.0.3
Added unit tests using `pytest` for:  
* all API endpoints under different scenarios  
* major model-related methods   

AWS functionalities ARE NOT covered as this is a secondary feature within the project.  This flow can be run manually from the CLI using `make run_pytest`, and in the future will be added as part of the CI/CD pipeline using GitHub Actions.
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
