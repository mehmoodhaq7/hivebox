"""MinIO S3-compatible storage integration."""

import boto3
import os
import json
import logging
from datetime import datetime, timezone
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = os.getenv("MINIO_BUCKET", "hivebox-data")


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )


def store_temperature(data: dict):
    """Store temperature data as JSON object in MinIO."""
    try:
        client = get_s3_client()
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
        key = f"temperature/{timestamp}.json"
        client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json",
        )
        logger.info("Temperature data stored: %s", key)
        return key
    except (BotoCoreError, ClientError) as e:
        logger.error("Storage failed: %s", e)
        return None