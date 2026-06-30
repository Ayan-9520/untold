"""Shared image generation HTTP clients."""

from __future__ import annotations

import base64
import logging
import time
import uuid
from typing import Any

import httpx

from app.domain.storage.registry import upload_bytes

logger = logging.getLogger("untold.image_client")


def aspect_to_size(aspect_ratio: str, width: int, height: int) -> tuple[int, int]:
    mapping = {
        "16:9": (1024, 576),
        "9:16": (576, 1024),
        "1:1": (1024, 1024),
        "4:3": (1024, 768),
        "3:4": (768, 1024),
    }
    return mapping.get(aspect_ratio, (width, height))


def openai_size(aspect_ratio: str) -> str:
    w, h = aspect_to_size(aspect_ratio, 1024, 1024)
    if w == h:
        return "1024x1024"
    if w > h:
        return "1792x1024"
    return "1024x1792"


def upload_image_bytes(
    data: bytes,
    mime_type: str,
    *,
    project_id: int | None = None,
    ext: str = "png",
) -> dict[str, Any]:
    folder = project_id or "studio"
    key = f"ai-images/{folder}/{uuid.uuid4().hex}.{ext}"
    uploaded = upload_bytes(key, data, mime_type)
    return {
        "url": uploaded.url,
        "key": uploaded.key,
        "size_bytes": uploaded.size_bytes,
        "mime_type": mime_type,
    }


def fetch_url_bytes(url: str, timeout: float = 60.0) -> bytes:
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.content


def generate_openai_images(
    *,
    api_key: str,
    model: str,
    prompt: str,
    aspect_ratio: str,
    timeout: float = 120.0,
) -> bytes:
    payload = {
        "model": model,
        "prompt": prompt,
        "size": openai_size(aspect_ratio),
        "n": 1,
        "response_format": "b64_json",
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    with httpx.Client(timeout=timeout) as client:
        resp = client.post("https://api.openai.com/v1/images/generations", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    b64 = data["data"][0].get("b64_json")
    if b64:
        return base64.b64decode(b64)
    url = data["data"][0].get("url")
    if url:
        return fetch_url_bytes(url, timeout=timeout)
    raise RuntimeError("OpenAI Images returned no image data")


def generate_google_imagen(
    *,
    api_key: str,
    model: str,
    prompt: str,
    aspect_ratio: str,
    timeout: float = 120.0,
) -> bytes:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": aspect_ratio},
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, params={"key": api_key}, json=payload)
        resp.raise_for_status()
        data = resp.json()
    predictions = data.get("predictions") or data.get("generatedImages") or []
    if not predictions:
        raise RuntimeError("Imagen returned no predictions")
    pred = predictions[0]
    b64 = pred.get("bytesBase64Encoded") or pred.get("image", {}).get("bytesBase64Encoded")
    if b64:
        return base64.b64decode(b64)
    if pred.get("url"):
        return fetch_url_bytes(pred["url"], timeout=timeout)
    raise RuntimeError("Imagen response missing image bytes")


def generate_stability(
    *,
    api_key: str,
    prompt: str,
    width: int,
    height: int,
    timeout: float = 120.0,
) -> bytes:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*",
    }
    payload = {
        "text_prompts": [{"text": prompt, "weight": 1}],
        "cfg_scale": 7,
        "width": width,
        "height": height,
        "samples": 1,
        "steps": 30,
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
    artifacts = data.get("artifacts") or []
    if not artifacts:
        raise RuntimeError("Stability AI returned no artifacts")
    b64 = artifacts[0].get("base64")
    if not b64:
        raise RuntimeError("Stability AI missing base64 artifact")
    return base64.b64decode(b64)


def generate_ideogram(
    *,
    api_key: str,
    prompt: str,
    aspect_ratio: str,
    timeout: float = 120.0,
) -> bytes:
    headers = {"Api-Key": api_key, "Content-Type": "application/json"}
    payload = {
        "image_request": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "model": "V_2",
        }
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post("https://api.ideogram.ai/generate", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    images = data.get("data") or []
    if not images:
        raise RuntimeError("Ideogram returned no images")
    url = images[0].get("url")
    if not url:
        raise RuntimeError("Ideogram missing image url")
    return fetch_url_bytes(url, timeout=timeout)


def generate_flux_bfl(
    *,
    api_key: str,
    model: str,
    prompt: str,
    width: int,
    height: int,
    timeout: float = 180.0,
) -> bytes:
    headers = {"x-key": api_key, "Content-Type": "application/json"}
    payload = {"prompt": prompt, "width": width, "height": height}
    endpoint = f"https://api.bfl.ml/v1/{model}"
    with httpx.Client(timeout=timeout) as client:
        submit = client.post(endpoint, headers=headers, json=payload)
        submit.raise_for_status()
        task = submit.json()
        task_id = task.get("id")
        polling_url = task.get("polling_url") or f"https://api.bfl.ml/v1/get_result?id={task_id}"
        deadline = time.time() + timeout
        while time.time() < deadline:
            poll = client.get(polling_url, headers=headers)
            poll.raise_for_status()
            result = poll.json()
            status = result.get("status")
            if status == "Ready":
                sample = (result.get("result") or {}).get("sample")
                if sample:
                    return fetch_url_bytes(sample, timeout=timeout)
                raise RuntimeError("Flux ready but no sample url")
            if status in ("Error", "Failed"):
                raise RuntimeError(result.get("error", "Flux generation failed"))
            time.sleep(1.5)
    raise RuntimeError("Flux generation timed out")


def generate_replicate(
    *,
    api_token: str,
    model: str,
    input_payload: dict[str, Any],
    timeout: float = 180.0,
) -> bytes:
    headers = {
        "Authorization": f"Token {api_token}",
        "Content-Type": "application/json",
    }
    owner, name = model.split("/", 1)
    with httpx.Client(timeout=30.0) as client:
        model_resp = client.get(f"https://api.replicate.com/v1/models/{owner}/{name}", headers=headers)
        model_resp.raise_for_status()
        version = model_resp.json()["latest_version"]["id"]

    body = {"version": version, "input": input_payload}
    with httpx.Client(timeout=timeout) as client:
        create = client.post("https://api.replicate.com/v1/predictions", headers=headers, json=body)
        create.raise_for_status()
        prediction = create.json()
        poll_url = prediction["urls"]["get"]
        deadline = time.time() + timeout
        while time.time() < deadline:
            poll = client.get(poll_url, headers=headers)
            poll.raise_for_status()
            result = poll.json()
            status = result.get("status")
            if status == "succeeded":
                output = result.get("output")
                if isinstance(output, list) and output:
                    return fetch_url_bytes(output[0], timeout=timeout)
                if isinstance(output, str):
                    return fetch_url_bytes(output, timeout=timeout)
                raise RuntimeError("Replicate succeeded without output url")
            if status in ("failed", "canceled"):
                raise RuntimeError(result.get("error", "Replicate prediction failed"))
            time.sleep(2)
    raise RuntimeError("Replicate prediction timed out")


def generate_fal(
    *,
    api_key: str,
    model: str,
    input_payload: dict[str, Any],
    timeout: float = 180.0,
) -> bytes:
    headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
    url = f"https://fal.run/{model}"
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, headers=headers, json=input_payload)
        resp.raise_for_status()
        data = resp.json()
    images = data.get("images") or []
    if images:
        img_url = images[0].get("url")
        if img_url:
            return fetch_url_bytes(img_url, timeout=timeout)
    if data.get("image", {}).get("url"):
        return fetch_url_bytes(data["image"]["url"], timeout=timeout)
    raise RuntimeError("Fal.ai returned no image")
