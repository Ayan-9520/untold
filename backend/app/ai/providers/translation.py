"""Translation providers — facade to translation studio registry."""

from __future__ import annotations

from app.ai.providers.base import TranslationProvider as BaseTranslationProvider
from app.domain.translation.types import TranslationRequest


class TranslationRegistryAdapter(BaseTranslationProvider):
    id = "translation_registry"
    label = "Translation Studio Registry"

    def is_available(self) -> bool:
        from app.domain.translation.providers.registry import get_translation_registry

        return bool(get_translation_registry().list_providers())

    def translate(self, request: TranslationRequest, provider_id: str | None = None):
        from app.domain.translation.providers.registry import get_translation_registry

        return get_translation_registry().translate(request, provider_id)


def list_translation_providers() -> list[dict]:
    from app.domain.translation.providers.registry import get_translation_registry

    return get_translation_registry().list_providers()


def translate(request: TranslationRequest, provider_id: str | None = None):
    from app.domain.translation.providers.registry import get_translation_registry

    return get_translation_registry().translate(request, provider_id)
