# Third-party imports
from loguru import logger
from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    Path
)
from prometheus_fastapi_instrumentator import Instrumentator

# Local imports
from settings.config import (
    API_NAME,
    API_VERSION,
    API_DESCRIPTION
)
from settings.environment_config import EnvironmentConfig
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

model_manager = TranslationModelManager(
    model_mappings=EnvironmentConfig.model_mappings,
    model_storage_mode=EnvironmentConfig.MODEL_STORAGE_MODE,
    overwrite_existing_models=EnvironmentConfig.OVERWRITE_EXISTING_MODELS
)
model_manager.load_api_models(
    s3_bucket_name=EnvironmentConfig.S3_BUCKET_NAME,
    model_limit=EnvironmentConfig.API_STARTUP_MODEL_LOADING_LIMIT,
)

# ---------------------------------------------------------------------
# Define endpoints

# initialize API
app = FastAPI(
    title=API_NAME,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Configure Prometheus metrics
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


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
        examples=True
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


@app.post("/predict/{translation_pair}", response_model=PredictResponse)
def predict(
    translation_pair: str = Path(
        ...,
        description="Translation pair in format 'source-target' (e.g., 'en-es', 'fr-de')"
    ),
    request: PredictRequest = None
):
    '''
    Translation endpoint for a specific translation pair.
    Handles both single and batch predictions for the specified translation pair.

    The translation pair is specified in the URL path (e.g., /predict/en-es).
    Send a single item in the array for individual translation,
    or multiple items for batch processing.
    '''
    # Validate translation pair against available models
    if translation_pair not in model_manager.model_mappings:
        available_pairs = list(model_manager.model_mappings.keys())
        raise HTTPException(
            status_code=422,
            detail=(
                f"Translation pair '{translation_pair}' is not supported."
                f"Available pairs: {available_pairs}")
        )

    results = []

    for index, item in enumerate(request.items):
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
                f"with translation pair '{translation_pair}' and request data {item.model_dump()} "
                f"and exception: {str(e)}"
            )

    # Return 500 error if no translations were successful
    if not results:
        raise HTTPException(
            status_code=500,
            detail="All translation attempts failed."
        )
    return {"results": results}
