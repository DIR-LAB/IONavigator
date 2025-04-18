import boto3
import os
from botocore.exceptions import ClientError
import traceback

class S3Client:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-2')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        print(f"Initialized S3 client with bucket: {self.bucket_name}")

    def upload_file(self, file_data, object_name):
        """Upload a file to S3"""
        try:
            print(f"Attempting to upload to S3: {object_name}")
            self.s3_client.upload_fileobj(file_data, self.bucket_name, object_name)
            print(f"Successfully uploaded: {object_name}")
            return True
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            return False

    def download_file(self, object_name):
        """Download a file from S3"""
        try:
            print(f"Attempting to download from S3: {object_name}")
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_name)
            content = response['Body'].read()
            print(f"Successfully downloaded: {object_name}")
            return content
        except ClientError as e:
            print(f"Error downloading from S3: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            return None

    def download_file_chunk(self, object_name, start_byte=0, chunk_size=8192):
        """Download a chunk of a file from S3"""
        try:
            print(f"Attempting to download chunk from S3: {object_name}")
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Range=f'bytes={start_byte}-{start_byte + chunk_size - 1}'
            )
            content = response['Body'].read()
            print(f"Successfully downloaded chunk: {object_name}")
            return content
        except ClientError as e:
            print(f"Error downloading chunk from S3: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            return None

    def get_file_url(self, object_name, expiration=3600):
        """Generate a presigned URL for an object"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None 
        
    def check_if_exists(self, object_name):
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError:
            return False
        
    def list_objects(self, prefix):
        """
        Recursively list all objects under a prefix directory in S3
        Returns a list of dictionaries containing object information
        """
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            objects = []
            
            # Iterate through each page of results
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    objects.extend(page['Contents'])
                
            print(objects)
            return objects
        except ClientError as e:
            print(f"Error listing objects: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            return []
        