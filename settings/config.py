# API info
API_NAME = "Translation API"
API_VERSION = "v0.0.1"
API_DESCRIPTION = '''API for text translation using pre-trained Transformer models.'''

# app behavior settings
AVAILABLE_TRANSLATIONS = ['en-fr', 'en-es']
MODEL_STORAGE_MODES = ['s3', 'local']
LOCAL_MODEL_DIR = "./models/downloads/"
