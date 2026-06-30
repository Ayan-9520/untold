"""Shared translation HTTP clients."""

from __future__ import annotations

import logging
import re
import uuid
from typing import Callable

import httpx

from app.domain.storage.registry import upload_bytes
from app.domain.translation.types import CONTENT_TYPES, TRANSLATION_LANGUAGES, TranslationRequest, TranslationResult
from app.domain.voice.subtitles import build_srt, build_vtt, estimate_duration

logger = logging.getLogger("untold.translation_client")

_LANG_CODES = {code for code, _ in TRANSLATION_LANGUAGES}

_DEEPL_LANG_MAP = {
    "en": "EN",
    "de": "DE",
    "fr": "FR",
    "es": "ES",
    "pt": "PT-BR",
    "ja": "JA",
    "zh": "ZH",
    "ru": "RU",
    "ar": "AR",
    "hi": "HI",
}


def normalize_langs(request: TranslationRequest) -> tuple[str, str, str]:
    ctype = request.content_type if request.content_type in CONTENT_TYPES else "script"
    source = request.source_lang if request.source_lang in _LANG_CODES else "en"
    target = request.target_lang if request.target_lang in _LANG_CODES else "es"
    return ctype, source, target


def plain_source_text(text: str, content_type: str) -> str:
    if content_type != "subtitles":
        return text.strip()
    lines: list[str] = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s.isdigit() or "-->" in s:
            continue
        lines.append(s)
    return "\n".join(lines) if lines else text.strip()


def llm_translation_prompt(
    text: str,
    *,
    source_lang: str,
    target_lang: str,
    content_type: str,
) -> str:
    return (
        f"Translate this {content_type} from {source_lang} to {target_lang}.\n"
        "Preserve line breaks and tone suitable for film/documentary production.\n"
        "Return only the translated text with no commentary.\n\n"
        f"{text}"
    )


def finish_translation(
    request: TranslationRequest,
    translated: str,
    *,
    provider_id: str,
    extra_meta: dict | None = None,
) -> TranslationResult:
    ctype, source, target = normalize_langs(request)
    duration = estimate_duration(translated)

    srt_content = None
    vtt_content = None
    srt_url = None
    vtt_url = None
    folder = request.project_id or "studio"

    if request.generate_srt and ctype in ("subtitles", "voice", "script"):
        srt_content = build_srt(translated, duration)
        srt_key = f"ai-translation/{folder}/{uuid.uuid4().hex}.srt"
        srt_up = upload_bytes(srt_key, srt_content.encode("utf-8"), "text/plain")
        srt_url = srt_up.url

    if request.generate_vtt and ctype in ("subtitles", "voice", "script"):
        vtt_content = build_vtt(translated, duration)
        vtt_key = f"ai-translation/{folder}/{uuid.uuid4().hex}.vtt"
        vtt_up = upload_bytes(vtt_key, vtt_content.encode("utf-8"), "text/vtt")
        vtt_url = vtt_up.url

    meta = {
        "content_type": ctype,
        "source_lang": source,
        "target_lang": target,
        "auto_sync": request.auto_sync,
        "duration_seconds": duration,
        **(extra_meta or {}),
    }

    return TranslationResult(
        output_text=f"Translated {ctype} from {source} → {target}",
        translated_text=translated,
        result_url=srt_url or vtt_url,
        srt_content=srt_content,
        vtt_content=vtt_content,
        srt_url=srt_url,
        vtt_url=vtt_url,
        provider=provider_id,
        meta=meta,
    )


def translate_google(
    *,
    api_key: str,
    text: str,
    source_lang: str,
    target_lang: str,
    timeout: float = 60.0,
) -> str:
    params = {
        "q": text,
        "target": target_lang,
        "format": "text",
        "key": api_key,
    }
    if source_lang:
        params["source"] = source_lang
    with httpx.Client(timeout=timeout) as client:
        resp = client.post("https://translation.googleapis.com/language/translate/v2", params=params)
        resp.raise_for_status()
        data = resp.json()
    translations = (data.get("data") or {}).get("translations") or []
    if not translations:
        raise RuntimeError("Google Translate returned no translations")
    return translations[0].get("translatedText", "").strip()


