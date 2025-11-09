from typing import Dict, List, TYPE_CHECKING
from transformers import pipeline


# imports not needed at runtime
if TYPE_CHECKING:
    from transformers import Pipeline


class ModelManager:
    '''
    Helper class for loading and managing the ML models
    for the API.
    '''
    def __init__(
            self,
            valid_translations: List[str],
            model_mappings: Dict[str, str]
    ):
        '''
        Initialize the ModelManager class.

        Params:
        --------
        valid_translations: List[str]
            A list of valid translation pairs.
        model_mappings: Dict[str, str]
            A dictionary mapping translation pairs to
            model names. Should be valid Hugging Face
            model names.
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
            not isinstance(valid_translations, list)
            or not valid_translations
        ):
            raise ValueError(
                "valid_translations must be a non-empty list"
            )

        # save valid model mappings based on valid translations
        valid_translations = [
            translation.lower()
            for translation in valid_translations
            if isinstance(translation, str)
        ]

        self.model_mappings = {
            k.lower(): v for k, v in model_mappings.items()
            if isinstance(k, str)
            and isinstance(v, str)
            and k.lower() in valid_translations
        }

    @staticmethod
    def load_model(
        model_name: str,
        task: str = "translation"
    ) -> "Pipeline":
        '''
        Loads a model from Hugging Face transformers using the
        pipeline function.

        Params:
        ---------
        model_name: str
            The name of the model to load from Hugging Face.
        task: str
            The task for the model
            (default is "translation").
        '''
        return pipeline(task, model=model_name)
