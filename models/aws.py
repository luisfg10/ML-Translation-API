from loguru import logger
import os
import boto3
from typing import Optional
from dotenv import load_dotenv

# Load .env file from parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)


class AWSServicesManager:
    def __init__(
            self,
            service: Optional[str] = 's3',
            aws_access_key: Optional[str] = None,
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
            aws_access_key (str, optional)
                The AWS access key. If None, will pull value from env vars.
            aws_secret_access_key (str, optional)
                The AWS secret access key. If None, will pull value from env vars.
            aws_region (str, optional)
                The AWS region. If None, will pull value from env vars.
            init_client (bool, optional)
                Whether to initialize the AWS client upon creation. Defaults to True.
        '''
        self.service = service
        if not aws_access_key:
            aws_access_key = os.getenv('AWS_ACCESS_KEY')
        self.aws_access_key = aws_access_key
        if not aws_secret_access_key:
            aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_secret_access_key = aws_secret_access_key
        if not aws_region:
            aws_region = os.getenv('AWS_REGION')
        self.aws_region = aws_region

        if init_client:
            self._init_client()

    def _init_client(self) -> None:
        '''
        Creates an AWS client using boto3 and saves it to the self.
        '''
        self.client = boto3.client(
            self.service,
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region
        )
        logger.info(f"AWS {self.service} client initialized successfully.")

    def create_s3_bucket(
            self,
            bucket_name: str,
    ) -> None:
        '''
        Creates an S3 bucket with the given name.

        Args:
            bucket_name (str)
                The name of the S3 bucket to create.
        '''
        if self.service != 's3':
            logger.error("Service is not S3. Cannot create S3 bucket.")
            return

        self.client.create_bucket(
            Bucket=bucket_name
        )
        logger.success(f"S3 bucket '{bucket_name}' created successfully.")

    def list_s3_bucket_contents(
            self,
            bucket_name: str,
            simplify_response: bool = True,
            print_response: bool = False
    ) -> None:
        '''
        Lists the contents of the specified S3 bucket.

        Args:
            bucket_name (str)
                The name of the S3 bucket to list contents from.
            simplify_response (bool, optional)
                Whether to simplify the response to only include object keys and sizes.
                Defaults to True.
            print_response (bool, optional)
                Whether to print the full response. Defaults to False.
        '''
        if self.service != 's3':
            logger.error("Service is not S3. Cannot list S3 bucket contents.")
            return

        response = self.client.list_objects_v2(
            Bucket=bucket_name
        )
        if simplify_response:
            response = {
                'Contents': [
                    {'Key': obj['Key'], 'Size': obj['Size']}
                    for obj in response.get('Contents', [])
                ]
            }
        if print_response:
            logger.info(f"S3 Bucket '{bucket_name}' Contents: {response}")

        return response

    def upload_file_to_s3(
            self,
            bucket_name: str,
            local_filepath: str,
            s3_filepath: Optional[str] = None
    ) -> None:
        '''
        Uploads a file to the specified S3 bucket.

        Args:
            bucket_name (str)
                The name of the S3 bucket to upload the file to.
            local_filepath (str)
                The path to the file to upload.
            s3_filepath (str, optional)
                The S3 file path where the file will be uploaded.
                If not provided, uses the local file name.
        '''
        if self.service != 's3':
            logger.error("Service is not S3. Cannot upload file to S3.")
            return

        self.client.upload_file(
            Filename=local_filepath,
            Bucket=bucket_name,
            Key=s3_filepath or os.path.basename(local_filepath)
        )
        logger.success(
            f"File '{local_filepath}' uploaded to S3 bucket '{bucket_name}' successfully."
        )

    def upload_directory_to_s3(
            self,
            bucket_name: str,
            local_directory: str,
            s3_directory: Optional[str] = None
    ) -> None:
        '''
        Uploads all files from a local directory to the specified S3 bucket.
        Uploaded files to s3 retain their relative paths.

        Args:
            bucket_name (str)
                The name of the S3 bucket to upload files to.
            local_directory (str)
                The path to the local directory to upload.
            s3_directory (str, optional)
                The S3 directory path where files will be uploaded.
                If not provided, uses the local directory name.
        '''
        if self.service != 's3':
            logger.error("Service is not S3. Cannot upload directory to S3.")
            return

        for root, _, files in os.walk(local_directory):
            for file in files:
                local_filepath = os.path.join(root, file)
                relative_path = os.path.relpath(local_filepath, local_directory)
                s3_filepath = os.path.join(
                    s3_directory or os.path.basename(local_directory),
                    relative_path
                )
                self.upload_file_to_s3(
                    bucket_name=bucket_name,
                    local_filepath=local_filepath,
                    s3_filepath=s3_filepath
                )
        logger.success(
            f"Directory '{local_directory}' uploaded to S3 bucket '{bucket_name}' successfully."
        )
