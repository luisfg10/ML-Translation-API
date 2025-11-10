# Third-party imports
import json
import click
import uvicorn
from typing import Optional

# Local code imports
from models.management import TranslationModelManager
from app.definition import app
from settings.config import MODEL_STORAGE_MODES


# ---------------------------------------------------------------------
# CLI group

@click.group()
def cli():
    pass


@cli.command()
@click.option("--translation-pair", type=str, required=True)
@click.option(
    "--model-storage-mode",
    type=click.Choice(MODEL_STORAGE_MODES, case_sensitive=False),
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


def run_api_on_server():
    '''
    Runs the FastAPI application using a Uvicorn server.
    '''
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
