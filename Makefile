# ---------------------------------------------------------------------------------
# Global Variables

PYTHON_INTERPRETER = python3.12
APP = main.py

# ---------------------------------------------------------------------------------
# Makefile targets

upload_model:
	$(PYTHON_INTERPRETER) $(APP) upload-model \
		--model_name $(model_name) \
		--upload_mode $(upload_mode) \
		--bucket_name $(bucket_name)

run_api_on_server:
	$(PYTHON_INTERPRETER) $(APP) run-server
