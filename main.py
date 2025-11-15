# Third-party imports
from loguru import logger
import os
import json
import click
import uvicorn
from typing import Optional

# Local code imports
from settings.config import AVAILABLE_MODEL_STORAGE_MODES
from models.aws import AWSServicesManager
from models.management import TranslationModelManager


# ---------------------------------------------------------------------
# CLI group

@click.group()
def cli():
    pass


# ---------------------------------------------------------------------
# AWS-related CLI commands

@cli.command()
@click.option("--bucket-name", type=str, required=True)
def list_aws_s3_bucket_contents(
        bucket_name: str
) -> None:
    '''
    Lists the contents of an AWS S3 bucket.
    Requires AWS credentials to be set in environment variables.
    Useful for ensuring AWS connection is properly set.

    Args:
        bucket_name (str)
            The name of the S3 bucket to list contents from.
    '''
    aws_manager = AWSServicesManager(service='s3')
    response = aws_manager.list_s3_bucket_contents(
        bucket_name=bucket_name,
        simplify_response=True
    )
    logger.debug(f"S3 Bucket '{bucket_name}' contents: \n{response}")


# ---------------------------------------------------------------------
# Model-related CLI commands

@cli.command()
@click.option("--translation-pair", type=str, required=True)
@click.option(
    "--model-storage-mode",
    type=click.Choice(AVAILABLE_MODEL_STORAGE_MODES, case_sensitive=False),
    required=True
)
@click.option("--bucket-name", type=str, required=False)
def upload_model(
    translation_pair: str,
    model_storage_mode: str,
    bucket_name: Optional[str] = None
) -> None:
    '''
    Uploads/saves a translation model from the Transformers library to a specified location.

    Args:
        translation_pair: str
            The translation pair to upload (e.g., 'en-fr', 'en-es').
        model_storage_mode: str
            The mode of upload, either 's3' for AWS S3 or 'local' for local storage.
            If 's3' is selected, bucket_name must be provided.
        bucket_name: Optional[str]
            The name of the S3 bucket to upload the model to.
            Required if model_storage_mode is 's3'.
    '''
    # read settings/model_mappings.py to get model mappings
    with open('settings/model_mappings.json', 'r') as f:
        model_mappings = json.load(f)

    model_manager = TranslationModelManager(
        model_mappings=model_mappings,
        model_storage_mode=model_storage_mode,
    )
    model_manager.upload_model(
        translation_pair=translation_pair,
        bucket_name=bucket_name
    )


@cli.command()
@click.option("--translation-pair", type=str, required=True)
@click.option("--input-text", type=str, required=True)
def test_model_prediction(
        translation_pair: str,
        input_text: str
) -> None:
    '''
    CLI command for individually testing model predictions with
    already-downloaded models. Outputs only the translated text, while
    the API endpoint may return additional metadata.

    Note: This means of generating predictions is significantly slower
    than using the API server, as the model has to be loaded from disk
    every time this command is run (API uses model caching).

    Args:
        translation_pair: str
            The translation pair to test (e.g., 'en-fr', 'en-es').
        input_text: str
            The text to translate.
    '''
    # read settings/model_mappings.py to get model mappings
    with open('settings/model_mappings.json', 'r') as f:
        model_mappings = json.load(f)

    output = TranslationModelManager(
        model_mappings=model_mappings,
        model_storage_mode='local',
    ).predict(
        translation_pair=translation_pair,
        text=input_text
    )

    input_language, output_language = translation_pair.split('-')
    logger.debug(
        "Translation data: \n"
        f"Input in language '{input_language}': {input_text} \n"
        f"Output in language '{output_language}': {output} \n"
        f"Model used: {model_mappings[translation_pair]}"
    )

# ---------------------------------------------------------------------
# API server command


@cli.command()
@click.option(
    "--model-storage-mode",
    type=click.Choice(AVAILABLE_MODEL_STORAGE_MODES, case_sensitive=False),
    required=True
)
@click.option("--bucket-name", type=str, required=False)
@click.option("--host", type=str, required=False)
@click.option("--port", type=int, required=False)
@click.option("--log-level", type=str, required=False)
def run_api_on_server(
        model_storage_mode: str,
        bucket_name: Optional[str] = None,
        host: Optional[str] = "0.0.0.0",
        port: Optional[int] = 8000,
        log_level: Optional[str] = "debug"
) -> None:
    '''
    Runs the FastAPI application using a Uvicorn server.

    Args:
        model_storage_mode: str
            The mode of model storage, either 's3' for AWS S3 or 'local' for local storage.
        bucket_name: Optional[str]
            The name of the S3 bucket to load the model from.
            Required if model_storage_mode is 's3'.
        host: Optional[str]
            The host address to bind the server to.
            Default is "0.0.0.0", which is the required value if running from a Docker
            container to allow external connections.
        port: Optional[int]
            The port number to bind the server to. Default is 8000.
        log_level: Optional[str]
            The logging level for the server. Default is "debug".
            Other options include "info", "warning", "error".
    '''
    # Import inside command for lazy loading
    from app.definition import app

    # export CLI command args to env vars
    if model_storage_mode:
        os.environ['MODEL_STORAGE_MODE'] = model_storage_mode
    if bucket_name:
        os.environ['BUCKET_NAME'] = bucket_name

    # run app
    uvicorn.run(
        app=app,
        host=host,
        port=port,
        log_level=log_level
    )


# ---------------------------------------------------------------------
# CLI entry point

if __name__ == "__main__":
    cli()
