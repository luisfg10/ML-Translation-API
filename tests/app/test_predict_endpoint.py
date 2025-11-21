import os
import pytest
from fastapi.testclient import TestClient
from app.definition import app


class TestPredictEndpoint:
    '''
    Test class for the 'predict/' API endpoint, which indirectly tests
    the TranslationModelManager as well.
    '''

    def setup_method(self):
        '''
        Initializes the TestClient for running tests against the FastAPI app.

        Testing considerations:
            - Doesn't cover model downloading from Hugging Face or s3, in order
              to keep tests fast and lightweight.
            - Doesn't cover S3 functionality
        '''
        # set testing behavior
        os.environ["MODEL_STORAGE_MODE"] = "local"
        os.environ["OVERWRITE_EXISTING_MODELS"] = "false"
        os.environ["API_STARTUP_MODEL_LOADING_LIMIT"] = "0"

        # init test client
        self.client = TestClient(app)

        # save available translations to work with
        response = self.client.get("/models")
        data = response.json()
        self.available_translations = list(data["models"].keys())

        # save basic texts for predictions
        self.sample_texts = {
            "en": "Hello world!",
            "fr": "Bonjour le monde!",
            "es": "¡Hola mundo!",
            "de": "Hallo Welt!"
        }

    def test_basic_single_prediction(self):
        '''
        Test a single prediction with only the essential fields,
        using as reference the available translations which are evaluated dynamically.
        Only runs if there is at least one available translation, otherwise skips the
        test.

        Checks:
            - status code
            - response structure contains schema with only one element like:
                {
                    "results": [{
                        "position": 0,
                        "result": "translated text"
                    }]
                }
            - translated text is non-empty
        '''
        if not self.available_translations:
            pytest.skip("No translation models available for testing")

        translation_pair_to_test = self.available_translations[0]

        source_lang, target_lang = translation_pair_to_test.split("-")
        text_to_translate = self.sample_texts.get(source_lang)
        request_payload = {
            "items": [{
                "source": source_lang,
                "target": target_lang,
                "text": text_to_translate
            }]
        }
        response = self.client.post(
            "/predict",
            json=request_payload
        )

        # status code
        assert response.status_code == 200
        # content structure
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) == 1
        first_result = data["results"][0]
        assert all(
            key in first_result
            for key in ("position", "result")
        )
        assert first_result["position"] == 0
        assert isinstance(first_result["result"], str)
        assert len(first_result["result"].strip()) > 0

    def test_basic_multiple_predictions(self):
        '''
        Test multiple predictions in a single request.
        Only runs if there is at least one available translation, otherwise skips the
        test.

        Checks:
            - all checks from single prediction test
            - number of results matches number of input texts
        '''
        if not self.available_translations:
            pytest.skip("No translation models available for testing")

        translation_pair_to_test = self.available_translations[0]

        source_lang, target_lang = translation_pair_to_test.split("-")
        text_to_translate = self.sample_texts.get(source_lang)

        # Create multiple items for batch prediction
        request_payload = {
            "items": [
                {
                    "source": source_lang,
                    "target": target_lang,
                    "text": text_to_translate
                },
                {
                    "source": source_lang,
                    "target": target_lang,
                    "text": text_to_translate
                },
                {
                    "source": source_lang,
                    "target": target_lang,
                    "text": text_to_translate
                }
            ]
        }

        response = self.client.post(
            "/predict",
            json=request_payload
        )

        # status code
        assert response.status_code == 200
        # content structure
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        # number of results matches number of input texts
        assert len(data["results"]) == 3

        # check each result
        for i, result in enumerate(data["results"]):
            assert all(
                key in result
                for key in ("position", "result")
            )
            assert result["position"] == i
            assert isinstance(result["result"], str)
            assert len(result["result"].strip()) > 0

    def test_prediction_with_optional_fields(self):
        '''
        Test a prediction request that includes optional, advanced fields.
        Only runs if there is at least one available translation, otherwise skips the
        test.

        Checks:
            - all checks from single prediction test
        '''
        if not self.available_translations:
            pytest.skip("No translation models available for testing")

        translation_pair_to_test = self.available_translations[0]

        source_lang, target_lang = translation_pair_to_test.split("-")
        text_to_translate = self.sample_texts.get(source_lang)

        # Include optional fields in the request
        request_payload = {
            "items": [{
                "source": source_lang,
                "target": target_lang,
                "text": text_to_translate,
                "max_length": 256,
                "num_beams": 3,
                "early_stopping": False
            }]
        }

        response = self.client.post(
            "/predict",
            json=request_payload
        )

        # status code
        assert response.status_code == 200
        # content structure
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) == 1
        first_result = data["results"][0]
        assert all(
            key in first_result
            for key in ("position", "result")
        )
        assert first_result["position"] == 0
        assert isinstance(first_result["result"], str)
        assert len(first_result["result"].strip()) > 0

    def test_prediction_invalid_translation_pair(self):
        '''
        Test the API's 500 response for an invalid translation pair.
        unlike the other tests, this one can be run without any available models.
        '''
        # Use an invalid translation pair that shouldn't exist
        request_payload = {
            "items": [{
                "source": "invalid",
                "target": "nonexistent",
                "text": "Test text for invalid translation pair"
            }]
        }

        response = self.client.post(
            "/predict",
            json=request_payload
        )

        # Should return 500 error for invalid translation pair
        assert response.status_code == 500
        # Check error response structure
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert "translation attempts failed" in data["detail"].lower()
