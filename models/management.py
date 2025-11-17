# Third-party imports
import json
from loguru import logger
from typing import Dict, Optional
from pathlib import Path
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForSeq2SeqLM

# Local imports
from settings.config import (
    AVAILABLE_TRANSLATIONS,
    AVAILABLE_MODEL_STORAGE_MODES,
    LOCAL_MODEL_DIR
)
from models.aws import AWSServicesManager


class TranslationModelManager(AWSServicesManager):
    '''
    Helper class for managing interactions with the ML models in the project,
    including:
        - loading models from Hugging Face
        - downloading models locally
        - uploading models to S3
        - downloading models from S3
        - loading models and conducting inference

    Inherits from AWSServicesManager to handle AWS S3 interactions.
    '''
    def __init__(
            self,
            model_mappings: Dict[str, str],
            model_storage_mode: str,
            overwrite_existing_models: bool = False
    ) -> None:
        '''
        Initialize the ModelManager class.

        Args:
            model_mappings: Dict[str, str]
                A dictionary mapping translation pairs to HuggingFace hub
                model names.
                e.g., {'en-fr': 'Helsinki-NLP/opus-mt-en-fr', ...}
            model_storage_mode: str
                The mode of model storage, either 's3' or 'local'.
                This parameter informs how models will be saved and loaded.
            overwrite_existing_models: bool
                Whether to overwrite existing local model files when doing download
                operations if such files already exist locally.
        '''
        # check inputs
        if (
            not isinstance(model_mappings, dict)
            or not model_mappings
        ):
            raise ValueError(
                "model_mappings must be a non-empty dictionary"
            )
        elif (
            not isinstance(model_storage_mode, str)
            or model_storage_mode.lower() not in AVAILABLE_MODEL_STORAGE_MODES
        ):
            raise ValueError(
                f"model_storage_mode must be one of "
                f"{AVAILABLE_MODEL_STORAGE_MODES}"
            )

        # save values to self
        self.overwrite_existing_models = overwrite_existing_models
        self.model_mappings = {
            k.lower(): v for k, v in model_mappings.items()
            if isinstance(k, str)
            and isinstance(v, str)
            and k.lower() in AVAILABLE_TRANSLATIONS
        }
        self.model_storage_mode = model_storage_mode.lower()

        # Add cache for loaded models
        self._model_cache = {}
        self._tokenizer_cache = {}
        logger.info(
            f"Initialized ModelManager with storage mode: "
            f"{self.model_storage_mode} "
            "and translation pairs: "
            f"{list(self.model_mappings.keys())}"
        )

        # init parent class
        if self.model_storage_mode == 's3':
            super().__init__(service='s3', init_client=True)

    def _resolve_model_from_translation_pair(
            self,
            translation_pair: str
    ) -> str:
        '''
        Resolves the Hugging Face model name for a given translation pair.

        Args:
            translation_pair: str
                The translation pair to resolve (e.g., 'en-fr', 'en-es').

        Returns:
            str
                The corresponding Hugging Face model name.

        Raises:
            ValueError
                If the translation pair is not found in the model mappings.
        '''
        if not isinstance(translation_pair, str):
            raise ValueError("'translation_pair' must be a string")
        translation_pair = translation_pair.lower()
        if translation_pair not in self.model_mappings:
            raise ValueError(
                f"Translation pair '{translation_pair}' not found. "
                f"Available pairs: "
                f"{list(self.model_mappings.keys())}"
            )
        return self.model_mappings[translation_pair]

    def _download_model_from_hugging_face(
            self,
            translation_pair: str
    ) -> None:
        '''
        Fetches a model and its tokenizer from the Hugging Face hub and saves it locally
        in a '.onnx' format in the specified local directory.
        Handles failures gracefully by logging errors without raising exceptions.

        Logic:
            1. Validates the translation pair exists in model mappings
            2. Downloads the PyTorch model from Hugging Face Hub
            3. Converts the model to ONNX format using Optimum library
               for better inference performance
            4. Downloads and saves the corresponding tokenizer
            5. Saves both model and tokenizer to a local directory

            ONNX (Open Neural Network Exchange) format provides:
            - Faster inference compared to PyTorch models
            - Smaller memory footprint
            - Cross-platform compatibility
            - Hardware optimization capabilities

        Args:
            translation_pair: str
                The translation pair to download (e.g., 'en-fr', 'en-es').
        '''
        # get model name from translation pair
        try:
            model_name = self._resolve_model_from_translation_pair(
                translation_pair=translation_pair
            )
        except ValueError as e:
            logger.error(str(e))
            return

        # check if directory already exists locally
        expected_model_dir = Path(LOCAL_MODEL_DIR) / translation_pair
        if not self.overwrite_existing_models and expected_model_dir.exists():
            logger.debug(
                f"Model for translation pair '{translation_pair}' "
                f"already exists locally at {expected_model_dir}, "
                "so download is skipped. To alter this behavior, set "
                f"'overwrite_existing_models=True' when creating the ModelManager instance."
            )
            return

        # local download
        logger.info(
            f"Downloading model '{model_name}' for translation pair "
            f"'{translation_pair}' from Hugging Face hub..."
        )
        try:
            # create local directory structure
            model_dir = Path(LOCAL_MODEL_DIR) / translation_pair
            model_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created model directory: {model_dir}")

            # download and convert model to ONNX format
            logger.debug("Converting model to ONNX format...")
            onnx_model = ORTModelForSeq2SeqLM.from_pretrained(
                model_name,
                export=True,  # Automatically convert to ONNX
                cache_dir=str(model_dir)
            )

            # download tokenizer alongside the model
            logger.debug("Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)

            # save both model and tokenizer to local directory
            onnx_model.save_pretrained(str(model_dir))
            tokenizer.save_pretrained(str(model_dir))

            logger.success(
                f"Successfully saved ONNX model and tokenizer for '{translation_pair}' "
                f"to {model_dir}"
            )

        except Exception as e:
            logger.error(
                f"Failed to download and convert model '{model_name}': {str(e)}"
            )
            return

    def _download_model_from_s3(
            self,
            translation_pair: str,
            s3_bucket_name: str
    ) -> None:
        '''
        Downloads a model from the specified S3 bucket to the local model directory.
        Expects the models to be stored in exactly the same directory structure as
        that used for local downloads:
            '{LOCAL_MODEL_DIR}/{translation_pair}/'

        Args:
            translation_pair: str
                The translation pair to download (e.g., 'en-fr', 'en-es').
            s3_bucket_name: str
                The name of the S3 bucket to download the model from.
        '''
        # check if directory already exists locally
        expected_model_dir = Path(LOCAL_MODEL_DIR) / translation_pair
        if not self.overwrite_existing_models and expected_model_dir.exists():
            logger.debug(
                f"Model for translation pair '{translation_pair}' "
                f"already exists locally at {expected_model_dir}, "
                "so download is skipped. To alter this behavior, set "
                f"'overwrite_if_exists=True' when calling this method."
            )
            return

        logger.info(
            f"Downloading model for translation pair '{translation_pair}' "
            f"from S3 bucket '{s3_bucket_name}'. This may take a few minutes..."
        )
        self.download_directory_from_s3(
            s3_bucket_name=s3_bucket_name,
            s3_prefix=expected_model_dir.name,
            local_directory=expected_model_dir.name
        )

    def save_model(
            self,
            translation_pair: str,
            s3_bucket_name: Optional[str] = None
    ) -> None:
        '''
        Router method to upload/save a model based on the specified upload mode saved
        to the ModelManager instance.
        Local saving involves downlaoding the model from Hugging Face and saving it
        locally in ONNX format.
        S3 uploading involves downloading the model from Hugging Face locally first,
        then uploading the local files to the specified S3 bucket.

        Args:
            translation_pair: str
                The translation pair to upload (e.g., 'en-fr', 'en-es').
            s3_bucket_name: Optional[str]
                The name of the S3 bucket to upload the model to.
                Required if self.model_storage_mode is 's3'.
        '''
        self._download_model_from_hugging_face(translation_pair=translation_pair)

        if self.model_storage_mode == 's3':
            # get directory name
            directory_to_upload = Path(LOCAL_MODEL_DIR) / translation_pair
            if not directory_to_upload.exists():
                raise FileNotFoundError(
                    f"Local model directory '{directory_to_upload}' does not exist. "
                    "Cannot upload to S3."
                )
            logger.debug(
                "Uploading model to S3, this action may take a few minutes..."
            )
            self.upload_directory_to_s3(
                s3_bucket_name=s3_bucket_name,
                local_directory=directory_to_upload
            )

    def load_api_models(
            self,
            s3_bucket_name: Optional[str] = None,
            model_limit: Optional[int] = 2
    ) -> None:
        '''
        Executes logic to load all available models from AVAILABLE_TRANSLATIONS
        following the specified model storage mode.

        Args:
            s3_bucket_name: Optional[str]
                The name of the S3 bucket to download models from.
                Required if self.model_storage_mode is 's3'.
            model_limit: Optional[int]
                Maximum number of models to load at once to avoid memory overload.
        '''
        for translation_pair in AVAILABLE_TRANSLATIONS[:model_limit]:
            if self.model_storage_mode == 'local':
                self._download_model_from_hugging_face(translation_pair=translation_pair)
            elif self.model_storage_mode == 's3':
                self._download_model_from_s3(
                    translation_pair=translation_pair,
                    s3_bucket_name=s3_bucket_name
                )

    def get_models_info(
            self,
            return_model_config: Optional[bool] = False
    ) -> Dict[str, str]:
        '''
        Returns information about the currently-loaded models available for the API per
        translation pair.

        Args:
            return_model_config: bool
                If True, returns additional model configuration details from the
                'config.json' file saved alongside the model.

        Returns:
            Dict[str, str]
                A dictionary with translation pairs as keys and model names as values.

        >>> model_manager = TranslationModelManager(
        ...     model_mappings={'en-fr': 'Helsinki-NLP/opus-mt-en-fr'},
        ...     model_storage_mode='local'
        ... )
        >>> print(model_manager.get_models_info(return_model_config=True))
        {
            'en-fr': {
                'model_name': 'Helsinki-NLP/opus-mt-en-fr',
                'file_type': 'ONNX',
                'config': { ... }  # contents of {LOCAL_MODEL_DIR}/{translation_pair}/config.json
            },
            ...
        }
        '''
        # walk directory to find downloaded models
        models = {}
        for translation_pair in AVAILABLE_TRANSLATIONS:
            model_dir = Path(LOCAL_MODEL_DIR) / translation_pair
            if model_dir.exists():
                models[translation_pair] = {
                    "model_name": self.model_mappings[translation_pair],
                    "file_type": "ONNX"
                }
                if return_model_config:
                    config_path = model_dir / "config.json"
                    if config_path.exists():
                        try:
                            with open(config_path, 'r') as f:
                                config_data = json.load(f)
                            models[translation_pair]["config"] = config_data
                        except Exception as e:
                            logger.error(
                                f"Failed to read config for '{translation_pair}': {str(e)}"
                            )
        return models

    def predict(
            self,
            translation_pair: str,
            text: str,
            max_length: Optional[int] = 512,
            num_beams: Optional[int] = 4,
            early_stopping: Optional[bool] = True,
            raise_on_missing_model: Optional[bool] = True
    ) -> str:
        '''
        Translates the given text using the model corresponding to the specified
        translation pair.

        To improve performance, caches loaded models in memory to avoid loading
        them redundantly for several predictions.
        Expects the model to be already downloaded locally in the path
            '{LOCAL_MODEL_DIR}/{translation_pair}' in ONNX format.

        Args:
            translation_pair: str
                The translation pair to use (e.g., 'en-fr', 'en-es').
            text: str
                The text to translate.
            max_length: Optional[int]
                Maximum length of generated translation, in tokens (default: 512).
            num_beams: Optional[int] = 4,
                Number of beams for beam search, aka the number of parallel translations to run.
                Higher = better quality but slower (default: 4).
            early_stopping: Optional[bool] = True,
                Whether to stop generation when all beams finish (default: True).
                If False, generation continues until max_length is reached.
            raise_on_missing_model: Optional[bool] = True
                If True, raises an error if the model for the specified translation pair
                is not found locally.
                If False, attempts to download the model and proceed with the prediction.

        Returns:
            str
                The translated text.
        '''
        # Validate inputs
        if not isinstance(text, str) or not text.strip():
            raise ValueError("'text' must be a non-empty string")

        # Check if translation pair is supported (will raise if not)
        self._resolve_model_from_translation_pair(translation_pair)

        # Check if model exists locally
        model_dir = Path(LOCAL_MODEL_DIR) / translation_pair
        if not model_dir.exists():
            if raise_on_missing_model:
                raise FileNotFoundError(
                    f"Model for translation pair '{translation_pair}' not found at '{model_dir}'. "
                    "Please download the model first using the 'save_model()' method."
                )
            else:
                logger.warning(
                    f"Model for translation pair '{translation_pair}' not found locally. "
                    "Attempting to download..."
                )
                self._download_model_from_hugging_face(translation_pair=translation_pair)

                # Check again after download attempt
                if not model_dir.exists():
                    raise FileNotFoundError(
                        f"Failed to download model for translation pair '{translation_pair}'. "
                        f"Model directory '{model_dir}' does not exist after download attempt."
                    )

        # Load from cache or disk
        if translation_pair not in self._model_cache:
            logger.debug(f"Loading model from '{model_dir}' (first time)")

            # Convert to absolute path to avoid Hugging Face interpreting it as a repo ID
            abs_model_dir = model_dir.resolve()
            logger.debug(f"Absolute model directory: {abs_model_dir}")

            # Verify that required ONNX files exist
            required_files = [
                "encoder_model.onnx",
                "decoder_model.onnx",
                "decoder_with_past_model.onnx"
            ]
            missing_files = [f for f in required_files if not (abs_model_dir / f).exists()]

            if missing_files:
                raise FileNotFoundError(
                    f"Missing required ONNX model files in '{abs_model_dir}': {missing_files}. "
                    "The model may not have been properly downloaded or converted."
                )

            self._model_cache[translation_pair] = ORTModelForSeq2SeqLM.from_pretrained(
                str(abs_model_dir),
                encoder_file_name="encoder_model.onnx",
                decoder_file_name="decoder_model.onnx",
                decoder_with_past_file_name="decoder_with_past_model.onnx"
            )
            self._tokenizer_cache[translation_pair] = AutoTokenizer.from_pretrained(
                str(abs_model_dir)
            )
        else:
            logger.debug(f"Using cached model for '{translation_pair}'")

        model = self._model_cache[translation_pair]
        tokenizer = self._tokenizer_cache[translation_pair]

        # Tokenize input text
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

        # Generate translation with custom parameters
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=num_beams,
            early_stopping=early_stopping
        )

        # Decode output
        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return translated_text
