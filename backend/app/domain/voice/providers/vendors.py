"""Cloud TTS / voice generation providers."""

from __future__ import annotations

import logging
import uuid

from app.core.config import get_settings
from app.domain.storage.registry import upload_bytes
from app.domain.voice.providers.base import VoiceProvider
from app.domain.voice.providers.demo import DemoVoiceProvider
from app.domain.voice.providers.voice_client import (
    language_to_bcp47,
    synthesize_azure_speech,
    synthesize_cartesia,
    synthesize_elevenlabs,
    synthesize_google_tts,
    synthesize_openai_tts,
    synthesize_playht,
    upload_audio_bytes,
)
from app.domain.voice.subtitles import build_srt, build_vtt, estimate_duration
from app.domain.voice.translation import demo_translate
from app.domain.voice.types import VOICE_LANGUAGES, VoiceGenerateRequest, VoiceGenerateResult

logger = logging.getLogger("untold.voice")

_LANG_CODES = {code for code, _ in VOICE_LANGUAGES}


class _BaseCloudVoiceProvider(VoiceProvider):
    def _prepare_text(self, request: VoiceGenerateRequest) -> tuple[str, str | None, str]:
        language = request.language if request.language in _LANG_CODES else "en"
        narration = request.text.strip()
        translated = None
        subtitle_text = narration
        if request.translate_to and request.translate_to in _LANG_CODES and request.translate_to != language:
            translated = demo_translate(narration, language, request.translate_to)
            subtitle_text = translated
        return narration, translated, subtitle_text

    def _finish(
        self,
        request: VoiceGenerateRequest,
        audio_bytes: bytes,
        mime_type: str,
        narration: str,
        subtitle_text: str,
        translated: str | None,
        **meta,
    ) -> VoiceGenerateResult:
        uploaded = upload_audio_bytes(audio_bytes, mime_type, project_id=request.project_id)
        duration = estimate_duration(narration, request.speed)

        srt_content = None
        vtt_content = None
        subtitles_url = None
        if request.sync_subtitles:
            srt_content = build_srt(subtitle_text, duration, request.speed)
            vtt_content = build_vtt(subtitle_text, duration)
            folder = request.project_id or "studio"
            srt_key = f"ai-voice/{folder}/{uuid.uuid4().hex}.srt"
            srt_up = upload_bytes(srt_key, srt_content.encode("utf-8"), "text/plain")
            subtitles_url = srt_up.url

        return VoiceGenerateResult(
            output_text=narration,
            result_url=uploaded["url"],
            r2_key=uploaded["key"],
            mime_type=mime_type,
            duration_seconds=duration,
            provider=self.id,
            subtitles_url=subtitles_url,
            subtitles_srt=srt_content,
            subtitles_vtt=vtt_content,
            translated_text=translated,
            meta={
                "language": request.language,
                "emotion": request.emotion,
                "pitch": request.pitch,
                "speed": request.speed,
                "voice_id": request.voice_id,
                "translate_to": request.translate_to,
                "sync_subtitles": request.sync_subtitles,
                "duration_seconds": duration,
                **meta,
            },
        )

    def _fallback(self, request: VoiceGenerateRequest, error: str) -> VoiceGenerateResult:
        logger.warning("%s failed (%s), using demo fallback", self.id, error)
        result = DemoVoiceProvider().generate(request)
        result.meta = dict(result.meta or {})
        result.meta["fallback"] = True
        result.meta["error"] = error
        result.meta["requested_provider"] = self.id
        return result


class ElevenLabsProvider(_BaseCloudVoiceProvider):
    id = "elevenlabs"
    label = "ElevenLabs"

    def is_available(self) -> bool:
        return bool(get_settings().elevenlabs_api_key)

    def generate(self, request: VoiceGenerateRequest) -> VoiceGenerateResult:
        s = get_settings()
        narration, translated, subtitle_text = self._prepare_text(request)
        voice_id = request.voice_id if request.voice_id and len(request.voice_id) > 10 else s.elevenlabs_voice_id
        try:
            audio, mime = synthesize_elevenlabs(
                api_key=s.elevenlabs_api_key or "",
                voice_id=voice_id,
                text=narration,
                model_id=s.elevenlabs_model,
            )
            return self._finish(
                request, audio, mime, narration, subtitle_text, translated,
                model=s.elevenlabs_model, elevenlabs_voice_id=voice_id,
            )
        except Exception as exc:
            return self._fallback(request, str(exc))


