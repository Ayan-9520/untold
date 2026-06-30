"""S3 / Cloudflare R2 storage provider."""

import logging

from app.core.config import get_settings
from app.domain.storage.base import StorageProvider, StorageUploadResult

logger = logging.getLogger("untold.storage.s3")


class S3R2StorageProvider(StorageProvider):
    id = "s3_r2"
    label = "S3 / R2 Cloud"

    def is_available(self) -> bool:
        s = get_settings()
        return bool(s.s3_bucket and s.aws_access_key_id and s.aws_secret_access_key)

    def _client(self):
        import boto3
        from botocore.config import Config

        s = get_settings()
        kwargs = {
            "aws_access_key_id": s.aws_access_key_id,
            "aws_secret_access_key": s.aws_secret_access_key,
            "region_name": s.s3_region,
            "config": Config(signature_version="s3v4"),
        }
        if s.s3_endpoint_url:
            kwargs["endpoint_url"] = s.s3_endpoint_url
        return boto3.client("s3", **kwargs), s

    def upload(self, key: str, data: bytes, content_type: str | None = None) -> StorageUploadResult:
        client, s = self._client()
        extra: dict = {}
        if content_type:
            extra["ContentType"] = content_type
        extra["CacheControl"] = "public, max-age=31536000, immutable"
        client.put_object(Bucket=s.s3_bucket, Key=key, Body=data, **extra)
        url = self.get_signed_url(key)
        if s.cdn_base_url:
            url = f"{s.cdn_base_url.rstrip('/')}/{key}"
        return StorageUploadResult(key=key, url=url, provider=self.id, size_bytes=len(data))

    def delete(self, key: str) -> None:
        client, s = self._client()
        client.delete_object(Bucket=s.s3_bucket, Key=key)

    def get_signed_url(self, key: str, expires_in: int = 3600) -> str | None:
        try:
            client, s = self._client()
            return client.generate_presigned_url(
                "get_object",
                Params={"Bucket": s.s3_bucket, "Key": key},
                ExpiresIn=expires_in,
            )
        except Exception as exc:
            logger.warning("Presign failed: %s", exc)
            return None

    def get_bytes(self, key: str) -> bytes:
        client, s = self._client()
        response = client.get_object(Bucket=s.s3_bucket, Key=key)
        return response["Body"].read()
