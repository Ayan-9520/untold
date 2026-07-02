"""Local filesystem storage for development."""

import os
import uuid
from pathlib import Path

from app.core.exceptions import ForbiddenError
from app.domain.storage.base import StorageProvider, StorageUploadResult

_UPLOAD_ROOT = Path(os.environ.get("UNTOLD_UPLOAD_DIR", "uploads/studio")).resolve()


def _upload_root() -> Path:
    return Path(os.environ.get("UNTOLD_UPLOAD_DIR", "uploads/studio")).resolve()


class LocalStorageProvider(StorageProvider):
    id = "local"
    label = "Local Storage"

    def __init__(self) -> None:
        _upload_root().mkdir(parents=True, exist_ok=True)

    def upload(self, key: str, data: bytes, content_type: str | None = None) -> StorageUploadResult:
        path = self.resolve_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return StorageUploadResult(
            key=key,
            url=f"/api/v1/studio/platform/assets/files/{key}",
            provider=self.id,
            size_bytes=len(data),
        )

    def delete(self, key: str) -> None:
        path = self.resolve_path(key)
        if path.exists():
            path.unlink()

    def resolve_path(self, key: str) -> Path:
        """Resolve storage key to an absolute path confined under the upload root."""
        root = _upload_root()
        normalized = key.replace("\\", "/").lstrip("/")
        if ".." in normalized.split("/"):
            raise ForbiddenError("Invalid file path")
        candidate = (root / normalized.replace("/", os.sep)).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ForbiddenError("Invalid file path") from exc
        return candidate

    @staticmethod
    def make_key(folder: str, filename: str) -> str:
        safe = filename.replace("..", "").replace("\\", "_").replace("/", "_")
        return f"{folder}/{uuid.uuid4().hex[:12]}_{safe}"

    @staticmethod
    def upload_root() -> Path:
        return _upload_root()