class OpenAITTSProvider(_BaseCloudVoiceProvider):
    id = "openai_tts"
    label = "OpenAI TTS"

    def is_available(self) -> bool:
        return bool(get_settings().openai_api_key)

    def generate(self, request: VoiceGenerateRequest) -> VoiceGenerateResult:
        s = get_settings()
        narration, translated, subtitle_text = self._prepare_text(request)
        voice = s.openai_tts_voice
        try:
            audio, mime = synthesize_openai_tts(
                api_key=s.openai_api_key or "",
                text=narration,
                model=s.openai_tts_model,
                voice=voice,
                speed=request.speed,
            )
            return self._finish(
                request, audio, mime, narration, subtitle_text, translated,
                model=s.openai_tts_model, openai_voice=voice,
            )
        except Exception as exc:
            return self._fallback(request, str(exc))


class AzureSpeechProvider(_BaseCloudVoiceProvider):
    id = "azure_speech"
    label = "Azure Speech"

    def is_available(self) -> bool:
        s = get_settings()
        return bool(s.azure_speech_key and s.azure_speech_region)

    def generate(self, request: VoiceGenerateRequest) -> VoiceGenerateResult:
        s = get_settings()
        narration, translated, subtitle_text = self._prepare_text(request)
        voice = request.voice_id if "-" in request.voice_id else s.azure_speech_voice
        try:
            audio, mime = synthesize_azure_speech(
                api_key=s.azure_speech_key or "",
                region=s.azure_speech_region,
                text=narration,
                voice=voice,
                language=language_to_bcp47(request.language),
                speed=request.speed,
                pitch=request.pitch,
            )
            return self._finish(
                request, audio, mime, narration, subtitle_text, translated,
                azure_voice=voice,
            )
        except Exception as exc:
            return self._fallback(request, str(exc))


class GoogleTTSProvider(_BaseCloudVoiceProvider):
    id = "google_tts"
    label = "Google TTS"

    def is_available(self) -> bool:
        s = get_settings()
        return bool(s.google_tts_api_key or s.gemini_api_key)

    def generate(self, request: VoiceGenerateRequest) -> VoiceGenerateResult:
        s = get_settings()
        api_key = s.google_tts_api_key or s.gemini_api_key or ""
        narration, translated, subtitle_text = self._prepare_text(request)
        bcp47 = language_to_bcp47(request.language)
        try:
            audio, mime = synthesize_google_tts(
                api_key=api_key,
                text=narration,
                language_code=bcp47,
                voice_name=s.google_tts_voice,
                speaking_rate=request.speed,
                pitch=(request.pitch - 1.0) * 10,
            )
            return self._finish(
                request, audio, mime, narration, subtitle_text, translated,
                google_voice=s.google_tts_voice,
            )
        except Exception as exc:
            return self._fallback(request, str(exc))


class CartesiaProvider(_BaseCloudVoiceProvider):
    id = "cartesia"
    label = "Cartesia"

    def is_available(self) -> bool:
        return bool(get_settings().cartesia_api_key)

    def generate(self, request: VoiceGenerateRequest) -> VoiceGenerateResult:
        s = get_settings()
        narration, translated, subtitle_text = self._prepare_text(request)
        voice_id = request.voice_id if len(request.voice_id) > 20 else s.cartesia_voice_id
        try:
            audio, mime = synthesize_cartesia(
                api_key=s.cartesia_api_key or "",
                text=narration,
                voice_id=voice_id,
                model_id=s.cartesia_model,
                language=request.language,
            )
            return self._finish(
                request, audio, mime, narration, subtitle_text, translated,
                cartesia_voice_id=voice_id,
            )
        except Exception as exc:
            return self._fallback(request, str(exc))


class PlayHTProvider(_BaseCloudVoiceProvider):
    id = "playht"
    label = "PlayHT"

    def is_available(self) -> bool:
        s = get_settings()
        return bool(s.playht_api_key and s.playht_user_id)

    def generate(self, request: VoiceGenerateRequest) -> VoiceGenerateResult:
        s = get_settings()
        narration, translated, subtitle_text = self._prepare_text(request)
        voice_id = request.voice_id if request.voice_id.startswith("s3://") or "/" in request.voice_id else s.playht_voice_id
        try:
            audio, mime = synthesize_playht(
                api_key=s.playht_api_key or "",
                user_id=s.playht_user_id or "",
                text=narration,
                voice_id=voice_id,
            )
            return self._finish(
                request, audio, mime, narration, subtitle_text, translated,
                playht_voice_id=voice_id,
            )
        except Exception as exc:
            return self._fallback(request, str(exc))


CLOUD_VOICE_PROVIDER_CLASSES: list[type[_BaseCloudVoiceProvider]] = [
    ElevenLabsProvider,
    OpenAITTSProvider,
    AzureSpeechProvider,
    GoogleTTSProvider,
    CartesiaProvider,
    PlayHTProvider,
]


def get_cloud_voice_providers() -> list[VoiceProvider]:
    return [cls() for cls in CLOUD_VOICE_PROVIDER_CLASSES]
