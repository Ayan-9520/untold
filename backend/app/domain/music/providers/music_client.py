"""Shared music generation HTTP clients."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Callable

import httpx

from app.domain.storage.registry import upload_bytes

logger = logging.getLogger("untold.music_client")


def fetch_url_bytes(url: str, timeout: float = 120.0) -> bytes:
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.content


def upload_music_bytes(
    data: bytes,
    mime_type: str,
    *,
    project_id: int | None = None,
    ext: str | None = None,
) -> dict[str, Any]:
    if not ext:
        ext = {"audio/mpeg": "mp3", "audio/mp3": "mp3", "audio/wav": "wav"}.get(mime_type, "mp3")
    folder = project_id or "studio"
    key = f"ai-music/{folder}/{uuid.uuid4().hex}.{ext}"
    uploaded = upload_bytes(key, data, mime_type)
    return {
        "url": uploaded.url,
        "key": uploaded.key,
        "size_bytes": uploaded.size_bytes,
        "mime_type": mime_type,
    }


def poll_task(
    poll_fn: Callable[[], dict[str, Any]],
    *,
    is_done: Callable[[dict[str, Any]], bool],
    is_failed: Callable[[dict[str, Any]], bool],
    timeout: float = 300.0,
    interval: float = 3.0,
) -> dict[str, Any]:
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = poll_fn()
        if is_done(result):
            return result
        if is_failed(result):
            raise RuntimeError(result.get("error") or result.get("message") or "Music task failed")
        time.sleep(interval)
    raise RuntimeError("Music generation timed out")


def _category_prompt(prompt: str, category: str) -> str:
    return f"[{category}] {prompt}".strip()


def generate_suno(
    *,
    api_key: str,
    base_url: str,
    prompt: str,
    duration: int,
    category: str,
    timeout: float = 300.0,
) -> tuple[bytes, str]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "prompt": _category_prompt(prompt, category),
        "duration": max(15, min(duration, 120)),
        "make_instrumental": True,
    }
    base = base_url.rstrip("/")
    with httpx.Client(timeout=60.0) as client:
        create = client.post(f"{base}/generate", headers=headers, json=payload)
        create.raise_for_status()
        task = create.json()
        task_id = task.get("id") or task.get("task_id") or (task.get("data") or {}).get("task_id")

        def poll() -> dict:
            r = client.get(f"{base}/generate/{task_id}", headers=headers)
            r.raise_for_status()
            return r.json()

        done = poll_task(
            poll,
            is_done=lambda x: x.get("status") in ("complete", "completed", "succeeded"),
            is_failed=lambda x: x.get("status") in ("failed", "error"),
            timeout=timeout,
        )
        url = (
            done.get("audio_url")
            or (done.get("data") or {}).get("audio_url")
            or ((done.get("clips") or [{}])[0].get("audio_url") if done.get("clips") else None)
        )
        if not url:
            raise RuntimeError("Suno completed without audio url")
        return fetch_url_bytes(url, timeout=timeout), "audio/mpeg"


def generate_udio(
    *,
    api_key: str,
    base_url: str,
    prompt: str,
    duration: int,
    category: str,
    timeout: float = 300.0,
) -> tuple[bytes, str]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "prompt": _category_prompt(prompt, category),
        "duration": max(15, min(duration, 120)),
        "instrumental": True,
    }
    base = base_url.rstrip("/")
    with httpx.Client(timeout=60.0) as client:
        create = client.post(f"{base}/generate", headers=headers, json=payload)
        create.raise_for_status()
        task = create.json()
        task_id = task.get("id") or task.get("job_id")

        def poll() -> dict:
            r = client.get(f"{base}/jobs/{task_id}", headers=headers)
            r.raise_for_status()
            return r.json()

        done = poll_task(
            poll,
            is_done=lambda x: x.get("status") in ("completed", "succeeded", "ready"),
            is_failed=lambda x: x.get("status") in ("failed", "error"),
            timeout=timeout,
        )
        url = done.get("audio_url") or (done.get("result") or {}).get("audio_url")
        if not url:
            raise RuntimeError("Udio completed without audio url")
        return fetch_url_bytes(url, timeout=timeout), "audio/mpeg"


def generate_stable_audio(
    *,
    api_key: str,
    prompt: str,
    duration: int,
    category: str,
    timeout: float = 180.0,
) -> tuple[bytes, str]:
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "audio/*"}
    data = {
        "prompt": _category_prompt(prompt, category),
        "duration": str(max(10, min(duration, 180))),
        "output_format": "mp3",
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            "https://api.stability.ai/v2beta/audio/stable-audio-2/text-to-audio",
            headers=headers,
            data=data,
        )
        resp.raise_for_status()
        mime = resp.headers.get("content-type", "audio/mpeg")
        return resp.content, mime


def generate_elevenlabs_music(
    *,
    api_key: str,
    prompt: str,
    duration: int,
    category: str,
    timeout: float = 180.0,
) -> tuple[bytes, str]:
    headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
    payload = {
        "text": _category_prompt(prompt, category),
        "duration_seconds": max(5, min(duration, 60)),
        "prompt_influence": 0.35,
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            "https://api.elevenlabs.io/v1/sound-generation",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        return resp.content, "audio/mpeg"


def generate_replicate_music(
    *,
    api_token: str,
    model: str,
    prompt: str,
    duration: int,
    category: str,
    timeout: float = 300.0,
) -> tuple[bytes, str]:
    headers = {"Authorization": f"Token {api_token}", "Content-Type": "application/json"}
    owner, name = model.split("/", 1)
    with httpx.Client(timeout=30.0) as client:
        model_resp = client.get(f"https://api.replicate.com/v1/models/{owner}/{name}", headers=headers)
        model_resp.raise_for_status()
        version = model_resp.json()["latest_version"]["id"]
        create = client.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json={
                "version": version,
                "input": {
                    "prompt": _category_prompt(prompt, category),
                    "duration": max(10, min(duration, 120)),
                },
            },
        )
        create.raise_for_status()
        poll_url = create.json()["urls"]["get"]

        def poll() -> dict:
            r = client.get(poll_url, headers=headers)
            r.raise_for_status()
            return r.json()

        done = poll_task(
            poll,
            is_done=lambda x: x.get("status") == "succeeded",
            is_failed=lambda x: x.get("status") in ("failed", "canceled"),
            timeout=timeout,
        )
        output = done.get("output")
        if isinstance(output, list) and output:
            return fetch_url_bytes(output[0], timeout=timeout), "audio/mpeg"
        if isinstance(output, str):
            return fetch_url_bytes(output, timeout=timeout), "audio/mpeg"
        raise RuntimeError("Replicate music succeeded without output")


def generate_fal_music(
    *,
    api_key: str,
    model: str,
    prompt: str,
    duration: int,
    category: str,
    timeout: float = 180.0,
) -> tuple[bytes, str]:
    headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
    payload = {
        "prompt": _category_prompt(prompt, category),
        "seconds_total": max(10, min(duration, 120)),
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(f"https://fal.run/{model}", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    audio = data.get("audio_file") or data.get("audio") or {}
    url = audio.get("url") if isinstance(audio, dict) else None
    if not url and data.get("audio_url"):
        url = data["audio_url"]
    if not url:
        raise RuntimeError("Fal music returned no audio url")
    return fetch_url_bytes(url, timeout=timeout), "audio/mpeg"
