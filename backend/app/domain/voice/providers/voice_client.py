"""Shared voice / TTS HTTP clients."""

from __future__ import annotations

import base64
import logging
import uuid
from typing import Any

import httpx

from app.domain.storage.registry import upload_bytes

logger = logging.getLogger("untold.voice_client")


def upload_audio_bytes(
    data: bytes,
    mime_type: str,
    *,
    project_id: int | None = None,
) -> dict[str, Any]:
    ext = {
        "audio/mpeg": "mp3",
        "audio/mp3": "mp3",
        "audio/wav": "wav",
        "audio/x-wav": "wav",
    }.get(mime_type, "mp3")
    folder = project_id or "studio"
    key = f"ai-voice/{folder}/{uuid.uuid4().hex}.{ext}"
    uploaded = upload_bytes(key, data, mime_type)
    return {
        "url": uploaded.url,
        "key": uploaded.key,
        "size_bytes": uploaded.size_bytes,
        "mime_type": mime_type,
    }


def synthesize_elevenlabs(
    *,
    api_key: str,
    voice_id: str,
    text: str,
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    timeout: float = 120.0,
) -> tuple[bytes, str]:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {"stability": stability, "similarity_boost": similarity_boost},
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.content, "audio/mpeg"


def synthesize_openai_tts(
    *,
    api_key: str,
    text: str,
    model: str = "tts-1",
    voice: str = "alloy",
    speed: float = 1.0,
    timeout: float = 120.0,
) -> tuple[bytes, str]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "speed": max(0.25, min(speed, 4.0)),
        "response_format": "mp3",
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post("https://api.openai.com/v1/audio/speech", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.content, "audio/mpeg"


def synthesize_azure_speech(
    *,
    api_key: str,
    region: str,
    text: str,
    voice: str,
    language: str = "en-US",
    speed: float = 1.0,
    pitch: float = 1.0,
    timeout: float = 120.0,
) -> tuple[bytes, str]:
    rate_pct = int((speed - 1.0) * 100)
    pitch_pct = int((pitch - 1.0) * 50)
    ssml = f"""<speak version='1.0' xml:lang='{language}'>
  <voice name='{voice}'>
    <prosody rate='{rate_pct:+d}%' pitch='{pitch_pct:+d}%'>
      {text}
    </prosody>
  </voice>
</speak>"""
    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, headers=headers, content=ssml.encode("utf-8"))
        resp.raise_for_status()
        return resp.content, "audio/mpeg"


def synthesize_google_tts(
    *,
    api_key: str,
    text: str,
    language_code: str = "en-US",
    voice_name: str | None = None,
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
    timeout: float = 120.0,
) -> tuple[bytes, str]:
    voice = {"languageCode": language_code, "name": voice_name} if voice_name else {"languageCode": language_code}
    payload = {
        "input": {"text": text},
        "voice": voice,
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": speaking_rate,
            "pitch": pitch,
        },
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            "https://texttospeech.googleapis.com/v1/text:synthesize",
            params={"key": api_key},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
    audio = base64.b64decode(data["audioContent"])
    return audio, "audio/mpeg"


def synthesize_cartesia(
    *,
    api_key: str,
    text: str,
    voice_id: str,
    model_id: str = "sonic-english",
    language: str = "en",
    timeout: float = 120.0,
) -> tuple[bytes, str]:
    headers = {
        "X-API-Key": api_key,
        "Cartesia-Version": "2024-06-10",
        "Content-Type": "application/json",
    }
    payload = {
        "model_id": model_id,
        "transcript": text,
        "voice": {"mode": "id", "id": voice_id},
        "output_format": {"container": "mp3", "encoding": "mp3", "sample_rate": 44100},
        "language": language,
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post("https://api.cartesia.ai/tts/bytes", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.content, "audio/mpeg"


def synthesize_playht(
    *,
    api_key: str,
    user_id: str,
    text: str,
    voice_id: str,
    quality: str = "medium",
    timeout: float = 120.0,
) -> tuple[bytes, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-User-Id": user_id,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "voice": voice_id,
        "output_format": "mp3",
        "quality": quality,
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post("https://api.play.ht/api/v2/tts/stream", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.content, "audio/mpeg"


def language_to_bcp47(language: str) -> str:
    return {
        "en": "en-US",
        "hi": "hi-IN",
        "ar": "ar-XA",
        "es": "es-ES",
        "fr": "fr-FR",
        "ja": "ja-JP",
    }.get(language, "en-US")
