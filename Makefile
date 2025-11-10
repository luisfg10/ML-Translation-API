# ---------------------------------------------------------------------------------
# Global Variables

# python
PYTHON_INTERPRETER = python3.12
APP = main.py

# app settings
translation-pair = en-es
model-storage-mode = local
bucket-name = None

# ---------------------------------------------------------------------------------
# Makefile targets

upload_model:
	$(PYTHON_INTERPRETER) $(APP) upload-model \
		--translation-pair $(translation-pair) \
		--model-storage-mode $(model-storage-mode) \
		--bucket-name $(bucket-name)

run_api_on_server:
	$(PYTHON_INTERPRETER) $(APP) run-server
