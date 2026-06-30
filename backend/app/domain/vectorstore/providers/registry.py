"""Vector store provider registry."""

from __future__ import annotations

from app.domain.vectorstore.providers.base import VectorStoreProvider
from app.domain.vectorstore.types import VectorSearchRequest, VectorSearchResult, VectorUpsertRequest, VectorUpsertResult


class VectorStoreProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, VectorStoreProvider] = {}

    def register(self, provider: VectorStoreProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [p.info() for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> VectorStoreProvider:
        from app.ai.adapters.legacy_registry import resolve_capability

        return resolve_capability("vectorstore", preferred)

    def upsert(self, request: VectorUpsertRequest, provider_id: str | None = None) -> VectorUpsertResult:
        from app.ai.runtime.invoke import invoke_provider_method

        return invoke_provider_method("vectorstore", "upsert", request, provider_id)

    def search(self, request: VectorSearchRequest, provider_id: str | None = None) -> VectorSearchResult:
        from app.ai.runtime.invoke import invoke_provider_method

        return invoke_provider_method("vectorstore", "search", request, provider_id)


_registry: VectorStoreProviderRegistry | None = None


def get_vectorstore_registry() -> VectorStoreProviderRegistry:
    global _registry
    if _registry is None:
        from app.ai.adapters.legacy_registry import sync_legacy_registry

        _registry = VectorStoreProviderRegistry()
        sync_legacy_registry(_registry, "vectorstore")
    return _registry
