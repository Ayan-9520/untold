"""Local filesystem storage for development."""

import os
import uuid
from pathlib import Path

from app.domain.storage.base import StorageProvider, StorageUploadResult

_UPLOAD_ROOT = Path(os.environ.get("UNTOLD_UPLOAD_DIR", "uploads/studio"))


class LocalStorageProvider(StorageProvider):
    id = "local"
    label = "Local Storage"

    def __init__(self) -> None:
        _UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    def upload(self, key: str, data: bytes, content_type: str | None = None) -> StorageUploadResult:
        path = _UPLOAD_ROOT / key.replace("/", os.sep)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return StorageUploadResult(key=key, url=f"/api/v1/studio/platform/assets/files/{key}", provider=self.id, size_bytes=len(data))

    def delete(self, key: str) -> None:
        path = _UPLOAD_ROOT / key.replace("/", os.sep)
        if path.exists():
            path.unlink()

    def resolve_path(self, key: str) -> Path:
        return _UPLOAD_ROOT / key.replace("/", os.sep)

    @staticmethod
    def make_key(folder: str, filename: str) -> str:
        safe = filename.replace("..", "").replace("\\", "_").replace("/", "_")
        return f"{folder}/{uuid.uuid4().hex[:12]}_{safe}"
