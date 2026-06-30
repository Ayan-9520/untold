"""Base provider contracts for all AI capabilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar


CAPABILITIES = (
    "llm",
    "image",
    "video",
    "voice",
    "music",
    "translation",
    "embeddings",
    "vectorstore",
)


class BaseProvider(ABC):
    """Vendor-neutral provider interface shared across studios."""

    capability: ClassVar[str] = "base"
    id: str = "base"
    label: str = "Base Provider"

    @abstractmethod
    def is_available(self) -> bool:
        """True when credentials and runtime dependencies are ready."""

    def info(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "id": self.id,
            "label": self.label,
            "available": self.is_available(),
        }


class LLMProvider(BaseProvider):
    capability = "llm"
    supports_modules: ClassVar[frozenset[str]] = frozenset()

    def supports(self, module: str) -> bool:
        return not self.supports_modules or module in self.supports_modules

    def info(self) -> dict[str, Any]:
        base = super().info()
        if self.supports_modules:
            base["modules"] = sorted(self.supports_modules)
        return base

    @abstractmethod
    def complete(self, *, module: str, prompt: str, parameters: dict | None = None) -> dict[str, Any]:
        """Text generation for research, script, SEO, and general LLM tasks."""


class ImageProvider(BaseProvider):
    capability = "image"

    @abstractmethod
    def generate(self, request: Any) -> Any:
        """Image generation."""


class VideoProvider(BaseProvider):
    capability = "video"

    @abstractmethod
    def generate(self, request: Any) -> Any:
        """Video generation."""


class VoiceProvider(BaseProvider):
    capability = "voice"

    @abstractmethod
    def generate(self, request: Any) -> Any:
        """Voice / TTS generation."""

    def preview(self, request: Any) -> Any:
        return self.generate(request)


class MusicProvider(BaseProvider):
    capability = "music"

    @abstractmethod
    def generate(self, request: Any) -> Any:
        """Music generation."""

    def preview(self, request: Any) -> Any:
        return self.generate(request)


class TranslationProvider(BaseProvider):
    capability = "translation"

    @abstractmethod
    def translate(self, request: Any) -> Any:
        """Text / subtitle translation."""


class EmbeddingsProvider(BaseProvider):
    capability = "embeddings"

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for one or more input strings."""


class VectorStoreProvider(BaseProvider):
    capability = "vectorstore"

    @abstractmethod
    def upsert(self, request: Any) -> Any:
        """Upsert vectors into a collection."""

    @abstractmethod
    def search(self, request: Any) -> Any:
        """Similarity search over a collection."""
