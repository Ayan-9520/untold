"""Provider factory — resolve capability backends by id."""

from __future__ import annotations

from typing import Any

from app.ai.bootstrap import ensure_bootstrapped
from app.ai.capability_registry import get_capability_registry
from app.ai.config import get_ai_config
from app.ai.providers.base import CAPABILITIES, LLMProvider
from app.ai.runtime.invoke import embed_texts, invoke_llm
from app.domain.ai.providers.llm_bridge import LLMProviderBridge
from app.domain.ai.types import AIJobRequest
from app.domain.embeddings.providers.registry import get_embeddings_registry
from app.domain.vectorstore.types import VectorSearchRequest, VectorUpsertRequest


class ProviderFactory:
    """Create and resolve providers across all AI capabilities."""

    def list_capabilities(self) -> list[str]:
        return list(CAPABILITIES)

    def list_llm_providers(self) -> list[dict]:
        ensure_bootstrapped()
        return get_capability_registry().list_providers("llm")

    def list_embeddings_providers(self) -> list[dict]:
        return get_embeddings_registry().list_providers()

    def resolve_llm(self, module: str, preferred: str | None = None) -> LLMProvider:
        ensure_bootstrapped()
        provider = get_capability_registry().resolve("llm", preferred, module=module)
        if isinstance(provider, LLMProviderBridge):
            return provider._inner
        from app.ai.providers.llm import get_llm_providers

        demo = next((p for p in get_llm_providers() if p.id == "demo"), None)
        if demo:
            return demo
        raise RuntimeError(f"No LLM provider available for module '{module}'")

    def resolve_embeddings(self, preferred: str | None = None):
        return get_embeddings_registry().resolve(preferred)

    def complete(
        self,
        *,
        module: str,
        prompt: str,
        parameters: dict | None = None,
        provider_id: str | None = None,
    ) -> dict[str, Any]:
        result = invoke_llm(
            AIJobRequest(module=module, prompt=prompt, parameters=parameters or {}),
            provider_id,
        )
        return {
            "output_text": result.output_text,
            "result_url": result.result_url,
            "meta": result.meta,
            "provider": result.provider,
        }

    def embed(self, texts: list[str], provider_id: str | None = None) -> list[list[float]]:
        return embed_texts(texts, provider_id)

    def list_vectorstore_providers(self) -> list[dict]:
        from app.domain.vectorstore.providers.registry import get_vectorstore_registry

        return get_vectorstore_registry().list_providers()

    def upsert_vectors(self, request: VectorUpsertRequest, provider_id: str | None = None):
        from app.domain.vectorstore.providers.registry import get_vectorstore_registry

        return get_vectorstore_registry().upsert(request, provider_id)

    def search_vectors(self, request: VectorSearchRequest, provider_id: str | None = None):
        from app.domain.vectorstore.providers.registry import get_vectorstore_registry

        return get_vectorstore_registry().search(request, provider_id)

    def get_domain_registry(self, capability: str) -> Any:
        """Return the studio-specific domain registry for media capabilities."""
        if capability == "image":
            from app.domain.image.providers.registry import get_image_registry
            return get_image_registry()
        if capability == "video":
            from app.domain.video.providers.registry import get_video_registry
            return get_video_registry()
        if capability == "voice":
            from app.domain.voice.providers.registry import get_voice_registry
            return get_voice_registry()
        if capability == "music":
            from app.domain.music.providers.registry import get_music_registry
            return get_music_registry()
        if capability == "translation":
            from app.domain.translation.providers.registry import get_translation_registry
            return get_translation_registry()
        raise ValueError(f"Unknown capability: {capability}")


_factory: ProviderFactory | None = None


def get_provider_factory() -> ProviderFactory:
    global _factory
    if _factory is None:
        _factory = ProviderFactory()
    return _factory
