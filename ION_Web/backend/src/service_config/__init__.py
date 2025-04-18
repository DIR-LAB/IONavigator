from .mongo_config import MongoDBClient
from .s3_config import S3Client

s3_client = S3Client()
mongodb_client = MongoDBClient()
