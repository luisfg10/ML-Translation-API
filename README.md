# ML Translation API

This project uses translation ML models from the HuggingFace `Transformers` library and serves them as an API service using `FastAPI`.  
(still in early development phase)


## Index
* [Repository Structure](#repository-structure)
* [How to run locally](#how-to-run-locally)
* [Optional: Deploy in public URL using AWS EC2](#optional-deploy-in-public-url-using-aws-ec2)
* [Upcoming features](#upcoming-features)
* [Relevant Documentation](#relevant-documentation)

## Repository Structure

## How to run locally

## Optional: Deploy in public URL using AWS EC2

## Upcoming features
* Add the option of loading/downloading models to/from `AWS S3` buckets to have a single source to pull the models from and improve API consistency.  
* Add unit tests using `pytest` to validate application functionality and ensure code quality.  
* Add the option of producing confidence lightweight scores for the `predict/` endpoint of the API so users can assess the reliability of the translations without bloating image size with packages like `torch`.
* Add open-source telemetry collection to keep track of API usage and performance metrics, like response times and error rates. 
* Add a module for model fine-tuning with custom datasets to allow users to adapt translation models to specific domains or languages, simulating a real-world scenario.  
* Use `nginx` in addition to a `docker-compose.yml` to scale the API service using several containers.


## Relevant Documentation
* [FastAPI](https://fastapi.tiangolo.com/tutorial/)
* [HuggingFace Hub Translation models](https://huggingface.co/models?pipeline_tag=translation&sort=trending)
* [ONNX](https://onnx.ai/)
* [Flake8](https://flake8.pycqa.org/en/latest/user/configuration.html)
