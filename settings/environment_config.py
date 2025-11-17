# Third-party imports
import os
import json
from dotenv import load_dotenv

# Local imports
from settings.config import (
    MODEL_MAPPINGS_FILE,
    LANGUAGE_MAPPINGS_FILE
)

# Load .env file from parent directory
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path, override=True)


class EnvironmentConfig:
    '''
    Class for collecting and storing environment configuration variables.
    '''
    # Testing
    TEST_TRANSLATION_PAIR = os.getenv('TEST_TRANSLATION_PAIR', 'en-fr')
    TEST_TEXT = os.getenv('TEST_TEXT', 'Hello, world!')
    TEST_FILE_DOWNLOAD_PATH = os.getenv('TEST_FILE_DOWNLOAD_PATH', 'test.txt')

    # Model Settings
    MODEL_STORAGE_MODE = os.getenv('MODEL_STORAGE_MODE')
    OVERWRITE_EXISTING_MODELS = os.getenv('OVERWRITE_EXISTING_MODELS', 'False').lower() == 'true'
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

    # API Settings
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8000))
    API_LOG_LEVEL = os.getenv('API_LOG_LEVEL', 'debug')
    API_STARTUP_MODEL_LOADING_LIMIT = int(os.getenv('API_STARTUP_MODEL_LOADING_LIMIT', 2))

    # Secrets
    SECRETS = {
        'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'aws_region': os.getenv('AWS_REGION'),
    }

    # Model Mappings (from json file)
    if os.path.exists(MODEL_MAPPINGS_FILE):
        with open(MODEL_MAPPINGS_FILE, 'r') as f:
            model_mappings = json.load(f)
    else:
        model_mappings = {}

    # Language Mappings (from json file)
    if os.path.exists(LANGUAGE_MAPPINGS_FILE):
        with open(LANGUAGE_MAPPINGS_FILE, 'r') as f:
            language_mappings = json.load(f)
    else:
        language_mappings = {}
