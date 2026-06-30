"""Embeddings provider abstraction."""

from abc import ABC, abstractmethod


class EmbeddingsProvider(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    def info(self) -> dict:
        return {
            "capability": "embeddings",
            "id": self.id,
            "label": self.label,
            "available": self.is_available(),
        }
