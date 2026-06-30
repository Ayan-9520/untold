"""Demo translation engine with content-type awareness."""

from __future__ import annotations

from app.domain.translation.types import TRANSLATION_LANGUAGES

_LANG_LABELS = dict(TRANSLATION_LANGUAGES)

_PREFIX = {
    "script": "SCRIPT",
    "voice": "NARRATION",
    "subtitles": "SUB",
    "metadata": "META",
    "description": "DESC",
    "title": "TITLE",
}


def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
    content_type: str = "script",
) -> str:
    if not text.strip() or source_lang == target_lang:
        return text.strip()

    label = _LANG_LABELS.get(target_lang, target_lang.upper())
    prefix = _PREFIX.get(content_type, "TRANS")

    if content_type == "subtitles":
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().isdigit() and "-->" not in ln]
        if lines:
            return "\n".join(f"[{label}] {ln}" for ln in lines)
    if content_type == "title":
        return f"[{label}] {text.strip()[:120]}"
    if content_type == "metadata":
        return f"[{label} metadata] {text.strip()}"

    return f"[{label} · {prefix}] {text.strip()}"
