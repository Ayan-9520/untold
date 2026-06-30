"""Cloud translation API stub."""

from app.domain.translation.providers.base import TranslationProvider
from app.domain.translation.providers.demo import DemoTranslationProvider
from app.domain.translation.types import TranslationRequest, TranslationResult


class StubTranslationProvider(TranslationProvider):
    id = "translation_stub"
    label = "Cloud Translation API (configure keys)"

    def is_available(self) -> bool:
        return False

    def translate(self, request: TranslationRequest) -> TranslationResult:
        return DemoTranslationProvider().translate(request)
