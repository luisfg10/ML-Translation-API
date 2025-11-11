# ---------------------------------------------------------------------------------
# Global Variables

# python
PYTHON_INTERPRETER = python3.12
APP = main.py

# model testing
test_text = Hello, how are you?

# app settings
translation-pair = en-fr
model-storage-mode = local
bucket-name = None

# ---------------------------------------------------------------------------------
# Makefile targets

upload_model:
	$(PYTHON_INTERPRETER) $(APP) upload-model \
		--translation-pair $(translation-pair) \
		--model-storage-mode $(model-storage-mode) \
		--bucket-name $(bucket-name)

test_model_prediction:
	$(PYTHON_INTERPRETER) $(APP) test-model-prediction \
		--translation-pair $(translation-pair) \
		--input-text "$(test_text)"

run_api_on_server:
	$(PYTHON_INTERPRETER) $(APP) run-server
