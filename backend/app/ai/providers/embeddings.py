"""Embeddings providers — facade to embeddings registry."""

from __future__ import annotations


def list_embeddings_providers() -> list[dict]:
    from app.domain.embeddings.providers.registry import get_embeddings_registry

    return get_embeddings_registry().list_providers()


def embed_texts(texts: list[str], provider_id: str | None = None) -> list[list[float]]:
    from app.domain.embeddings.providers.registry import get_embeddings_registry

    return get_embeddings_registry().embed(texts, provider_id)
