# Third-party imports
from loguru import logger
import click
import uvicorn
from typing import Optional
from pathlib import Path

# Local code imports
from settings.config import (
    AVAILABLE_MODEL_STORAGE_MODES,
    LOCAL_MODEL_DIR
)
from settings.environment_config import EnvironmentConfig
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
@click.option(
    "--s3-bucket-name",
    type=str,
    default=EnvironmentConfig.S3_BUCKET_NAME
)
def list_aws_s3_bucket_contents(
        s3_bucket_name: str
) -> None:
    '''
    Lists the contents of an AWS S3 bucket.
    Requires AWS credentials to be set in environment variables.
    Useful for ensuring AWS connection is properly set.

    Args:
        s3_bucket_name (str)
            The name of the S3 bucket to list contents from.
    '''
    aws_manager = AWSServicesManager(service='s3')
    aws_manager.list_s3_bucket_contents(
        s3_bucket_name=s3_bucket_name,
        simplify_response=True,
        verbose=True
    )


@cli.command()
@click.option(
    "--s3-bucket-name",
    type=str,
    default=EnvironmentConfig.S3_BUCKET_NAME
)
def test_aws_s3_file_upload(
        s3_bucket_name: str
) -> None:
    '''
    Uploads a .txt with the text "Hello, World!" to the specified S3 bucket.

    Args:
        s3_bucket_name (str)
            The name of the S3 bucket to upload the file to.
    '''
    aws_manager = AWSServicesManager(service='s3')

    # create test file
    test_filename = "test.txt"
    with open(test_filename, 'w') as f:
        f.write("Hello, World!")

    # upload test file to S3 bucket
    aws_manager.upload_file_to_s3(
        s3_bucket_name=s3_bucket_name,
        local_filepath=test_filename,
        s3_filepath=test_filename,
        verbose=True
    )


@cli.command()
@click.option(
    "--s3-bucket-name",
    type=str,
    default=EnvironmentConfig.S3_BUCKET_NAME
)
@click.option(
    "--s3-filepath",
    type=str,
    default=EnvironmentConfig.TEST_FILE_DOWNLOAD_PATH
)
def test_aws_s3_file_download(
        s3_bucket_name: str,
        s3_filepath: str
) -> None:
    '''
    Downloads a file from the specified S3 bucket.

    Args:
        s3_bucket_name (str)
            The name of the S3 bucket to download the file from.
        s3_filepath (str)
            The S3 file path of the file to download.
        local_filepath (str)
            The local path where the file will be saved.
    '''
    aws_manager = AWSServicesManager(service='s3')
    aws_manager.download_file_from_s3(
        s3_bucket_name=s3_bucket_name,
        s3_filepath=s3_filepath,
        local_filepath=s3_filepath,
        verbose=True
    )


@cli.command()
@click.option(
    "--s3-bucket-name",
    type=str,
    default=EnvironmentConfig.S3_BUCKET_NAME
)
@click.option(
    "--test-translation-pair",
    type=str,
    default=EnvironmentConfig.TEST_TRANSLATION_PAIR
)
def test_aws_s3_directory_download(
        s3_bucket_name: str,
        test_translation_pair: str = EnvironmentConfig.TEST_TRANSLATION_PAIR
) -> None:
    '''
    Downloads all files from a specified S3 directory to a local directory.
    Only provide the translation pair name, as the process assumes the model
    is found in s3 using the same directory structure as in the project.

    Args:
        s3_bucket_name (str)
            The name of the S3 bucket to download the files from.
        s3_directory (str)
            The S3 directory path to download files from.
        local_directory (str)
            The local directory where the files will be saved.
    '''
    aws_manager = AWSServicesManager(service='s3')
    directory_path = Path(LOCAL_MODEL_DIR) / test_translation_pair
    aws_manager.download_directory_from_s3(
        s3_bucket_name=s3_bucket_name,
        s3_prefix=directory_path,
        local_directory=directory_path,
    )