def translate_deepl(
    *,
    api_key: str,
    base_url: str,
    text: str,
    source_lang: str,
    target_lang: str,
    timeout: float = 60.0,
) -> str:
    target = _DEEPL_LANG_MAP.get(target_lang, target_lang.upper())
    source = _DEEPL_LANG_MAP.get(source_lang, source_lang.upper()) if source_lang else None
    payload: dict = {
        "text": [text],
        "target_lang": target,
    }
    if source:
        payload["source_lang"] = source
    headers = {"Authorization": f"DeepL-Auth-Key {api_key}", "Content-Type": "application/json"}
    url = f"{base_url.rstrip('/')}/v2/translate"
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    translations = data.get("translations") or []
    if not translations:
        raise RuntimeError("DeepL returned no translations")
    return translations[0].get("text", "").strip()


def translate_azure(
    *,
    api_key: str,
    region: str,
    text: str,
    source_lang: str,
    target_lang: str,
    timeout: float = 60.0,
) -> str:
    params = {"api-version": "3.0", "to": target_lang}
    if source_lang:
        params["from"] = source_lang
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/json",
    }
    if region and region != "global":
        headers["Ocp-Apim-Subscription-Region"] = region
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            "https://api.cognitive.microsofttranslator.com/translate",
            params=params,
            headers=headers,
            json=[{"text": text}],
        )
        resp.raise_for_status()
        data = resp.json()
    if not data or not data[0].get("translations"):
        raise RuntimeError("Azure Translator returned no translations")
    return data[0]["translations"][0]["text"].strip()


def translate_aws(
    *,
    region: str,
    text: str,
    source_lang: str,
    target_lang: str,
) -> str:
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("boto3 required for AWS Translate") from exc

    client = boto3.client("translate", region_name=region)
    kwargs: dict = {
        "Text": text,
        "SourceLanguageCode": source_lang,
        "TargetLanguageCode": target_lang,
    }
    result = client.translate_text(**kwargs)
    translated = result.get("TranslatedText", "").strip()
    if not translated:
        raise RuntimeError("AWS Translate returned empty text")
    return translated


def translate_openai_llm(
    *,
    api_key: str,
    model: str,
    text: str,
    source_lang: str,
    target_lang: str,
    content_type: str,
    timeout: float = 90.0,
) -> str:
    from app.ai.providers.llm_client import chat_openai_compatible, system_prompt_for

    prompt = llm_translation_prompt(
        text,
        source_lang=source_lang,
        target_lang=target_lang,
        content_type=content_type,
    )
    return chat_openai_compatible(
        url="https://api.openai.com/v1/chat/completions",
        api_key=api_key,
        model=model,
        user_prompt=prompt,
        system=system_prompt_for("translation"),
        timeout=timeout,
    )


def translate_gemini_llm(
    *,
    api_key: str,
    model: str,
    text: str,
    source_lang: str,
    target_lang: str,
    content_type: str,
    timeout: float = 90.0,
) -> str:
    from app.ai.providers.llm_client import chat_gemini, system_prompt_for

    prompt = llm_translation_prompt(
        text,
        source_lang=source_lang,
        target_lang=target_lang,
        content_type=content_type,
    )
    return chat_gemini(
        api_key=api_key,
        model=model,
        user_prompt=prompt,
        system=system_prompt_for("translation"),
        timeout=timeout,
    )


def aws_translate_available(region: str) -> bool:
    try:
        import boto3

        client = boto3.client("translate", region_name=region)
        client.list_languages(MaxResults=1)
        return True
    except Exception:
        return False


def split_subtitle_lines(text: str) -> list[str]:
    if not text.strip():
        return []
    if content_type_subtitles(text):
        return [ln.strip() for ln in plain_source_text(text, "subtitles").splitlines() if ln.strip()]
    return [ln for ln in re.split(r"\n+", text) if ln.strip()]


def content_type_subtitles(text: str) -> bool:
    return "-->" in text


def translate_lines(
    lines: list[str],
    translate_fn: Callable[[str], str],
) -> str:
    if not lines:
        return ""
    if len(lines) == 1:
        return translate_fn(lines[0])
    translated: list[str] = []
    for line in lines:
        translated.append(translate_fn(line))
    return "\n".join(translated)
