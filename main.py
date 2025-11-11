# Third-party imports
from loguru import logger
import os
import json
import click
import uvicorn
from typing import Optional

# Local code imports
from settings.config import AVAILABLE_MODEL_STORAGE_MODES
from models.management import TranslationModelManager


# ---------------------------------------------------------------------
# CLI group

@click.group()
def cli():
    pass


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
def run_api_on_server(
        model_storage_mode: str,
        bucket_name: Optional[str] = None
):
    '''
    Runs the FastAPI application using a Uvicorn server.

    Args:
        model_storage_mode: str
            The mode of model storage, either 's3' for AWS S3 or 'local' for local storage.
        bucket_name: Optional[str]
            The name of the S3 bucket to load the model from.
            Required if model_storage_mode is 's3'.
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
        host="0.0.0.0",
        port=8000,
        debug=True
    )


# ---------------------------------------------------------------------
# CLI entry point

if __name__ == "__main__":
    cli()
