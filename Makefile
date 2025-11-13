# ---------------------------------------------------------------------------------
# Global Variables

# python
PYTHON_INTERPRETER = python3.12
APP = main.py

# test settings
translation-pair = en-fr
model-storage-mode = local
bucket-name = None
test_text = Hello, how are you?

# API server settings
api_host = 127.0.0.1
api_port = 8000
log_level = debug

# ---------------------------------------------------------------------------------
# Makefile Commands

# Testing

upload_model:
	$(PYTHON_INTERPRETER) $(APP) upload-model \
		--translation-pair $(translation-pair) \
		--model-storage-mode $(model-storage-mode) \
		--bucket-name $(bucket-name)

test_model_prediction:
	$(PYTHON_INTERPRETER) $(APP) test-model-prediction \
		--translation-pair $(translation-pair) \
		--input-text "$(test_text)"


# API Server

run_api_on_server:
	$(PYTHON_INTERPRETER) $(APP) run-api-on-server \
		--model-storage-mode $(model-storage-mode) \
		--bucket-name $(bucket-name) \
		--host $(api_host) \
		--port $(api_port) \
		--log-level $(log_level)