# ---------------------------------------------------------------------
# Model-related CLI commands

@cli.command()
@click.option(
    "--translation-pair",
    type=str,
    default=EnvironmentConfig.TEST_TRANSLATION_PAIR
)
@click.option(
    "--model-storage-mode",
    type=click.Choice(AVAILABLE_MODEL_STORAGE_MODES, case_sensitive=False),
    default=EnvironmentConfig.MODEL_STORAGE_MODE
)
@click.option(
    "--s3-bucket-name",
    type=str,
    default=EnvironmentConfig.S3_BUCKET_NAME
)
@click.option(
    "--overwrite-existing-models",
    is_flag=True,
    default=EnvironmentConfig.OVERWRITE_EXISTING_MODELS
)
def save_model(
    translation_pair: str,
    model_storage_mode: str,
    s3_bucket_name: Optional[str] = None,
    overwrite_existing_models: bool = False
) -> None:
    '''
    Uploads/saves a translation model from the Transformers library to a specified location.

    Args:
        translation_pair: str
            The translation pair to upload (e.g., 'en-fr', 'en-es').
        model_storage_mode: str
            The mode of upload, either 's3' for AWS S3 or 'local' for local storage.
            If 's3' is selected, s3_bucket_name must be provided.
        s3_bucket_name: Optional[str]
            The name of the S3 bucket to upload the model to.
            Required if model_storage_mode is 's3'.
        overwrite_existing_models: bool
            Whether to overwrite existing local model files when doing download
            operations if such files already exist locally. Defaults to False.
    '''
    model_manager = TranslationModelManager(
        model_mappings=EnvironmentConfig.model_mappings,
        model_storage_mode=model_storage_mode,
        overwrite_existing_models=overwrite_existing_models
    )
    model_manager.save_model(
        translation_pair=translation_pair,
        s3_bucket_name=s3_bucket_name
    )


@cli.command()
@click.option(
    "--translation-pair",
    type=str,
    default=EnvironmentConfig.TEST_TRANSLATION_PAIR
)
@click.option(
    "--input-text",
    type=str,
    default=EnvironmentConfig.TEST_TEXT
)
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
    output = TranslationModelManager(
        model_mappings=EnvironmentConfig.model_mappings,
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
        f"Model used: {EnvironmentConfig.model_mappings[translation_pair]}"
    )

# ---------------------------------------------------------------------
# API server command


@cli.command()
@click.option(
    "--host",
    type=str,
    default=EnvironmentConfig.API_HOST
)
@click.option(
    "--port",
    type=int,
    default=EnvironmentConfig.API_PORT
)
@click.option(
    "--log-level",
    type=str,
    default=EnvironmentConfig.API_LOG_LEVEL
)
def run_api_on_server(
        host: Optional[str] = "0.0.0.0",
        port: Optional[int] = 8000,
        log_level: Optional[str] = "debug"
) -> None:
    '''
    Runs the FastAPI application using a Uvicorn server.

    Args received directly:
        host: Optional[str]
            The host address to bind the server to.
            Default is "0.0.0.0", which is the required value if running from a Docker
            container to allow external connections.
        port: Optional[int]
            The port number to bind the server to. Default is 8000.
        log_level: Optional[str]
            The logging level for the server. Default is "debug".
            Other options include "info", "warning", "error".

    Args received via environment variables:
        MODEL_STORAGE_MODE: str
            The mode of model storage, either 's3' for AWS S3 or 'local' for local storage.
        S3_BUCKET_NAME: Optional[str]
            The name of the S3 bucket to load the model from.
            Required if MODEL_STORAGE_MODE is 's3'.
        OVERWRITE_EXISTING_MODELS: bool
            Whether to overwrite existing local model files when doing download
            operations if such files already exist locally. Defaults to False.
    '''
    # Import inside command for lazy loading
    from app.definition import app

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
