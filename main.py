# Third-party imports
import click
import uvicorn

# Local imports
from app.main import app


# ---------------------------------------------------------------------
# CLI group

@click.group()
def cli():
    pass


@cli.command()
@click.option("--model-name", type=str, required=True)
def upload_model_to_s3(
        model_name: str
) -> None:
    '''
    Uploads a model to an S3 bucket.

    Args:
        model_name : str
            The name of the model to upload.
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

