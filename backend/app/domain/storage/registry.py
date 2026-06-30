"""Storage provider registry."""

from __future__ import annotations

from app.core.config import get_settings
from app.domain.storage.base import StorageProvider, StorageUploadResult
from app.domain.storage.local import LocalStorageProvider
from app.domain.storage.s3_r2 import S3R2StorageProvider

_registry: dict[str, StorageProvider] | None = None


def get_storage_registry() -> dict[str, StorageProvider]:
    global _registry
    if _registry is None:
        _registry = {
            "local": LocalStorageProvider(),
            "s3_r2": S3R2StorageProvider(),
        }
    return _registry


def resolve_storage_provider(preferred: str | None = None) -> StorageProvider:
    registry = get_storage_registry()
    settings = get_settings()
    order = []
    if preferred:
        order.append(preferred)
    order.append(settings.storage_default_provider if hasattr(settings, "storage_default_provider") else "local")
    order.extend(["s3_r2", "local"])
    seen: set[str] = set()
    for pid in order:
        if pid in seen:
            continue
        seen.add(pid)
        provider = registry.get(pid)
        if provider and provider.is_available():
            return provider
    return registry["local"]


def upload_bytes(key: str, data: bytes, content_type: str | None = None, provider_id: str | None = None) -> StorageUploadResult:
    return resolve_storage_provider(provider_id).upload(key, data, content_type)
