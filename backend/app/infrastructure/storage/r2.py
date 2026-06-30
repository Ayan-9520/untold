"""Backward-compatible object storage shim.

Delegates to the canonical domain storage provider (S3/R2).
Prefer ``app.domain.storage.registry`` for new code.
"""

from __future__ import annotations

import logging
import uuid
from typing import BinaryIO

from app.domain.storage.s3_r2 import S3R2StorageProvider

logger = logging.getLogger("untold.storage")


class ObjectStorage:
    def __init__(self) -> None:
        self._provider = S3R2StorageProvider()

    @property
    def enabled(self) -> bool:
        return self._provider.is_available()

    def build_key(self, prefix: str, filename: str) -> str:
        safe = filename.replace(" ", "-").lower()
        return f"studio/{prefix}/{uuid.uuid4().hex}-{safe}"

    def public_url(self, key: str) -> str:
        from app.core.config import get_settings

        s = get_settings()
        if s.cdn_base_url:
            return f"{s.cdn_base_url.rstrip('/')}/{key}"
        url = self._provider.get_signed_url(key)
        return url or key

    def upload(self, key: str, body: BinaryIO, content_type: str) -> str:
        if not self.enabled:
            raise RuntimeError("Object storage is not configured")
        data = body.read()
        result = self._provider.upload(key, data, content_type)
        return result.url

    def delete(self, key: str) -> None:
        if not self.enabled:
            return
        try:
            self._provider.delete(key)
        except Exception as exc:
            logger.warning("Failed to delete object %s: %s", key, exc)

    def get_bytes(self, key: str) -> bytes:
        if not self.enabled:
            raise RuntimeError("Object storage is not configured")
        return self._provider.get_bytes(key)


storage = ObjectStorage()
