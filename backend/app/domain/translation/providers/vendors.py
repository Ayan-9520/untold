"""Cloud translation providers."""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.domain.translation.providers.base import TranslationProvider
from app.domain.translation.providers.demo import DemoTranslationProvider
from app.domain.translation.providers.translation_client import (
    aws_translate_available,
    finish_translation,
    normalize_langs,
    plain_source_text,
    translate_aws,
    translate_azure,
    translate_deepl,
    translate_gemini_llm,
    translate_google,
    translate_openai_llm,
)
from app.domain.translation.types import TranslationRequest, TranslationResult

logger = logging.getLogger("untold.translation")


class _BaseCloudTranslationProvider(TranslationProvider):
    def _source(self, request: TranslationRequest) -> tuple[str, str, str, str]:
        ctype, source, target = normalize_langs(request)
        text = plain_source_text(request.source_text, ctype)
        return ctype, source, target, text

    def translate(self, request: TranslationRequest) -> TranslationResult:
        override = request.meta.get("translated_override")
        if override:
            return self._finish(request, override, tm_hit=True)
        return self._translate_cloud(request)

    def _translate_cloud(self, request: TranslationRequest) -> TranslationResult:
        raise NotImplementedError

    def _finish(self, request: TranslationRequest, translated: str, **meta) -> TranslationResult:
        return finish_translation(request, translated, provider_id=self.id, extra_meta=meta)

    def _fallback(self, request: TranslationRequest, error: str) -> TranslationResult:
        logger.warning("%s failed (%s), using demo fallback", self.id, error)
        result = DemoTranslationProvider().translate(request)
        result.meta = dict(result.meta or {})
        result.meta["fallback"] = True
        result.meta["error"] = error
        result.meta["requested_provider"] = self.id
        return result


class GoogleTranslateProvider(_BaseCloudTranslationProvider):
    id = "google"
    label = "Google Translate"

    def is_available(self) -> bool:
        return bool(get_settings().google_translate_api_key)

    def _translate_cloud(self, request: TranslationRequest) -> TranslationResult:
        ctype, source, target, text = self._source(request)
        if not text.strip() or source == target:
            return self._finish(request, text)
        s = get_settings()
        try:
            translated = translate_google(
                api_key=s.google_translate_api_key or "",
                text=text,
                source_lang=source,
                target_lang=target,
            )
            return self._finish(request, translated, engine="google-cloud-translate-v2")
        except Exception as exc:
            return self._fallback(request, str(exc))


class DeepLProvider(_BaseCloudTranslationProvider):
    id = "deepl"
    label = "DeepL"

    def is_available(self) -> bool:
        return bool(get_settings().deepl_api_key)

    def _translate_cloud(self, request: TranslationRequest) -> TranslationResult:
        ctype, source, target, text = self._source(request)
        if not text.strip() or source == target:
            return self._finish(request, text)
        s = get_settings()
        try:
            translated = translate_deepl(
                api_key=s.deepl_api_key or "",
                base_url=s.deepl_api_base_url,
                text=text,
                source_lang=source,
                target_lang=target,
            )
            return self._finish(request, translated, engine="deepl-v2")
        except Exception as exc:
            return self._fallback(request, str(exc))


class OpenAITranslationProvider(_BaseCloudTranslationProvider):
    id = "openai"
    label = "OpenAI"

    def is_available(self) -> bool:
        return bool(get_settings().openai_api_key)

    def _translate_cloud(self, request: TranslationRequest) -> TranslationResult:
        ctype, source, target, text = self._source(request)
        if not text.strip() or source == target:
            return self._finish(request, text)
        s = get_settings()
        try:
            translated = translate_openai_llm(
                api_key=s.openai_api_key or "",
                model=s.translation_openai_model,
                text=text,
                source_lang=source,
                target_lang=target,
                content_type=ctype,
            )
            return self._finish(request, translated, model=s.translation_openai_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


class GeminiTranslationProvider(_BaseCloudTranslationProvider):
    id = "gemini"
    label = "Gemini"

    def is_available(self) -> bool:
        return bool(get_settings().gemini_api_key)

    def _translate_cloud(self, request: TranslationRequest) -> TranslationResult:
        ctype, source, target, text = self._source(request)
        if not text.strip() or source == target:
            return self._finish(request, text)
        s = get_settings()
        try:
            translated = translate_gemini_llm(
                api_key=s.gemini_api_key or "",
                model=s.translation_gemini_model,
                text=text,
                source_lang=source,
                target_lang=target,
                content_type=ctype,
            )
            return self._finish(request, translated, model=s.translation_gemini_model)
        except Exception as exc:
            return self._fallback(request, str(exc))


class AzureTranslatorProvider(_BaseCloudTranslationProvider):
    id = "azure"
    label = "Azure Translator"

    def is_available(self) -> bool:
        return bool(get_settings().azure_translator_api_key)

    def _translate_cloud(self, request: TranslationRequest) -> TranslationResult:
        ctype, source, target, text = self._source(request)
        if not text.strip() or source == target:
            return self._finish(request, text)
        s = get_settings()
        try:
            translated = translate_azure(
                api_key=s.azure_translator_api_key or "",
                region=s.azure_translator_region,
                text=text,
                source_lang=source,
                target_lang=target,
            )
            return self._finish(request, translated, engine="azure-translator-v3")
        except Exception as exc:
            return self._fallback(request, str(exc))


class AWSTranslateProvider(_BaseCloudTranslationProvider):
    id = "aws_translate"
    label = "AWS Translate"

    def is_available(self) -> bool:
        s = get_settings()
        if s.aws_access_key_id and s.aws_secret_access_key:
            return True
        return aws_translate_available(s.aws_translate_region)

    def _translate_cloud(self, request: TranslationRequest) -> TranslationResult:
        ctype, source, target, text = self._source(request)
        if not text.strip() or source == target:
            return self._finish(request, text)
        s = get_settings()
        try:
            translated = translate_aws(
                region=s.aws_translate_region,
                text=text,
                source_lang=source,
                target_lang=target,
            )
            return self._finish(request, translated, engine="aws-translate")
        except Exception as exc:
            return self._fallback(request, str(exc))


CLOUD_TRANSLATION_PROVIDER_CLASSES: list[type[_BaseCloudTranslationProvider]] = [
    GoogleTranslateProvider,
    DeepLProvider,
    OpenAITranslationProvider,
    GeminiTranslationProvider,
    AzureTranslatorProvider,
    AWSTranslateProvider,
]


def get_cloud_translation_providers() -> list[TranslationProvider]:
    return [cls() for cls in CLOUD_TRANSLATION_PROVIDER_CLASSES]
