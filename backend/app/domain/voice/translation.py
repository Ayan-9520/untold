"""Demo translation for voice narration (replace with LLM/TTS bridge in production)."""

from __future__ import annotations

_LANG_LABELS = {
    "en": "English",
    "hi": "Hindi",
    "ar": "Arabic",
    "es": "Spanish",
    "fr": "French",
    "ja": "Japanese",
}


def demo_translate(text: str, source_lang: str, target_lang: str) -> str:
    if not target_lang or target_lang == source_lang:
        return text
    label = _LANG_LABELS.get(target_lang, target_lang.upper())
    return f"[{label} narration] {text}"
