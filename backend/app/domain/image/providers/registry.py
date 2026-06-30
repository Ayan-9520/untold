"""Image generation provider registry."""

from __future__ import annotations

from app.domain.image.providers.base import ImageProvider
from app.domain.image.types import ImageGenerateRequest, ImageGenerateResult


class ImageProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ImageProvider] = {}

    def register(self, provider: ImageProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [{"id": p.id, "label": p.label, "available": p.is_available()} for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> ImageProvider:
        from app.ai.adapters.legacy_registry import resolve_capability

        return resolve_capability("image", preferred)

    def generate(self, request: ImageGenerateRequest, provider_id: str | None = None) -> ImageGenerateResult:
        from app.ai.runtime.invoke import invoke_provider_method

        return invoke_provider_method(
            "image",
            "generate",
            request,
            provider_id,
            prompt_for_cost=request.prompt,
        )


_registry: ImageProviderRegistry | None = None


def get_image_registry() -> ImageProviderRegistry:
    global _registry
    if _registry is None:
        from app.ai.adapters.legacy_registry import sync_legacy_registry

        _registry = ImageProviderRegistry()
        sync_legacy_registry(_registry, "image")
    return _registry
