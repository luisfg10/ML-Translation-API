# Third-party imports
from loguru import logger
import os
import json
from fastapi import FastAPI, Query

# Local imports
from settings.config import (
    API_NAME,
    API_VERSION,
    API_DESCRIPTION
)
from models.management import TranslationModelManager
from app.schemas import (
    RootResponse,
    HealthResponse,
    ModelsResponse,
    PredictRequest,
    PredictResponse,
)

# ---------------------------------------------------------------------
# Model loading (outside endpoints)

model_storage_mode = os.getenv('MODEL_STORAGE_MODE', 'local')
bucket_name = os.getenv('BUCKET_NAME', None)
with open('settings/model_mappings.json', 'r') as f:
    model_mappings = json.load(f)
model_manager = TranslationModelManager(
    model_mappings=model_mappings,
    model_storage_mode=model_storage_mode,
)
model_manager.load_api_models(bucket_name=bucket_name)

# ---------------------------------------------------------------------
# Define endpoints

# initialize API
app = FastAPI(
    title=API_NAME,
    description=API_DESCRIPTION,
    version=API_VERSION
)


@app.get("/", response_model=RootResponse)
def root():
    '''
    Root endpoint to return base app info.
    '''
    return {
        "name": API_NAME,
        "version": API_VERSION,
        "description": API_DESCRIPTION
    }


@app.get("/health", response_model=HealthResponse)
def health():
    '''
    Health check endpoint to return API health status.
    '''
    return {"status": "ok"}


@app.get("/models", response_model=ModelsResponse)
def models(
    return_model_config: bool = Query(
        default=False,
        description="Include detailed model configuration metadata in the response.",
        example=True
    )
):
    '''
    Returns information about the loaded models.
    Includes an optional query parameter to return detailed model configuration.
    '''
    model_metadata = model_manager.get_models_info(
        return_model_config=return_model_config
    )
    return {"models": model_metadata}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    '''
    Translation endpoint - handles both single and batch predictions.

    Send a single item in the array for individual translation,
    or multiple items for batch processing.
    '''
    results = []

    for index, item in enumerate(request.items):
        # Construct translation pair from source and target
        translation_pair = f"{item.source}-{item.target}"

        # Get translation from model manager
        try:
            translated_text = model_manager.predict(
                translation_pair=translation_pair,
                text=item.text,
                max_length=item.max_length,
                num_beams=item.num_beams,
                early_stopping=item.early_stopping,
                raise_on_missing_model=False
            )
            results.append({
                "position": index,
                "result": translated_text
            })
        except Exception as e:
            logger.error(
                f"Translation failed for item at position {index} "
                f"with request data {item.model_dump()} "
                f"and exception: {str(e)}"
            )
    return {"results": results}
