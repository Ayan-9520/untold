"""Single capability-based AI provider registry."""

from __future__ import annotations

import logging
from typing import Any

from app.ai.config import get_ai_config
from app.ai.providers.base import CAPABILITIES

logger = logging.getLogger("untold.ai.capability_registry")

_MEDIA_MODULES = frozenset({"image", "video", "thumbnail"})

_CAPABILITY_ENABLED_ATTR = {
    "llm": "enabled_providers",
    "image": "image_enabled_providers",
    "video": "video_enabled_providers",
    "voice": "voice_enabled_providers",
    "music": "music_enabled_providers",
    "translation": "translation_enabled_providers",
    "embeddings": "embeddings_enabled_providers",
    "vectorstore": "vectorstore_enabled_providers",
}


class CapabilityRegistry:
    """Canonical registry for all AI capabilities and provider instances."""

    def __init__(self) -> None:
        self._providers: dict[str, dict[str, Any]] = {cap: {} for cap in CAPABILITIES}

    def register(self, capability: str, provider: Any) -> None:
        if capability not in self._providers:
            raise ValueError(f"Unknown capability: {capability}")
        pid = getattr(provider, "id", None)
        if not pid:
            raise ValueError("Provider must have an id")
        self._providers[capability][pid] = provider
        logger.debug("Registered %s provider %s", capability, pid)

    def get(self, capability: str, provider_id: str) -> Any | None:
        return self._providers.get(capability, {}).get(provider_id)

    def providers_for(self, capability: str) -> dict[str, Any]:
        return dict(self._providers.get(capability, {}))

    def list_providers(self, capability: str) -> list[dict]:
        items: list[dict] = []
        for provider in self._providers.get(capability, {}).values():
            if hasattr(provider, "info"):
                items.append(provider.info())
            else:
                items.append(
                    {
                        "id": provider.id,
                        "label": getattr(provider, "label", provider.id),
                        "available": provider.is_available() if hasattr(provider, "is_available") else True,
                    }
                )
        return items

    def _enabled_set(self, capability: str) -> set[str]:
        cfg = get_ai_config()
        attr = _CAPABILITY_ENABLED_ATTR.get(capability, "enabled_providers")
        raw = getattr(cfg, attr, cfg.enabled_providers)
        return {x.strip() for x in raw if x.strip()}

    def _resolution_order(self, capability: str, preferred: str | None) -> list[str]:
        cfg = get_ai_config()
        enabled = self._enabled_set(capability)
        order: list[str] = []
        if preferred and preferred in enabled:
            order.append(preferred)
        default = cfg.default_for(capability)
        if default in enabled:
            order.append(default)
        order.extend(sorted(enabled))
        if capability == "llm":
            order.extend(["media_stub", "demo"])
        else:
            order.append("demo")
        return order

    def resolve(self, capability: str, preferred: str | None = None, *, module: str | None = None) -> Any:
        providers = self._providers.get(capability, {})
        seen: set[str] = set()
        cfg = get_ai_config()
        from app.core.config import get_settings

        settings = get_settings()
        demo_ids = {"demo", "media_stub"}

        for pid in self._resolution_order(capability, preferred):
            if pid in seen:
                continue
            seen.add(pid)
            if settings.is_production and not settings.ai_allow_demo_in_production and pid in demo_ids:
                continue
            provider = providers.get(pid)
            if not provider:
                continue
            if hasattr(provider, "is_available") and not provider.is_available():
                continue
            if capability == "llm" and module:
                if hasattr(provider, "supports") and not provider.supports(module):
                    continue
                if hasattr(provider, "supports_modules") and provider.supports_modules:
                    if module not in provider.supports_modules and module not in _MEDIA_MODULES:
                        continue
            return provider

        raise RuntimeError(f"No provider available for capability '{capability}'")


_registry: CapabilityRegistry | None = None


def get_capability_registry() -> CapabilityRegistry:
    global _registry
    if _registry is None:
        _registry = CapabilityRegistry()
    return _registry
