"""Vector store providers — facade to vector store registry."""

from __future__ import annotations

from app.domain.vectorstore.types import VectorSearchRequest, VectorSearchResult, VectorUpsertRequest, VectorUpsertResult


def list_vectorstore_providers() -> list[dict]:
    from app.domain.vectorstore.providers.registry import get_vectorstore_registry

    return get_vectorstore_registry().list_providers()


def upsert_vectors(
    request: VectorUpsertRequest,
    provider_id: str | None = None,
) -> VectorUpsertResult:
    from app.domain.vectorstore.providers.registry import get_vectorstore_registry

    return get_vectorstore_registry().upsert(request, provider_id)


def search_vectors(
    request: VectorSearchRequest,
    provider_id: str | None = None,
) -> VectorSearchResult:
    from app.domain.vectorstore.providers.registry import get_vectorstore_registry

    return get_vectorstore_registry().search(request, provider_id)
