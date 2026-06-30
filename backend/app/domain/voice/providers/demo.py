"""Demo voice provider — WAV narration + synchronized subtitles."""

from __future__ import annotations

import uuid

from app.domain.storage.registry import upload_bytes
from app.domain.voice.providers.base import VoiceProvider
from app.domain.voice.subtitles import build_srt, build_vtt, estimate_duration
from app.domain.voice.translation import demo_translate
from app.domain.voice.types import VOICE_LANGUAGES, VoiceGenerateRequest, VoiceGenerateResult
from app.domain.voice.wav_builder import build_demo_wav

_LANG_CODES = {code for code, _ in VOICE_LANGUAGES}


class DemoVoiceProvider(VoiceProvider):
    id = "demo"
    label = "Demo Voice Generator (WAV)"

    def is_available(self) -> bool:
        return True

    def generate(self, request: VoiceGenerateRequest) -> VoiceGenerateResult:
        language = request.language if request.language in _LANG_CODES else "en"
        narration = request.text.strip()
        translated = None
        subtitle_text = narration

        if request.translate_to and request.translate_to in _LANG_CODES and request.translate_to != language:
            translated = demo_translate(narration, language, request.translate_to)
            subtitle_text = translated

        duration = estimate_duration(narration, request.speed)
        wav_bytes = build_demo_wav(
            duration,
            pitch=request.pitch,
            emotion=request.emotion,
        )

        folder = request.project_id or "studio"
        audio_key = f"ai-voice/{folder}/{uuid.uuid4().hex}.wav"
        uploaded = upload_bytes(audio_key, wav_bytes, "audio/wav")

        srt_content = None
        vtt_content = None
        subtitles_url = None
        if request.sync_subtitles:
            srt_content = build_srt(subtitle_text, duration, request.speed)
            vtt_content = build_vtt(subtitle_text, duration)
            srt_key = f"ai-voice/{folder}/{uuid.uuid4().hex}.srt"
            srt_up = upload_bytes(srt_key, srt_content.encode("utf-8"), "text/plain")
            subtitles_url = srt_up.url

        return VoiceGenerateResult(
            output_text=narration,
            result_url=uploaded.url,
            r2_key=uploaded.key,
            mime_type="audio/wav",
            duration_seconds=duration,
            provider=self.id,
            subtitles_url=subtitles_url,
            subtitles_srt=srt_content,
            subtitles_vtt=vtt_content,
            translated_text=translated,
            meta={
                "language": language,
                "emotion": request.emotion,
                "pitch": request.pitch,
                "speed": request.speed,
                "voice_id": request.voice_id,
                "translate_to": request.translate_to,
                "sync_subtitles": request.sync_subtitles,
                "duration_seconds": duration,
                "simulated": True,
            },
        )
