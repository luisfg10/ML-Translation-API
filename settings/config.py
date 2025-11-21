# API info
API_NAME = "Translation API"
API_VERSION = "v0.0.3"
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

# Default directories
LOCAL_MODEL_DIR = "models/downloads"
MODEL_MAPPINGS_FILE = "settings/model_mappings.json"
LANGUAGE_MAPPINGS_FILE = "settings/language_mappings.json"
