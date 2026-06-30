"""Demo translation provider — text + SRT/VTT upload."""

from __future__ import annotations

import uuid

from app.domain.storage.registry import upload_bytes
from app.domain.translation.providers.base import TranslationProvider
from app.domain.translation.translator import translate_text
from app.domain.translation.types import CONTENT_TYPES, TRANSLATION_LANGUAGES, TranslationRequest, TranslationResult
from app.domain.voice.subtitles import build_srt, build_vtt, estimate_duration

_LANG_CODES = {code for code, _ in TRANSLATION_LANGUAGES}


class DemoTranslationProvider(TranslationProvider):
    id = "demo"
    label = "Demo Translation Engine"

    def is_available(self) -> bool:
        return True

    def translate(self, request: TranslationRequest) -> TranslationResult:
        ctype = request.content_type if request.content_type in CONTENT_TYPES else "script"
        source = request.source_lang if request.source_lang in _LANG_CODES else "en"
        target = request.target_lang if request.target_lang in _LANG_CODES else "es"

        translated = request.meta.get("translated_override") or translate_text(request.source_text, source, target, ctype)
        duration = estimate_duration(translated)

        srt_content = None
        vtt_content = None
        srt_url = None
        vtt_url = None
        folder = request.project_id or "studio"

        if request.generate_srt and ctype in ("subtitles", "voice", "script"):
            srt_content = build_srt(translated, duration) if request.auto_sync else build_srt(translated, duration)
            srt_key = f"ai-translation/{folder}/{uuid.uuid4().hex}.srt"
            srt_up = upload_bytes(srt_key, srt_content.encode("utf-8"), "text/plain")
            srt_url = srt_up.url

        if request.generate_vtt and ctype in ("subtitles", "voice", "script"):
            vtt_content = build_vtt(translated, duration)
            vtt_key = f"ai-translation/{folder}/{uuid.uuid4().hex}.vtt"
            vtt_up = upload_bytes(vtt_key, vtt_content.encode("utf-8"), "text/vtt")
            vtt_url = vtt_up.url

        primary_url = srt_url or vtt_url

        return TranslationResult(
            output_text=f"Translated {ctype} from {source} → {target}",
            translated_text=translated,
            result_url=primary_url,
            srt_content=srt_content,
            vtt_content=vtt_content,
            srt_url=srt_url,
            vtt_url=vtt_url,
            provider=self.id,
            meta={
                "content_type": ctype,
                "source_lang": source,
                "target_lang": target,
                "auto_sync": request.auto_sync,
                "duration_seconds": duration,
                "simulated": True,
            },
        )
