# ML Translation API

This project uses translation ML models from the HuggingFace `Transformers` library and serves them as a lightweight API service using `FastAPI` as the web framework on a `uvicorn` server and `optimum.onnxruntime` for model inference optimization. It offers an optional capability to store and retrieve the ML models using `AWS S3`.

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
│   ├── postman_collection.json         
│   └── api_exploration.ipynb
├── models/                     # Model management and utilities
│   ├── management.py 
│   ├── aws.py           
│   └── downloads/              # Downloaded translation models
│       ├── en-es/              
│       ├── en-fr/              
│       └── ...                 
├── settings/                   # Configuration and settings
│   ├── config.py  
│   ├── environment_config.py        
│   ├── .env.template              
│   ├── language_mappings.json  
│   └── model_mappings.json     
├── tests/                      # Test suite
│   └── app/                    # Tests for application modules
│       ├── test_basic_endpoints.py
│       └── test_predict_endpoint.py
│   
├── main.py                     # Definition of the main executables + adequation into CLI commands
├── requirements.txt            
├── Dockerfile                  # Production Dockerfile
├── Dockerfile-dev              # Development Dockerfile
├── .dockerignore               # Files and directories to ignore in Docker builds
├── .gitignore
├── CHANGELOG.md                # Document significant changes across project versions
├── Makefile                    # Build and development commands
└── README.md               
```
### `settings/` directory
This directory contains the required configuration files for running the application.
* `config.py`: Contains the main configuration settings for the API, including the available translation pairs, the available means of uploading/downloading models, the directory within the project where the models are stored, etc.
* `environment_config.py`: Manages the loading of environment variables detaling more specific API/model behavior from a `.env` file, which is also expected to be in the **settings/** directory. See the `.env.template` file for reference on how to create your own `.env` file.
* `language_mappings.json`: A JSON file that maps language codes to their full names (e.g., "en" to "English").
* `model_mappings.json`: A JSON file that maps translation pairs to their corresponding HuggingFace model names.

### `Makefile` and `main.py`
The `Makefile` contains several CLI targets to facilitate development and testing of the application, as well as the main command to run the API on a `uvicorn` server. These commands come from the `main.py` file, and are explained there in more detail.

### `exp/` directory
This directory contains useful material for understanding and exploring the API's capabilities and behavior, including a Jupyter notebook and a Postman collection with examples. Both resources are complementary to better understand how to interact with the API.

### `tests/` directory
This directory contains the test suite for the application, organized into subdirectories for testing different parts of the project:
* `app/`: Contains tests for the application modules, including tests for basic API endpoints and the prediction endpoint.
* `models/`: Contains tests related to model management and functionality.
The tests can be run automatically using the `make run_pytest` command from the `Makefile` on the CLI.

## Environment variables and API configuration
Below is an explanation of the environment variables used in this project:

### Testing Variables
* `TEST_TRANSLATION_PAIR`: Specifies the default language pair used for testing translations (e.g., "en-fr" for English to French).
* `TEST_TEXT`: The default text used for testing the translation functionality (e.g., "Hello, world!").
* `TEST_FILE_DOWNLOAD_PATH`: The file path for running AWS S3 upload/download tests.

### Model Variables
* `MODEL_STORAGE_MODE`: Determines where the models are stored/uploaded. It can be set to either **local** (models are stored locally in the project directory) or **s3** (models are stored in an AWS S3 bucket).
* `S3_BUCKET_NAME`: The name of the AWS S3 bucket used for storing models when `MODEL_STORAGE_MODE` is set to **s3**.

### API Variables
* `API_HOST`: The host address for the API server (default is **0.0.0.0**).
* `API_PORT`: The port number on which the API server listens (default is **8000**).
* `API_LOG_LEVEL`: The logging level for the API server (e.g., **debug**, **info**, **warning**, **error**).

### Credentials/Secrets
The credentials required for accessing AWS S3 services. These should be set as environment variables and not hardcoded in the codebase for security reasons.
* `AWS_ACCESS_KEY_ID`: The AWS access key ID for accessing S3 services.
* `AWS_SECRET_ACCESS_KEY`: The AWS secret access key for accessing S3 services.
* `AWS_REGION`: The AWS region where the S3 bucket is located.

**Note**: The AWS S3 is an optional, non-essential feature of the project. The API will still work fine if using local model storage.

## How to run locally  
It's advised to run the project in a Docker container for ease of deployment and consistency across different environments. Alternatively, it can be run using other options like virtual environments, but this is not covered in this README.

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
4. Create a `.env` file in the `settings/` directory based on the provided `.env.template` file. Fill in the necessary environment variables depending on your use case. From the terminal, this may be done with the commands:

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
    
    # Test model predictions and other commands
    make test_model_prediction
    ```

## Upcoming features
* Add the option of producing confidence lightweight scores for the `predict/` endpoint of the API so users can assess the reliability of the translations without bloating image size with packages like `torch`.
* Add open-source telemetry collection to keep track of API usage and performance metrics, like response times and error rates. 
* Add a module for model fine-tuning with custom datasets to allow users to adapt translation models to specific domains or languages, simulating a real-world scenario.  
* Use `nginx` in addition to a `docker-compose.yml` to scale and manage the API service using several containers.
* Integrate CI/CD pipelines using GitHub Actions to automate running the `pytest` tests whenever a pull request is created.
* Automate the process of deploying the Docker container to cloud services like AWS EC2 in order to expose the API to public consumption using `boto3`.


## Relevant Documentation
* [FastAPI](https://fastapi.tiangolo.com/tutorial/)
* [Uvicorn](https://uvicorn.dev/)
* [HuggingFace Hub Translation models](https://huggingface.co/models?pipeline_tag=translation&sort=trending)
* [ONNX](https://onnx.ai/)
* [Optimum ONNX Runtime](https://huggingface.co/docs/optimum/v1.2.1/en/onnxruntime/modeling_ort)
* [Boto3 (AWS SDK for Python)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
* [Pytest](https://docs.pytest.org/en/stable/)
* [Flake8](https://flake8.pycqa.org/en/latest/user/configuration.html)
* [Postman Docs](https://learning.postman.com/docs/introduction/overview/)
