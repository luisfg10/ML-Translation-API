# ML Translation API

This project uses translation ML models from the HuggingFace `Transformers` library and serves them as a lightweight API service using `FastAPI` as the web framework on a `uvicorn` server and `optimum.onnxruntime` for model inference optimization. 

For comparison, this project is able to run the API on a ~5GB Docker container, while projects using frameworks like `torch` can take ~15GB of space due to the heavy dependedencies required. This makes it suitable for deployment in resource-constrained environments.

## Index
* [Repository Structure](#repository-structure)
* [Environment variables and API configuration](#environment-variables-and-api-configuration)
* [How to run locally](#how-to-run-locally)
* [Upcoming features](#upcoming-features)
* [Relevant Documentation](#relevant-documentation)

## Repository Structure

Here is an overview of the structure of the repository:

```
ML-Translation-API/
├── app/                        # Application core modules
│   ├── definition.py            
│   └── schemas.py           
├── exp/                        # API exploration
│   └── api_exploration.ipynb
├── models/                     # Model management and utilities
│   ├── management.py           
│   └── downloads/              # Downloaded translation models
│       ├── en-es/              
│       ├── en-fr/              
│       └── ...                 
├── settings/                   # Configuration and settings
│   ├── config.py               
│   ├── language_mappings.json  
│   └── model_mappings.json     
├── main.py                     # Definition of the main executables + adequation into CLI commands
├── requirements.txt            
├── Dockerfile                  # Production Dockerfile
├── Dockerfile-dev              # Development Dockerfile
├── .dockerignore               # Files and directories to ignore in Docker builds
├── Makefile                    # Build and development commands
└── README.md               
```
### `settings/` directory
This directory contains the required configuration files for the application.
* `config.py`: Contains the main configuration settings for the API, including the available translation pairs, the available means of uploading/downloading models, and the directory within the project where the models are stored.
* `language_mappings.json`: A JSON file that maps language codes to their full names (e.g., "en" to "English").
* `model_mappings.json`: A JSON file that maps translation pairs to their corresponding HuggingFace model names.

### `Makefile` and `main.py`
The `Makefile` contains several CLI targets to facilitate development and testing of the application. These commands come from the `main.py` file, and are also explained there.

## Environment variables and API configuration

## How to run locally  
The application is meant to be run in a Docker container for ease of deployment and consistency across different environments. 

### First Steps

1. Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine.  
2. Clone this repository to your local machine using:
   ```bash
   git clone https://github.com/luisfg10/ML-Translation-API.git
    ```
3. Navigate to the project directory:
   ```bash
   cd ML-Translation-API
   ```

### Production Setup
The production version of the project goes straight to business and runs the API server automatically as a command when the container starts.

1. Build the Docker image from the provided `Dockerfile`:
    ```bash
    docker build -t ml-translation-api .
    ```
2. Run the Docker container, mapping the container's port to your local machine's port:
    ```bash
    docker run -p 8000:8000 ml-translation-api
    ```
    This automatically starts the uvicorn server running the FastAPI application, and maps port `8000` of the container (left) to port `8000` (right) on your local machine.

3. Once the container is running, you can access the API documentation by navigating to `http://localhost:8000/docs` in your web browser. This will open the interactive Swagger UI where you can test the API endpoints. Alternatively, call the endpoints directly using tools like `curl` or Postman.

### Development Setup
On a development setting, it's desirable to modify and test out different parts of the project before running the API server.

1. Build a development Docker image:
    ```bash
    docker build -f Dockerfile-dev -t ml-translation-api:dev .
    ```
**Command breakdown:**
- `-f Dockerfile-dev`: Specifies to Docker o use the `Dockerfile-dev` file for building the image instead of the default `Dockerfile`. 

2. Run the container in development mode with volume mounting and interactive shell:
    ```bash
    docker run --rm -v "${PWD}":/app -p 8000:8000 -it ml-translation-api:dev
    ```

**Command breakdown:**
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

3. Inside the container, you can now run the commands from the `Makefile` individually:
    ```bash
    # Run the API server manually
    make run_api_on_server
    
    # Test model predictions
    make test_model_prediction
    
    # Upload models
    make upload_model
    ```

## Upcoming features
* Add the option of loading/downloading models to/from `AWS S3` buckets to have a single source to pull the models from and improve API consistency.  
* Add unit tests using `pytest` to validate application functionality and ensure code quality.  
* Add the option of producing confidence lightweight scores for the `predict/` endpoint of the API so users can assess the reliability of the translations without bloating image size with packages like `torch`.
* Add open-source telemetry collection to keep track of API usage and performance metrics, like response times and error rates. 
* Add a module for model fine-tuning with custom datasets to allow users to adapt translation models to specific domains or languages, simulating a real-world scenario.  
* Use `nginx` in addition to a `docker-compose.yml` to scale and manage the API service using several containers.


## Relevant Documentation
* [FastAPI](https://fastapi.tiangolo.com/tutorial/)
* [HuggingFace Hub Translation models](https://huggingface.co/models?pipeline_tag=translation&sort=trending)
* [ONNX](https://onnx.ai/)
* [Flake8](https://flake8.pycqa.org/en/latest/user/configuration.html)
