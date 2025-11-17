# ---------------------------------------------------------------------------------
# Global Variables

# python
PYTHON_INTERPRETER = python3.11
APP = main.py

# ---------------------------------------------------------------------------------
# Makefile Commands

# Testing

list_aws_s3_bucket_contents:
	$(PYTHON_INTERPRETER) $(APP) list-aws-s3-bucket-contents

test_aws_s3_file_upload:
	$(PYTHON_INTERPRETER) $(APP) test-aws-s3-file-upload

test_aws_s3_file_download:
	$(PYTHON_INTERPRETER) $(APP) test-aws-s3-file-download

test_aws_s3_directory_download:
	$(PYTHON_INTERPRETER) $(APP) test-aws-s3-directory-download

save_model:
	$(PYTHON_INTERPRETER) $(APP) upload-model

test_model_prediction:
	$(PYTHON_INTERPRETER) $(APP) test-model-prediction


# API Server

run_api_on_server:
	$(PYTHON_INTERPRETER) $(APP) run-api-on-server
