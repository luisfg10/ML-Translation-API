# ML Translation API

This repository uses `HuggingFace` translation models and serves them via a RESTful API using `FastAPI` on a `uvicorn` server. It uses `ONNX Runtime` for efficient and lightweight model inference, provides optional model fetching and storage with `AWS`, extensive but not comprehensive app functionality tests using `pytest`, containerization with `Docker` for both development and production setups, and app scaling, load balancing, monitoring and orchestration using `Docker Compose`, `nginx`, `Prometheus` and `Grafana`.

## Table of Contents
- [1. Project Structure](#1-project-structure)
- [2. Environment Configuration](#2-environment-configuration)
- [3. Development Setup](#3-development-setup)
- [4. Production Setup](#4-production-setup)
- [5. Application Endpoints](#5-application-endpoints)
- [6. Project Limitations and Future Work](#6-project-limitations-and-future-work)
- [7. Relevant Documentation](#7-relevant-documentation)

## 1. Project Structure

Below is an overview of the structure of the repository:

```
ML-Translation-API/
├── .github/                    # GitHub-specific configurations like copilot settings
├── app/                        # Application core modules
│   ├── definition.py
│   ├── metrics.py            
│   └── schemas.py           
├── examples/                   # notebooks showing API usage and logic
│   ├── postman_collection.json         
│   └── api_exploration.ipynb
│
├── models/                     # Model management and utilities
│   ├── management.py 
│   ├── aws.py           
│   └── downloads/              # Downloaded translation models
│       ├── en-es/              
│       ├── en-fr/              
│       └── ...      
│
├── grafana/                    # Grafana configurations
├── prometheus/                 # Prometheus configurations
├── settings/                   # Project configuration and settings (including nginx)
├── tests/                      # Testing with pytest
│   
├── main.py                     # Definition of the main executables + adequation into CLI commands
├── Makefile                    # Build and development commands
├── requirements.txt            # API Python dependencies, excluding testing
├── requirements-test.txt       # Testing dependencies
├── Dockerfile                  # API Production Dockerfile
├── Dockerfile.dev              # API Development Dockerfile
├── docker-compose.yml          # Full service orchestration instructions (API, nginx, etc.)
├── .dockerignore               # Files and directories to ignore in Docker builds
├── .gitignore
├── CHANGELOG.md                # Document significant changes across project versions
└── README.md               
```

## 2. Environment Configuration  
The API's behavior can be configured from the values inside the `settings/` directory. These settings are called inside `main.py` to execute the project's different functionalities.  
* `.env.template`: Template for environment variables. Copy this file to `.env` and modify the values as needed.
* `config.py`: Contains basic application configurations such as API name and version, allowed translation pairs, and the default directories for model storage and mapping.
* `environment_config.py`: Contains a utility class for loading and managing environment variables.
* `model_mappings.json`: JSON file that maps translation pairs to their respective HuggingFace models.
* `nginx.conf`: Configuration file for the `nginx` server used as a reverse proxy and load balancer for the API, when deployed with Docker Compose.

## 3. Development Setup  
This project can be set up for local development using Docker or with a local Python environment. For Docker-based development, follow these steps:

1. Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine.  
2. Clone this repository to your local machine using:
   ```bash
   git clone https://github.com/luisfg10/ML-Translation-API.git
    ```
3. Navigate to the project directory:
   ```bash
   cd ML-Translation-API
   ```
4. Create a `.env` file in the `settings/` directory based on the instructions provided in section 2.
5. Build a development Docker image:
    ```bash
    docker build -f Dockerfile.dev -t ml-translation-api:dev .
    ```
Command breakdown:
- `-f Dockerfile.dev`: Specifies to Docker o use the `Dockerfile.dev` file for building the image instead of the default `Dockerfile`. 

6. Run the container in development mode with volume mounting and interactive shell:
    ```bash
    docker run --rm -v "${PWD}":/app -p 8000:8000 -it ml-translation-api:dev
    ```

Command breakdown:
- `docker run`: Creates and starts a new container
- `--rm`: Automatically removes the container when it exits (keeps system clean)
- `-v "${PWD}":/app`: Mounts the current directory (`${PWD}`) to the container's `/app` directory
  - `"${PWD}"`: Your current working directory (the project root)
  - `:/app`: Maps to the container's working directory
  - This allows you to edit files locally and see changes immediately inside the container
- `-p 8000:8000`: Maps port 8000 from container to your local machine
  - `8000` (left): Port on your local machine
  - `8000` (right): Port inside the container
- `-it`: Combines two flags:
  - `-i`: Keeps STDIN open (interactive mode)
  - `-t`: Allocates a pseudo-TTY (terminal)
- `ml-translation-api:dev`: The image name and tag to run

7. Inside the container, you can now run the commands from the `Makefile` individually:
    ```bash
    # Run the API server manually
    make run_api_on_server
    
    # Test model predictions and other commands
    make test_model_prediction
    ```

**Note**: This mode is meant for testing the API server's different functionalities or as a whole, and does not include the full orchestration with `nginx`, `Prometheus`, and `Grafana`.

## 4. Production Setup  
The production version of the project goes straight to running the API server automatically as a command when the container starts, as specified in the `Dockerfile`. It also includes the full orchestration with `nginx`, `Prometheus`, and `Grafana` using `docker-compose`. To set up the production environment, make sure you have Docker Desktop installed and run:

```bash
docker compose up -d
```
This command will build and start all the services defined in the `docker-compose.yml` file in detached mode (`-d`), allowing you to run the services in the background.  
After this, the API will be accessible at `http://localhost/` (port 80).

## 5. Application Endpoints  
`FastAPI` automatically generates interactive API documentation that can be accessed once the server is running. You can access the documentation at:
- Swagger UI: `http://localhost/docs`
- ReDoc: `http://localhost/redoc`

If running the entire cluster with `docker-compose`, the following endpoints will also be available:
* Prometheus UI: `http://localhost:9090`
* Grafana UI: `http://localhost:3000`. Grafana has been set up in this project to not require a login for simplicity, although in a real production setting this should be changed for security purposes. It also has a pre-configured connection to the Prometheus data source and a dashboard to visualize basic API metrics.

## 6. Project Limitations and Future Work  
There are many ways this project can be improved and extended. Here are some ideas for future work:
* Improve monitoring capabilities and traceability by generating and collecting logs, traces and spans using open-source telemetry tools like `OpenTelemetry`.  
* Currently, Prometheus is set up to only scrape the FastAPI application, not `nginx`. Add `nginx` metrics exporting using the `nginx-prometheus-exporter` to monitor request rates, error rates, and response times at the proxy level, which is useful when the main app is down or not finished loading.  
* Currently, the monitoring capabilities are very basic and all engineering-focused. It would be useful to monitor for machine learning-specific metrics like translation quality (e.g., BLEU scores) over time to detect model drift or degradation in performance, although this would require some thought, as for each translation request there's no ground truth to compare against.
* Add a module for model fine-tuning with custom datasets to allow users to adapt translation models to specific domains or languages, simulating a real-world scenario.  
* Integrate CI/CD pipelines using GitHub Actions to automate running the `pytest` tests and attempting to build the project's `Docker image` whenever a pull request is created.
* Add an optional frontend interface for user-friendly interaction with the API.
* Make the project deployable on cloud platforms like AWS, GCP, or Azure and not just locally with Docker.

## 7. Relevant Documentation
* [FastAPI](https://fastapi.tiangolo.com/tutorial/)
* [Uvicorn](https://uvicorn.dev/)
* [HuggingFace Hub Translation models](https://huggingface.co/models?pipeline_tag=translation&sort=trending)
* [ONNX](https://onnx.ai/)
* [Optimum ONNX Runtime](https://huggingface.co/docs/optimum/v1.2.1/en/onnxruntime/modeling_ort)
* [Boto3 (AWS SDK for Python)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
* [Pytest](https://docs.pytest.org/en/stable/)
* [Flake8](https://flake8.pycqa.org/en/latest/user/configuration.html)
* [nginx Beginner's Guide](https://nginx.org/en/docs/beginners_guide.html)
* [Grafana Docs](https://grafana.com/docs/)
* [Prometheus Docs](https://prometheus.io/docs/introduction/overview/)