"""S3 / Cloudflare R2 signed streaming URLs."""

import logging
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import get_settings

logger = logging.getLogger("untold")
settings = get_settings()


class StreamingService:
    @staticmethod
    def get_signed_stream_url(video_id: int, stream_key: str | None, fallback_url: str | None) -> tuple[str, int, str]:
        expires_in = settings.stream_url_expire_seconds

        if settings.s3_bucket and stream_key and settings.aws_access_key_id:
            try:
                url = StreamingService._s3_presigned_url(stream_key, expires_in)
                return url, expires_in, "hls" if stream_key.endswith(".m3u8") else "mp4"
            except Exception as exc:
                logger.warning("S3 presign failed, using token URL: %s", exc)

        if fallback_url and fallback_url.startswith("http"):
            token_url = StreamingService._jwt_signed_url(video_id, fallback_url, expires_in)
            return token_url, expires_in, "mp4"

        token_url = StreamingService._jwt_signed_url(video_id, f"stream://video/{video_id}", expires_in)
        return token_url, expires_in, "token"

    @staticmethod
    def get_magazine_download_url(storage_key: str | None, fallback_url: str | None) -> tuple[str, int]:
        expires_in = settings.stream_url_expire_seconds
        if settings.s3_bucket and storage_key and settings.aws_access_key_id:
            try:
                return StreamingService._s3_presigned_url(storage_key, expires_in), expires_in
            except Exception as exc:
                logger.warning("Magazine presign failed: %s", exc)
        if fallback_url:
            return fallback_url, expires_in
        raise ValueError("Magazine file not available")

    @staticmethod
    def _s3_presigned_url(key: str, expires_in: int) -> str:
        import boto3
        from botocore.config import Config

        client_kwargs = {
            "aws_access_key_id": settings.aws_access_key_id,
            "aws_secret_access_key": settings.aws_secret_access_key,
            "region_name": settings.s3_region,
            "config": Config(signature_version="s3v4"),
        }
        if settings.s3_endpoint_url:
            client_kwargs["endpoint_url"] = settings.s3_endpoint_url

        client = boto3.client("s3", **client_kwargs)
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    @staticmethod
    def _jwt_signed_url(video_id: int, base_url: str, expires_in: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        token = jwt.encode(
            {"vid": video_id, "exp": expire, "type": "stream"},
            settings.secret_key,
            algorithm=settings.algorithm,
        )
        sep = "&" if "?" in base_url else "?"
        return f"{base_url}{sep}token={token}"
