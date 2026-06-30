"""Unified AI provider registry."""

from __future__ import annotations

from typing import Any

from app.ai.bootstrap import ensure_bootstrapped
from app.ai.capability_registry import get_capability_registry
from app.ai.config import get_ai_config
from app.ai.providers.base import CAPABILITIES
from app.ai.providers.factory import get_provider_factory
from app.ai.runtime.invoke import embed_texts, invoke_llm
from app.domain.ai.providers.registry import ProviderRegistry as LegacyLLMRegistry
from app.domain.ai.providers.registry import get_provider_registry
from app.domain.ai.types import AIJobRequest, AIJobResult


class AIRegistry:
    """Central registry for all UNTOLD AI capabilities and providers."""

    def __init__(self) -> None:
        self._factory = get_provider_factory()
        self._legacy_llm = get_provider_registry()

    def list_capabilities(self) -> list[dict]:
        ensure_bootstrapped()
        cfg = get_ai_config()
        reg = get_capability_registry()
        return [
            {
                "id": cap,
                "default_provider": cfg.default_for(cap),
                "providers": reg.list_providers(cap),
            }
            for cap in CAPABILITIES
        ]

    def list_providers(self, capability: str) -> list[dict]:
        ensure_bootstrapped()
        return get_capability_registry().list_providers(capability)

    def resolve_llm(self, module: str, preferred: str | None = None) -> Any:
        return self._legacy_llm.resolve(module, preferred)

    def generate_llm(self, request: AIJobRequest, provider_id: str | None = None) -> AIJobResult:
        return invoke_llm(request, provider_id)

    def embed(self, texts: list[str], provider_id: str | None = None) -> list[list[float]]:
        return embed_texts(texts, provider_id)

    def upsert_vectors(self, request, provider_id: str | None = None):
        return self._factory.upsert_vectors(request, provider_id)

    def search_vectors(self, request, provider_id: str | None = None):
        return self._factory.search_vectors(request, provider_id)

    def overview(self) -> dict:
        cfg = get_ai_config()
        return {
            "config": {
                "default_provider": cfg.default_provider,
                "enabled_providers": list(cfg.enabled_providers),
                "openai_configured": bool(cfg.openai_api_key),
                "openai_model": cfg.openai_model,
                "embeddings_model": cfg.embeddings_model,
            },
            "capabilities": self.list_capabilities(),
        }


_registry: AIRegistry | None = None


def get_ai_registry() -> AIRegistry:
    global _registry
    if _registry is None:
        _registry = AIRegistry()
    return _registry


def bootstrap_legacy_llm_registry(registry: LegacyLLMRegistry) -> None:
    """Backward-compatible hook for tests and legacy bootstrap paths."""
    from app.ai.adapters.legacy_registry import sync_legacy_registry

    sync_legacy_registry(registry, "llm")
