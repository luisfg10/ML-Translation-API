# ML Translation API

This project uses ML transformers models from the HuggingFace `Tranformers` library and serves them as an API service using `FastAPI`. The models are loaded to and from AWS S3 using the `boto3` library.


## Index
[Overview](#overview)
[Repository Structure](#repository-structure)
[How to run locally](#how-to-run-locally)
[Optional: Deploy in public URL using AWS EC2](#optional-deploy-in-public-url-using-aws-ec2)
[Upcoming features](#upcoming-features)
[Relevant Documentation](#relevant-documentation)

## Overview

## Repository Structure

## How to run locally

## Optional: Deploy in public URL using AWS EC2

## Upcoming features
* Add unit tests using `pytest` to validate any changes to the application.
* Add open-source telemetry collection to keep track of API usage and performance metrics, like response times and error rates. 
* Use `nginx` in addition to a `docker-compose.yml` to scale the API service using several containers.


## Relevant Documentation
* [FastAPI](https://fastapi.tiangolo.com/tutorial/)
* [HuggingFace Hub Translation models](https://huggingface.co/models?pipeline_tag=translation&sort=trending)
* [Flake8](https://flake8.pycqa.org/en/latest/user/configuration.html)
