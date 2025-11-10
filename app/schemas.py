from pydantic import BaseModel


class PredictData(BaseModel):
    '''
    Schema for input data to the model in prediction requests.
    Attributes:
    ------------
        source: str
            Source language code (e.g., 'en' for English).
        target: str
            Target language code (e.g., 'es' for Spanish).
        text: str
            Text to be translated.
        max_response_length: int | None
            Optional maximum length for the translated text.
            If the text exceeds this length, it will be truncated.
    '''
    source: str
    target: str
    text: str
    max_response_length: int | None = None

    # example of request
    class Config:
        json_schema_extra = {
            "example": {
                "source": "en",
                "target": "es",
                "text": "Hello, how are you?",
                "max_response_length": 50
            }
        }
