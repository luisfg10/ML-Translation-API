# Third-party imports
import os
import json
from fastapi import FastAPI

# Local imports
from settings.config import (
    API_NAME,
    API_VERSION,
    API_DESCRIPTION
)
from models.management import TranslationModelManager
from app.schemas import PredictData

# load translation models outside of endpoints
model_storage_mode = os.getenv('MODEL_STORAGE_MODE', 'local')
bucket_name = os.getenv('BUCKET_NAME', None)
with open('settings/model_mappings.json', 'r') as f:
    model_mappings = json.load(f)
model_manager = TranslationModelManager(
    model_mappings=model_mappings,
    model_storage_mode=model_storage_mode,
)

# initialize API
app = FastAPI(
    title=API_NAME,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# ---------------------------------------------------------------------
# Define endpoints


@app.get("/")
def root():
    '''
    Root endpoint to return base app info.
    '''
    return {
        "name": API_NAME,
        "version": API_VERSION,
        "description": API_DESCRIPTION
    }


@app.get("/health")
def health():
    '''
    Health check endpoint to return API health status.
    '''
    return {"status": "ok"}


@app.get("/model")
def model():
    '''
    Returns information about the loaded models.
    '''
    pass


@app.post("/predict")
def predict(data: PredictData):
    '''
    Prediction endpoint to return model predictions.
    '''
    pass


@app.post("/batch_predict")
def batch_predict(data: list[PredictData]):
    '''
    Batch predictions endpoint for sending multiple translation requests.
    '''
    pass
