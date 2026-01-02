from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


# ------------------------------------------------------------------------------------------
# Root (/) endpoint

class RootResponse(BaseModel):
    '''
    Schema for the root endpoint response.
    '''
    name: str = Field(..., description="Name of the API")
    version: str = Field(..., description="Version of the API")
    description: str = Field(..., description="Description of the API")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "name": "Translation API",
                "version": "0.0.1",
                "description": "API for text translation using pre-trained Transformer models."
            }
        }


# ------------------------------------------------------------------------------------------
# Health (/health) endpoint

class HealthResponse(BaseModel):
    '''
    Schema for the health check endpoint response.
    '''
    status: str = Field(..., description="Health status of the API")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "status": "ok"
            }
        }

# ------------------------------------------------------------------------------------------
# Models (/models) endpoint


class ModelInfo(BaseModel):
    '''
    Schema for individual model information.
    '''
    model_name: str = Field(..., description="Name of the Hugging Face model")
    file_type: str = Field(..., description="Model file storage format")
    config: Optional[Dict[str, Any]] = Field(None, description="Detailed model configuration")


class ModelsResponse(BaseModel):
    '''
    Schema for the /models endpoint response.
    '''
    models: Dict[str, ModelInfo] = Field(
        ...,
        description="Dictionary of available models metadata by translation pair"
    )

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "models": {
                    "en-es": {
                        "model_name": "Helsinki-NLP/opus-mt-en-es",
                        "file_type": "ONNX",
                        "config": {
                            "vocab_size": 65000,
                            "max_position_embeddings": 512,
                            "num_layers": 6
                        }
                    },
                    "en-fr": {
                        "model_name": "Helsinki-NLP/opus-mt-en-fr",
                        "file_type": "ONNX",
                        "config": {
                            "vocab_size": 64000,
                            "max_position_embeddings": 512,
                            "num_layers": 6
                        }
                    }
                }
            }
        }

# ------------------------------------------------------------------------------------------
# Prediction (/predict) endpoint


class PredictData(BaseModel):
    '''
    Schema for input data to the model in prediction requests.
    Note: Translation pair (source-target) is now specified in the endpoint path.

    Hints:
        ge: greater than or equal to
        le: less than or equal to
    '''
    text: str = Field(..., description="Text to be translated.")
    max_length: Optional[int] = Field(
        512,
        description="Maximum length of generated translation in tokens.",
        ge=1,
        le=1024
    )
    num_beams: Optional[int] = Field(
        4,
        description="Number of beams for beam search.",
        ge=1,
        le=10
    )
    early_stopping: Optional[bool] = Field(
        True,
        description="Whether to stop generation when all beams finish."
    )

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "text": "Hello, how are you?",
                "max_length": 512,
                "num_beams": 4,
                "early_stopping": True
            }
        }


class PredictRequest(BaseModel):
    '''
    Schema for prediction requests - handles both single and batch predictions.
    All items in the batch will use the same translation pair specified in the endpoint path.
    '''
    items: List[PredictData] = Field(
        ...,
        description="List of translation requests for the same translation pair.",
        min_length=1,
        max_length=100
    )

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "text": "Hello, how are you?",
                        "max_length": 512,
                        "num_beams": 4,
                        "early_stopping": True
                    },
                    {
                        "text": "Good morning, everyone!",
                        "max_length": 256,
                        "num_beams": 3,
                        "early_stopping": True
                    }
                ]
            }
        }


class SinglePredictResponse(BaseModel):
    '''
    Schema for single prediction response.
    Returns the position of the translation in the original request
    in case of batch predictions, which may have failed for some items.
    '''
    position: int = Field(
        ...,
        description="Position of the input item in the request"
    )
    result: str = Field(
        ...,
        description="Translated text corresponding to the input"
    )

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "position": 0,
                "result": "Hola, ¿cómo estás?"
            }
        }


class PredictResponse(BaseModel):
    '''
    Schema for prediction responses.
    All results correspond to the same translation pair specified in the endpoint path.
    '''
    results: List[SinglePredictResponse] = Field(
        ...,
        description="List of translation results for each successful input item"
    )

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "position": 0,
                        "result": "Hola, ¿cómo estás?"
                    },
                    {
                        "position": 1,
                        "result": "¡Buenos días a todos!"
                    }
                ]
            }
        }
