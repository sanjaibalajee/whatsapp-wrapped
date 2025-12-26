import boto3
import gzip
import json
import uuid
from io import BytesIO
from flask import current_app
from botocore.config import Config as BotoConfig


class StorageService:
    """Cloudflare R2 storage service"""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy initialization of S3 client"""
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=current_app.config["R2_ENDPOINT_URL"],
                aws_access_key_id=current_app.config["R2_ACCESS_KEY_ID"],
                aws_secret_access_key=current_app.config["R2_SECRET_ACCESS_KEY"],
                region_name="auto",  # Required for Cloudflare R2
                config=BotoConfig(
                    signature_version="s3v4",
                    retries={"max_attempts": 3, "mode": "adaptive"},
                ),
            )
        return self._client

    @property
    def bucket(self):
        return current_app.config["R2_BUCKET_NAME"]

    def upload_file(self, file_obj, prefix: str = "uploads") -> str:
        """
        Upload a file to R2
        Returns the S3 key
        """
        key = f"{prefix}/{uuid.uuid4()}.txt"

        self.client.upload_fileobj(
            file_obj,
            self.bucket,
            key,
            ExtraArgs={"ContentType": "text/plain"},
        )

        return key

    def upload_bytes(self, data: bytes, key: str, content_type: str = "application/octet-stream"):
        """Upload raw bytes to R2"""
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )

    def upload_json(self, data: dict, prefix: str = "results", compress: bool = True) -> str:
        """
        Upload JSON data to R2
        Optionally compresses with gzip
        Returns the S3 key
        """
        json_str = json.dumps(data, default=str)

        if compress:
            key = f"{prefix}/{uuid.uuid4()}.json.gz"
            compressed = gzip.compress(json_str.encode("utf-8"))
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=compressed,
                ContentType="application/gzip",
            )
        else:
            key = f"{prefix}/{uuid.uuid4()}.json"
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json_str.encode("utf-8"),
                ContentType="application/json",
            )

        return key

    def download_file(self, key: str) -> bytes:
        """Download file from R2"""
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def download_to_file(self, key: str, file_path: str):
        """Download file from R2 to local path"""
        self.client.download_file(self.bucket, key, file_path)

    def download_json(self, key: str) -> dict:
        """
        Download and parse JSON from R2
        Handles gzipped files automatically
        """
        data = self.download_file(key)

        if key.endswith(".gz"):
            data = gzip.decompress(data)

        return json.loads(data.decode("utf-8"))

    def get_file_stream(self, key: str) -> BytesIO:
        """Get file as a stream"""
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return BytesIO(response["Body"].read())

    def delete_file(self, key: str):
        """Delete file from R2"""
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def delete_files(self, keys: list[str]):
        """Delete multiple files from R2"""
        if not keys:
            return

        objects = [{"Key": key} for key in keys]
        self.client.delete_objects(
            Bucket=self.bucket,
            Delete={"Objects": objects},
        )

    def file_exists(self, key: str) -> bool:
        """Check if file exists in R2"""
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except self.client.exceptions.ClientError:
            return False

    def get_file_size(self, key: str) -> int:
        """Get file size in bytes"""
        response = self.client.head_object(Bucket=self.bucket, Key=key)
        return response["ContentLength"]


# Singleton instance
storage = StorageService()
