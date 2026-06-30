"""Cloud storage provider abstraction — vendor-neutral."""

from dataclasses import dataclass


@dataclass
class StorageUploadResult:
    key: str
    url: str | None
    provider: str
    size_bytes: int


class StorageProvider:
    id: str = "base"
    label: str = "Storage"

    def is_available(self) -> bool:
        return True

    def upload(self, key: str, data: bytes, content_type: str | None = None) -> StorageUploadResult:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError

    def get_signed_url(self, key: str, expires_in: int = 3600) -> str | None:
        return None
