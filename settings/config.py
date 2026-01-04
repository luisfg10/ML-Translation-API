# API info
API_NAME: str = "Translation API"
API_VERSION: str = "v0.0.6"
API_DESCRIPTION: str = '''API for text translation using pre-trained Transformer models.'''

# general settings
AVAILABLE_TRANSLATIONS: list[str] = [
    'en-fr',
    'en-es',
    'en-de',
    'de-en',
    'fr-es',
    'es-en'
]
AVAILABLE_MODEL_STORAGE_MODES: list[str] = ['s3', 'local']

# Default directories
LOCAL_MODEL_DIR: str = "models/downloads"
MODEL_MAPPINGS_FILE: str = "settings/model_mappings.json"
LANGUAGE_MAPPINGS_FILE: str = "settings/language_mappings.json"
