"""Shared video generation HTTP clients."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Callable

import httpx

from app.domain.storage.registry import upload_bytes

logger = logging.getLogger("untold.video_client")


def aspect_to_ratio(aspect_ratio: str) -> str:
    return aspect_ratio if aspect_ratio in ("16:9", "9:16", "1:1", "4:3") else "16:9"


def aspect_to_dimensions(aspect_ratio: str, width: int, height: int) -> tuple[int, int]:
    mapping = {
        "16:9": (1280, 720),
        "9:16": (720, 1280),
        "1:1": (720, 720),
        "4:3": (960, 720),
    }
    return mapping.get(aspect_ratio, (width, height))


def fetch_url_bytes(url: str, timeout: float = 120.0) -> bytes:
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.content


def upload_video_bytes(
    data: bytes,
    *,
    project_id: int | None = None,
    mime_type: str = "video/mp4",
    ext: str = "mp4",
) -> dict[str, Any]:
    folder = project_id or "studio"
    key = f"ai-videos/{folder}/{uuid.uuid4().hex}.{ext}"
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
            raise RuntimeError(result.get("error") or result.get("failure") or "Video task failed")
        time.sleep(interval)
    raise RuntimeError("Video generation timed out")


def generate_runway(
    *,
    api_key: str,
    model: str,
    prompt: str,
    duration: int,
    aspect_ratio: str,
    timeout: float = 300.0,
) -> bytes:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Runway-Version": "2024-11-06",
    }
    payload = {
        "model": model,
        "promptText": prompt,
        "duration": max(5, min(duration, 10)),
        "ratio": aspect_to_ratio(aspect_ratio).replace(":", ":"),
    }
    with httpx.Client(timeout=60.0) as client:
        create = client.post("https://api.dev.runwayml.com/v1/text_to_video", headers=headers, json=payload)
        create.raise_for_status()
        task = create.json()
        task_id = task["id"]

        def poll() -> dict:
            r = client.get(f"https://api.dev.runwayml.com/v1/tasks/{task_id}", headers=headers)
            r.raise_for_status()
            return r.json()

        done = poll_task(
            poll,
            is_done=lambda x: x.get("status") == "SUCCEEDED",
            is_failed=lambda x: x.get("status") in ("FAILED", "CANCELLED"),
            timeout=timeout,
        )
        url = (done.get("output") or [None])[0] if isinstance(done.get("output"), list) else done.get("output")
        if not url:
            raise RuntimeError("Runway succeeded without output url")
        return fetch_url_bytes(url, timeout=timeout)


def generate_google_veo(
    *,
    api_key: str,
    model: str,
    prompt: str,
    aspect_ratio: str,
    timeout: float = 300.0,
) -> bytes:
    headers = {"Content-Type": "application/json"}
    base = f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"aspectRatio": aspect_to_ratio(aspect_ratio)},
    }
    with httpx.Client(timeout=60.0) as client:
        start = client.post(f"{base}:predictLongRunning", params={"key": api_key}, json=payload, headers=headers)
        start.raise_for_status()
        op = start.json()
        op_name = op.get("name")
        if not op_name:
            raise RuntimeError("Veo missing operation name")

        def poll() -> dict:
            r = client.get(
                f"https://generativelanguage.googleapis.com/v1beta/{op_name}",
                params={"key": api_key},
            )
            r.raise_for_status()
            return r.json()

        done = poll_task(
            poll,
            is_done=lambda x: x.get("done") is True,
            is_failed=lambda x: bool(x.get("error")),
            timeout=timeout,
        )
        response = done.get("response") or {}
        videos = response.get("videos") or response.get("generatedVideos") or []
        if videos:
            uri = videos[0].get("uri") or videos[0].get("gcsUri")
            if uri and uri.startswith("http"):
                return fetch_url_bytes(uri, timeout=timeout)
        b64 = (response.get("video") or {}).get("bytesBase64Encoded")
        if b64:
            import base64
            return base64.b64decode(b64)
        raise RuntimeError("Google Veo returned no video")


def generate_luma(
    *,
    api_key: str,
    prompt: str,
    aspect_ratio: str,
    timeout: float = 300.0,
) -> bytes:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "aspect_ratio": aspect_to_ratio(aspect_ratio)}
    with httpx.Client(timeout=60.0) as client:
        create = client.post("https://api.lumalabs.ai/dream-machine/v1/generations", headers=headers, json=payload)
        create.raise_for_status()
        gen = create.json()
        gen_id = gen["id"]

        def poll() -> dict:
            r = client.get(f"https://api.lumalabs.ai/dream-machine/v1/generations/{gen_id}", headers=headers)
            r.raise_for_status()
            return r.json()

        done = poll_task(
            poll,
            is_done=lambda x: x.get("state") == "completed",
            is_failed=lambda x: x.get("state") in ("failed", "error"),
            timeout=timeout,
        )
        assets = done.get("assets") or {}
        url = assets.get("video") or (done.get("video") or {}).get("url")
        if not url:
            raise RuntimeError("Luma completed without video url")
        return fetch_url_bytes(url, timeout=timeout)


def generate_pika(
    *,
    api_key: str,
    prompt: str,
    aspect_ratio: str,
    timeout: float = 300.0,
) -> bytes:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "promptText": prompt,
        "aspectRatio": aspect_to_ratio(aspect_ratio).replace(":", ":"),
    }
    with httpx.Client(timeout=60.0) as client:
        create = client.post("https://api.pika.art/v1/generate", headers=headers, json=payload)
        create.raise_for_status()
        job = create.json()
        job_id = job.get("id") or job.get("job_id")

        def poll() -> dict:
            r = client.get(f"https://api.pika.art/v1/generate/{job_id}", headers=headers)
            r.raise_for_status()
            return r.json()

        done = poll_task(
            poll,
            is_done=lambda x: x.get("status") in ("finished", "completed", "succeeded"),
            is_failed=lambda x: x.get("status") in ("failed", "error"),
            timeout=timeout,
        )
        url = done.get("videoUrl") or done.get("url") or (done.get("video") or {}).get("url")
        if not url:
            raise RuntimeError("Pika completed without video url")
        return fetch_url_bytes(url, timeout=timeout)


def generate_kling(
    *,
    api_key: str,
    api_secret: str | None,
    prompt: str,
    duration: int,
    aspect_ratio: str,
    timeout: float = 300.0,
) -> bytes:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if api_secret:
        headers["X-Kling-Secret"] = api_secret
    payload = {
        "prompt": prompt,
        "duration": str(max(5, min(duration, 10))),
        "aspect_ratio": aspect_to_ratio(aspect_ratio),
        "mode": "std",
    }
    with httpx.Client(timeout=60.0) as client:
        create = client.post("https://api.klingai.com/v1/videos/text2video", headers=headers, json=payload)
        create.raise_for_status()
        task = create.json()
        task_id = task.get("data", {}).get("task_id") or task.get("task_id")

        def poll() -> dict:
            r = client.get(f"https://api.klingai.com/v1/videos/text2video/{task_id}", headers=headers)
            r.raise_for_status()
            return r.json()

        done = poll_task(
            poll,
            is_done=lambda x: (x.get("data") or {}).get("task_status") == "succeed",
            is_failed=lambda x: (x.get("data") or {}).get("task_status") == "failed",
            timeout=timeout,
        )
        videos = (done.get("data") or {}).get("task_result", {}).get("videos") or []
        url = videos[0].get("url") if videos else None
        if not url:
            raise RuntimeError("Kling succeeded without video url")
        return fetch_url_bytes(url, timeout=timeout)


def generate_hailuo(
    *,
    api_key: str,
    group_id: str,
    prompt: str,
    timeout: float = 300.0,
) -> bytes:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": "video-01", "prompt": prompt}
    with httpx.Client(timeout=60.0) as client:
        create = client.post(
            f"https://api.minimax.chat/v1/video_generation?GroupId={group_id}",
            headers=headers,
            json=payload,
        )
        create.raise_for_status()
        task = create.json()
        task_id = task.get("task_id") or (task.get("data") or {}).get("task_id")

        def poll() -> dict:
            r = client.get(
                f"https://api.minimax.chat/v1/query/video_generation?GroupId={group_id}&task_id={task_id}",
                headers=headers,
            )
            r.raise_for_status()
            return r.json()

        done = poll_task(
            poll,
            is_done=lambda x: (x.get("status") or (x.get("data") or {}).get("status")) == "Success",
            is_failed=lambda x: (x.get("status") or (x.get("data") or {}).get("status")) == "Failed",
            timeout=timeout,
        )
        file_id = (done.get("data") or {}).get("file_id") or done.get("file_id")
        if not file_id:
            raise RuntimeError("Hailuo missing file_id")
        file_resp = client.get(
            f"https://api.minimax.chat/v1/files/retrieve?GroupId={group_id}&file_id={file_id}",
            headers=headers,
        )
        file_resp.raise_for_status()
        url = (file_resp.json().get("file") or {}).get("download_url")
        if not url:
            raise RuntimeError("Hailuo missing download url")
        return fetch_url_bytes(url, timeout=timeout)


def generate_replicate_video(
    *,
    api_token: str,
    model: str,
    input_payload: dict[str, Any],
    timeout: float = 300.0,
) -> bytes:
    headers = {"Authorization": f"Token {api_token}", "Content-Type": "application/json"}
    owner, name = model.split("/", 1)
    with httpx.Client(timeout=30.0) as client:
        model_resp = client.get(f"https://api.replicate.com/v1/models/{owner}/{name}", headers=headers)
        model_resp.raise_for_status()
        version = model_resp.json()["latest_version"]["id"]

        create = client.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json={"version": version, "input": input_payload},
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
            return fetch_url_bytes(output[0], timeout=timeout)
        if isinstance(output, str):
            return fetch_url_bytes(output, timeout=timeout)
        raise RuntimeError("Replicate video succeeded without output")
