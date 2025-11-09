import uvicorn
from fastapi import FastAPI
from settings.config import (
    API_NAME,
    API_VERSION,
    API_DESCRIPTION
)
from app.schemas import PredictData

# load model outside of endpoints

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
    Returns information about the loaded model.
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
