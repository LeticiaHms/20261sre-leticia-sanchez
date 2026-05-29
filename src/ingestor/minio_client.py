import boto3
from botocore.client import Config
from common.config import config
from common.logger import logger

class MinioClient:
    """Wrapper para interações com o MinIO (S3 API)."""

    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=f"http://{config.MINIO_ENDPOINT}",
            aws_access_key_id=config.MINIO_ACCESS_KEY,
            aws_secret_access_key=config.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        self.bucket = "landing-zone"
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except:
            logger.info(f"Criando bucket {self.bucket}")
            self.s3.create_bucket(Bucket=self.bucket)

    def upload_file(self, file_path, object_name):
        """Faz o upload de um arquivo local para o MinIO."""
        try:
            self.s3.upload_file(file_path, self.bucket, object_name)
            logger.info(f"Upload concluído: {object_name}", bucket=self.bucket)
        except Exception as e:
            logger.error(f"Erro no upload para MinIO: {str(e)}")
            raise
