# ---------------------------------------------------------------------------------
# Global Variables

# python
PYTHON_INTERPRETER = python3.11
APP = main.py

# ---------------------------------------------------------------------------------
# Makefile Commands

# Development
list_aws_s3_bucket_contents:
	$(PYTHON_INTERPRETER) $(APP) list-aws-s3-bucket-contents

aws_s3_file_upload:
	$(PYTHON_INTERPRETER) $(APP) aws-s3-file-upload

aws_s3_file_download:
	$(PYTHON_INTERPRETER) $(APP) aws-s3-file-download

aws_s3_directory_download:
	$(PYTHON_INTERPRETER) $(APP) aws-s3-directory-download

save_model:
	$(PYTHON_INTERPRETER) $(APP) save-model

run_model_prediction:
	$(PYTHON_INTERPRETER) $(APP) run-model-prediction

# Testing
run_pytest:
	$(PYTHON_INTERPRETER) -m pytest tests/


# API Server
run_api_on_server:
	$(PYTHON_INTERPRETER) $(APP) run-api-on-server
