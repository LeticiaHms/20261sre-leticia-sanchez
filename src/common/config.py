import os
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    # MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "admin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "password123")
    MINIO_SECURE: bool = False

    # ClickHouse
    CH_HOST: str = os.getenv("CH_HOST", "localhost")
    CH_PORT: int = int(os.getenv("CH_PORT", "8123"))
    CH_USER: str = os.getenv("CH_USER", "admin")
    CH_PASSWORD: str = os.getenv("CH_PASSWORD", "password123")
    CH_DB: str = os.getenv("CH_DB", "northwind")

    # App
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    RETENTION_DAYS: int = 7

config = Config()
