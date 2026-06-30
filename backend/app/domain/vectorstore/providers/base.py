"""Vector store provider abstraction."""

from abc import ABC, abstractmethod

from app.domain.vectorstore.types import (
    VectorSearchRequest,
    VectorSearchResult,
    VectorUpsertRequest,
    VectorUpsertResult,
)


class VectorStoreProvider(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        ...

    def ensure_collection(self, collection: str, dimension: int) -> None:
        """Create collection/index if missing."""

    @abstractmethod
    def upsert(self, request: VectorUpsertRequest) -> VectorUpsertResult:
        ...

    @abstractmethod
    def search(self, request: VectorSearchRequest) -> VectorSearchResult:
        ...

    def delete(self, collection: str, ids: list[str]) -> int:
        return 0

    def info(self) -> dict:
        return {
            "capability": "vectorstore",
            "id": self.id,
            "label": self.label,
            "available": self.is_available(),
        }
