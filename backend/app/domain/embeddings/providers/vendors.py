"""Cloud embeddings providers."""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.domain.embeddings.providers.base import EmbeddingsProvider
from app.domain.embeddings.providers.demo import DemoEmbeddingsProvider
from app.domain.embeddings.providers.embeddings_client import (
    embed_bge_hf,
    embed_bge_openai_compatible,
    embed_cohere,
    embed_gemini,
    embed_jina,
    embed_openai,
    embed_voyage,
)

logger = logging.getLogger("untold.embeddings")


class _BaseCloudEmbeddingsProvider(EmbeddingsProvider):
    def _fallback(self, texts: list[str], error: str) -> list[list[float]]:
        logger.warning("%s embeddings failed (%s), using demo vectors", self.id, error)
        vectors = DemoEmbeddingsProvider().embed(texts)
        return vectors


class OpenAIEmbeddingsProvider(_BaseCloudEmbeddingsProvider):
    id = "openai"
    label = "OpenAI Embeddings"

    def is_available(self) -> bool:
        return bool(get_settings().openai_api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        s = get_settings()
        try:
            return embed_openai(
                api_key=s.openai_api_key or "",
                model=s.openai_embeddings_model,
                texts=texts,
            )
        except Exception as exc:
            return self._fallback(texts, str(exc))


class VoyageEmbeddingsProvider(_BaseCloudEmbeddingsProvider):
    id = "voyage"
    label = "Voyage AI"

    def is_available(self) -> bool:
        return bool(get_settings().voyage_api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        s = get_settings()
        try:
            return embed_voyage(
                api_key=s.voyage_api_key or "",
                model=s.voyage_embeddings_model,
                texts=texts,
            )
        except Exception as exc:
            return self._fallback(texts, str(exc))


class CohereEmbeddingsProvider(_BaseCloudEmbeddingsProvider):
    id = "cohere"
    label = "Cohere"

    def is_available(self) -> bool:
        return bool(get_settings().cohere_api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        s = get_settings()
        try:
            return embed_cohere(
                api_key=s.cohere_api_key or "",
                model=s.cohere_embeddings_model,
                texts=texts,
            )
        except Exception as exc:
            return self._fallback(texts, str(exc))


class GeminiEmbeddingsProvider(_BaseCloudEmbeddingsProvider):
    id = "gemini"
    label = "Gemini Embeddings"

    def is_available(self) -> bool:
        return bool(get_settings().gemini_api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        s = get_settings()
        try:
            return embed_gemini(
                api_key=s.gemini_api_key or "",
                model=s.gemini_embeddings_model,
                texts=texts,
            )
        except Exception as exc:
            return self._fallback(texts, str(exc))


class JinaEmbeddingsProvider(_BaseCloudEmbeddingsProvider):
    id = "jina"
    label = "Jina AI"

    def is_available(self) -> bool:
        return bool(get_settings().jina_api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        s = get_settings()
        try:
            return embed_jina(
                api_key=s.jina_api_key or "",
                model=s.jina_embeddings_model,
                texts=texts,
            )
        except Exception as exc:
            return self._fallback(texts, str(exc))


class BGEEmbeddingsProvider(_BaseCloudEmbeddingsProvider):
    id = "bge"
    label = "BGE"

    def is_available(self) -> bool:
        s = get_settings()
        return bool(s.bge_api_base_url or s.huggingface_api_token)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        s = get_settings()
        try:
            if s.bge_api_base_url:
                return embed_bge_openai_compatible(
                    base_url=s.bge_api_base_url,
                    model=s.bge_model,
                    texts=texts,
                    api_key=s.bge_api_key,
                )
            return embed_bge_hf(
                api_token=s.huggingface_api_token or "",
                model=s.bge_model,
                texts=texts,
            )
        except Exception as exc:
            return self._fallback(texts, str(exc))


CLOUD_EMBEDDINGS_PROVIDER_CLASSES: list[type[_BaseCloudEmbeddingsProvider]] = [
    OpenAIEmbeddingsProvider,
    VoyageEmbeddingsProvider,
    CohereEmbeddingsProvider,
    GeminiEmbeddingsProvider,
    JinaEmbeddingsProvider,
    BGEEmbeddingsProvider,
]


def get_cloud_embeddings_providers() -> list[EmbeddingsProvider]:
    return [cls() for cls in CLOUD_EMBEDDINGS_PROVIDER_CLASSES]
