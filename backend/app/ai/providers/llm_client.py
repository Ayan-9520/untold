"""Shared LLM HTTP clients — OpenAI-compatible, Anthropic, Gemini, Ollama, Bedrock."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger("untold.ai.llm_client")

MODULE_SYSTEM_PROMPTS: dict[str, str] = {
    "research": "You are a documentary research assistant. Produce structured, factual briefs with sources and angles.",
    "script": "You are an award-winning documentary scriptwriter. Write in cinematic narration style.",
    "storyboard": "You are a storyboard director. Output clear shot lists and visual beats.",
    "seo": "You are an SEO specialist for video and documentary content. Output titles, descriptions, and tags.",
    "translation": "You are a professional translator for film and media content.",
    "thumbnail": "You are a thumbnail strategist for YouTube and streaming platforms.",
    "shorts": "You are a short-form video hook writer for Reels, Shorts, and TikTok.",
    "voice": "You write voice-over narration scripts for documentaries.",
    "music": "You write music briefs for documentary scoring.",
}


def system_prompt_for(module: str) -> str:
    return MODULE_SYSTEM_PROMPTS.get(
        module,
        "You are UNTOLD Studio AI — a production assistant for documentary and sports storytelling.",
    )


def chat_openai_compatible(
    *,
    url: str,
    api_key: str,
    model: str,
    user_prompt: str,
    system: str,
    extra_headers: dict[str, str] | None = None,
    timeout: float = 60.0,
) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        **(extra_headers or {}),
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def chat_anthropic(
    *,
    api_key: str,
    model: str,
    user_prompt: str,
    system: str,
    timeout: float = 60.0,
) -> str:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 4096,
        "system": system,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    parts = data.get("content") or []
    return "".join(p.get("text", "") for p in parts if p.get("type") == "text").strip()


def chat_gemini(
    *,
    api_key: str,
    model: str,
    user_prompt: str,
    system: str,
    timeout: float = 60.0,
) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": f"{system}\n\n{user_prompt}"}]}],
        "generationConfig": {"temperature": 0.7},
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, params={"key": api_key}, json=payload)
        resp.raise_for_status()
        data = resp.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates")
    parts = candidates[0].get("content", {}).get("parts") or []
    return "".join(p.get("text", "") for p in parts).strip()


def chat_ollama(
    *,
    base_url: str,
    model: str,
    user_prompt: str,
    system: str,
    timeout: float = 120.0,
) -> str:
    url = f"{base_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
    return (data.get("message") or {}).get("content", "").strip()


def chat_azure_openai(
    *,
    endpoint: str,
    deployment: str,
    api_key: str,
    api_version: str,
    user_prompt: str,
    system: str,
    timeout: float = 60.0,
) -> str:
    base = endpoint.rstrip("/")
    url = f"{base}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
    }
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def chat_bedrock(
    *,
    region: str,
    model_id: str,
    user_prompt: str,
    system: str,
    timeout: float = 60.0,
) -> str:
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("boto3 required for AWS Bedrock") from exc

    client = boto3.client("bedrock-runtime", region_name=region)
    if model_id.startswith("anthropic."):
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": system,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(response["body"].read())
        parts = result.get("content") or []
        return "".join(p.get("text", "") for p in parts if p.get("type") == "text").strip()

    if model_id.startswith("amazon.titan"):
        body = {
            "inputText": f"{system}\n\n{user_prompt}",
            "textGenerationConfig": {"maxTokenCount": 4096, "temperature": 0.7},
        }
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(response["body"].read())
        return (result.get("results") or [{}])[0].get("outputText", "").strip()

    body = {
        "prompt": f"<s>[INST] {system}\n\n{user_prompt} [/INST]",
        "max_gen_len": 4096,
        "temperature": 0.7,
    }
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return result.get("generation", "").strip()


def ollama_reachable(base_url: str, timeout: float = 2.0) -> bool:
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(f"{base_url.rstrip('/')}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False


def bedrock_available(region: str) -> bool:
    try:
        import boto3

        sts = boto3.client("sts", region_name=region)
        sts.get_caller_identity()
        return True
    except Exception:
        return False
