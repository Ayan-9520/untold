"""Embeddings provider registry."""

from __future__ import annotations

from app.domain.embeddings.providers.base import EmbeddingsProvider


class EmbeddingsProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, EmbeddingsProvider] = {}

    def register(self, provider: EmbeddingsProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [p.info() for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> EmbeddingsProvider:
        from app.ai.adapters.legacy_registry import resolve_capability

        return resolve_capability("embeddings", preferred)

    def embed(self, texts: list[str], provider_id: str | None = None) -> list[list[float]]:
        from app.ai.runtime.invoke import embed_texts

        return embed_texts(texts, provider_id)


_registry: EmbeddingsProviderRegistry | None = None


def get_embeddings_registry() -> EmbeddingsProviderRegistry:
    global _registry
    if _registry is None:
        from app.ai.adapters.legacy_registry import sync_legacy_registry

        _registry = EmbeddingsProviderRegistry()
        sync_legacy_registry(_registry, "embeddings")
    return _registry
