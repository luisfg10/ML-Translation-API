# Third-party imports
from loguru import logger
import os
import boto3
from typing import Optional, Union
from pathlib import Path

# Local imports
from settings.environment_config import EnvironmentConfig


class AWSServicesManager:
    def __init__(
            self,
            service: Optional[str] = 's3',
            aws_access_key_id: Optional[str] = None,
            aws_secret_access_key: Optional[str] = None,
            aws_region: Optional[str] = None,
            init_client: bool = True
    ) -> None:
        '''
        Initializes the AWS Services Manager with optional credentials.
        If not provided, it will use environment variables.

        Args:
            service (str, optional)
                The AWS service to manage. Defaults to 's3'.
            aws_access_key_id (str, optional)
                The AWS access key. If None, will pull value from env vars.
            aws_secret_access_key (str, optional)
                The AWS secret access key. If None, will pull value from env vars.
            aws_region (str, optional)
                The AWS region. If None, will pull value from env vars.
            init_client (bool, optional)
                Whether to initialize the AWS client upon creation. Defaults to True.
        '''
        self.service = service
        if not aws_access_key_id:
            aws_access_key_id = EnvironmentConfig.SECRETS.get('aws_access_key_id')
        self.aws_access_key_id = aws_access_key_id
        if not aws_secret_access_key:
            aws_secret_access_key = EnvironmentConfig.SECRETS.get('aws_secret_access_key')
        self.aws_secret_access_key = aws_secret_access_key
        if not aws_region:
            aws_region = EnvironmentConfig.SECRETS.get('aws_region')
        self.aws_region = aws_region

        if init_client:
            self._init_client()

    def _init_client(self) -> None:
        '''
        Creates an AWS client using boto3 and saves it to the self.
        '''
        self.client = boto3.client(
            self.service,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region
        )
        logger.info(f"AWS {self.service} client initialized successfully.")

    def _validate_service(
            self,
            required_service: str
    ) -> None:
        '''
        Validates that the class instance can perform a given operation
        by checking the service type. Raises an error if the service does not match.
        '''
        if self.service != required_service:
            raise ValueError(
                f"Service is not {required_service}. Cannot perform this operation."
            )

    def create_s3_bucket(
            self,
            s3_bucket_name: str,
    ) -> None:
        '''
        Creates an S3 bucket with the given name.

        Args:
            s3_bucket_name (str)
                The name of the S3 bucket to create.
        '''
        self._validate_service(required_service='s3')

        self.client.create_bucket(
            Bucket=s3_bucket_name
        )
        logger.success(f"S3 bucket '{s3_bucket_name}' created successfully.")

    def list_s3_bucket_contents(
            self,
            s3_bucket_name: str,
            bucket_prefix: Optional[str] = None,
            simplify_response: bool = True,
            verbose: bool = False
    ) -> None:
        '''
        Lists the contents of the specified S3 bucket.

        Args:
            s3_bucket_name (str)
                The name of the S3 bucket to list contents from.
            bucket_prefix (str, optional)
                The prefix to filter objects in the bucket. Defaults to None.
                use this to list objects within a specific "folder" in the bucket.
            simplify_response (bool, optional)
                Whether to simplify the response to only include object keys and sizes.
                Defaults to True.
            verbose (bool, optional)
                Whether to print the full response. Defaults to False.
        '''
        self._validate_service(required_service='s3')
        if not s3_bucket_name:
            raise ValueError("s3_bucket_name must be provided.")

        if bucket_prefix:
            response = self.client.list_objects_v2(
                Bucket=s3_bucket_name,
                Prefix=bucket_prefix
            )
        else:
            response = self.client.list_objects_v2(
                Bucket=s3_bucket_name
            )

        if simplify_response:
            response = {
                'Contents': [
                    {'Key': obj['Key'], 'Size': obj['Size']}
                    for obj in response.get('Contents', [])
                ]
            }
        if verbose:
            logger.info(f"S3 Bucket '{s3_bucket_name}' response: {response}")

        return response

    def upload_file_to_s3(
            self,
            s3_bucket_name: str,
            local_filepath: Union[str, Path],
            s3_filepath: Optional[str] = None,
            verbose: bool = False
    ) -> None:
        '''
        Uploads a file to the specified S3 bucket.

        Args:
            s3_bucket_name (str)
                The name of the S3 bucket to upload the file to.
            local_filepath (Union[str, Path])
                The path to the file to upload.
            s3_filepath (str, optional)
                The S3 file path where the file will be uploaded.
                If not provided, uses the local file name.
            verbose (bool, optional)
                Whether to log verbose output. Defaults to False.
        '''
        self._validate_service(required_service='s3')

        self.client.upload_file(
            Filename=local_filepath,
            Bucket=s3_bucket_name,
            Key=s3_filepath or os.path.basename(local_filepath)
        )

        if verbose:
            logger.success(
                f"File '{local_filepath}' uploaded to S3 bucket '{s3_bucket_name}' successfully."
            )

    def upload_directory_to_s3(
            self,
            s3_bucket_name: str,
            local_directory: Union[str, Path],
            s3_directory: Optional[str] = None
    ) -> None:
        '''
        Uploads all files from a local directory to the specified S3 bucket.
        S3 doesn't support directories natively, so in order to upload a directory
        each file is uploaded individually within the same sub-directory structure.
        Uploaded files to s3 retain their relative paths.

        Args:
            s3_bucket_name (str)
                The name of the S3 bucket to upload files to.
            local_directory (Union[str, Path])
                The path to the local directory to upload.
            s3_directory (str, optional)
                Custom S3 directory path where files will be uploaded.
                If not provided, uses the local directory's default path.
        '''
        self._validate_service(required_service='s3')

        for root, _, files in os.walk(local_directory):
            for file in files:
                local_filepath = os.path.join(root, file)
                if s3_directory:
                    filename = os.path.relpath(
                        local_filepath,
                        local_directory
                    )
                    s3_filepath = os.path.join(
                        s3_directory,
                        filename
                    )
                else:
                    s3_filepath = local_filepath

                self.upload_file_to_s3(
                    s3_bucket_name=s3_bucket_name,
                    local_filepath=local_filepath,
                    s3_filepath=s3_filepath
                )
        logger.success(
            f"Directory '{local_directory}' uploaded to S3 bucket '{s3_bucket_name}' successfully."
        )

    def download_file_from_s3(
            self,
            s3_bucket_name: str,
            s3_filepath: str,
            local_filepath: str,
            verbose: bool = False
    ) -> None:
        '''
        Downloads a file from the specified S3 bucket and file location to a local path.

        Args:
            s3_bucket_name (str)
                The name of the S3 bucket to download the file from.
            s3_filepath (str)
                The S3 file path of the file to download.
            local_filepath (str)
                The local path where the file will be saved.
            verbose (bool, optional)
                Whether to log verbose output. Defaults to False.
        '''
        self._validate_service(required_service='s3')

        self.client.download_file(
            Bucket=s3_bucket_name,
            Key=s3_filepath,
            Filename=local_filepath
        )
        if verbose:
            logger.success(
                f"File '{s3_filepath}' downloaded from S3 bucket '{s3_bucket_name}' "
                f"to '{local_filepath}' successfully."
            )

    def download_directory_from_s3(
            self,
            s3_bucket_name: str,
            s3_prefix: str,
            local_directory: Union[str, Path]
    ) -> None:
        '''
        Downloads all files from a specified S3 directory to a local directory.
        S3 doesn't support directories natively, so this function lists all objects
        with the given prefix and downloads them while retaining their relative paths.

        Args:
            s3_bucket_name (str)
                The name of the S3 bucket to download files from.
            s3_directory (str)
                The S3 directory path to download files from within the bucket.
            local_directory (Union[str, Path])
                The local directory where files will be saved.
        '''
        self._validate_service(required_service='s3')

        paginator = self.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=s3_bucket_name, Prefix=s3_prefix):
            for obj in page.get('Contents', []):
                s3_filepath = obj['Key']
                relative_path = os.path.relpath(s3_filepath, s3_prefix)
                local_filepath = os.path.join(local_directory, relative_path)
                os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
                self.download_file_from_s3(
                    s3_bucket_name=s3_bucket_name,
                    s3_filepath=s3_filepath,
                    local_filepath=local_filepath
                )
        logger.success(
            f"Directory '{s3_prefix}' downloaded from S3 bucket '{s3_bucket_name}' "
            f"to '{local_directory}' successfully."
        )
