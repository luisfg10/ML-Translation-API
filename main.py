# Third-party imports
import click
import uvicorn
from typing import Optional

# Local imports
from app.main import app
from settings.config import UPLOAD_MODES


# ---------------------------------------------------------------------
# CLI group

@click.group()
def cli():
    pass


@cli.command()
@click.option("--model-name", type=str, required=True)
@click.option(
    "--upload-mode",
    type=click.Choice(UPLOAD_MODES, case_sensitive=False),
    required=True
)
@click.option("--bucket-name", type=str, required=False)
def upload_model(
        model_name: str,
        upload_mode: str,
        bucket_name: Optional[str] = None
) -> None:
    '''
    Uploads/saves a translation model from the Transformers library to a specified location.

    Args:
        model_name: str
            The name of the model to upload.
        upload_mode: str
            The mode of upload, either 's3' for AWS S3 or 'local' for local storage.
            If 's3' is selected, bucket_name must be provided.
            If 'local' is selected, the model will be saved in the local
            'models/downloads' directory.
        bucket_name: Optional[str]
            The name of the S3 bucket to upload the model to.
            Required if upload_mode is 's3'.
    '''


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
