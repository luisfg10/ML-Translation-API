from fastapi.testclient import TestClient
from app import app


class TestBasicEndpoints:
    """
    Test class for basic API endpoints: 'root/', 'health/', and 'models/'.
    """

    def setup_method(self):
        """
        Initializes the TestClient for running tests against the FastAPI app.
        Defined as an instance attribute as opposed to a class attribute
        for test isolation.
        """
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """
        Test root endpoint returns correct status and content.
        """
        response = self.client.get("/")

        # status code
        assert response.status_code == 200

        # content
        data = response.json()
        assert all(
            key in data
            for key in ("name", "version", "description")
        )

    def test_health_endpoint(self):
        """
        Test health endpoint returns correct status and content.
        """
        response = self.client.get("/health")

        # status code
        assert response.status_code == 200

        # content
        data = response.json()
        assert (
            "status" in data
            and data["status"] == "ok"
        )

    def test_models_endpoint_basic(self):
        """
        Test models endpoint without config parameter.
        """
        response = self.client.get("/models")

        # status code
        assert response.status_code == 200

        # content
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], dict)

        # Check structure of model info for one of the models
        if data.get("models"):
            first_model = next(iter(data["models"].values()))
            assert all(
                key in first_model
                for key in ("model_name", "file_type")
            )
            assert first_model["file_type"] == "ONNX"
            # Config should not be provided in basic response
            assert (
                "config" not in first_model
                or first_model["config"] is None
            )

    def test_models_endpoint_with_config(self):
        """
        Test models endpoint with config parameter set to true.
        """
        response = self.client.get("/models?return_model_config=true")

        assert response.status_code == 200

        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], dict)

        # Check that config is included when requested
        if data["models"]:
            first_model = next(iter(data["models"].values()))
            assert all(
                key in first_model
                and first_model[key] is not None
                for key in ("model_name", "file_type", "config")
            )

            assert isinstance(first_model["config"], dict)
            assert all(
                key in first_model["config"]
                for key in ("transformers_version", "model_type", "vocab_size")
            )
