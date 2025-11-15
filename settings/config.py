# API info
API_NAME = "Translation API"
API_VERSION = "v0.0.1"
API_DESCRIPTION = '''API for text translation using pre-trained Transformer models.'''

# general settings
AVAILABLE_TRANSLATIONS = [
    'en-fr',
    'en-es',
    'en-de',
    'de-en',
    'fr-es',
    'es-en'
]
AVAILABLE_MODEL_STORAGE_MODES = ['s3', 'local']
LOCAL_MODEL_DIR = "models/downloads"
STARTUP_MODEL_LOADING_LIMIT = 2
OVERWRITE_EXISTING_MODELS = False
