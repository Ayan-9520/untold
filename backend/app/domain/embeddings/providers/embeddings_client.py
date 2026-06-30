"""Shared embeddings HTTP clients."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger("untold.embeddings_client")


def embed_openai(
    *,
    api_key: str,
    model: str,
    texts: list[str],
    timeout: float = 60.0,
) -> list[list[float]]:
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": model, "input": texts},
        )
        resp.raise_for_status()
        data = resp.json()["data"]
    return [row["embedding"] for row in sorted(data, key=lambda x: x["index"])]


def embed_voyage(
    *,
    api_key: str,
    model: str,
    texts: list[str],
    timeout: float = 60.0,
) -> list[list[float]]:
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            "https://api.voyageai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"input": texts, "model": model},
        )
        resp.raise_for_status()
        data = resp.json()["data"]
    return [row["embedding"] for row in sorted(data, key=lambda x: x["index"])]


def embed_cohere(
    *,
    api_key: str,
    model: str,
    texts: list[str],
    timeout: float = 60.0,
) -> list[list[float]]:
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            "https://api.cohere.com/v2/embed",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "texts": texts,
                "model": model,
                "input_type": "search_document",
                "embedding_types": ["float"],
            },
        )
        resp.raise_for_status()
        payload = resp.json()
    vectors = (payload.get("embeddings") or {}).get("float") or []
    if len(vectors) != len(texts):
        raise RuntimeError("Cohere returned unexpected embedding count")
    return vectors


def embed_gemini(
    *,
    api_key: str,
    model: str,
    texts: list[str],
    timeout: float = 60.0,
) -> list[list[float]]:
    base = f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
    if len(texts) == 1:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                f"{base}:embedContent",
                params={"key": api_key},
                json={"content": {"parts": [{"text": texts[0]}]}},
            )
            resp.raise_for_status()
            values = resp.json()["embedding"]["values"]
        return [values]

    requests = [{"model": f"models/{model}", "content": {"parts": [{"text": t}]}} for t in texts]
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            f"{base}:batchEmbedContents",
            params={"key": api_key},
            json={"requests": requests},
        )
        resp.raise_for_status()
        embeddings = resp.json().get("embeddings") or []
    return [e["values"] for e in embeddings]


def embed_jina(
    *,
    api_key: str,
    model: str,
    texts: list[str],
    timeout: float = 60.0,
) -> list[list[float]]:
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            "https://api.jina.ai/v1/embeddings",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": model, "input": texts},
        )
        resp.raise_for_status()
        data = resp.json()["data"]
    return [row["embedding"] for row in sorted(data, key=lambda x: x["index"])]


def embed_bge_hf(
    *,
    api_token: str,
    model: str,
    texts: list[str],
    timeout: float = 120.0,
) -> list[list[float]]:
    url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    vectors: list[list[float]] = []
    with httpx.Client(timeout=timeout) as client:
        for text in texts:
            resp = client.post(url, headers=headers, json={"inputs": text})
            resp.raise_for_status()
            raw: Any = resp.json()
            vectors.append(_normalize_hf_vector(raw))
    return vectors


def embed_bge_openai_compatible(
    *,
    base_url: str,
    model: str,
    texts: list[str],
    api_key: str | None = None,
    timeout: float = 120.0,
) -> list[list[float]]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    url = f"{base_url.rstrip('/')}/v1/embeddings"
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, headers=headers, json={"model": model, "input": texts})
        resp.raise_for_status()
        data = resp.json()["data"]
    return [row["embedding"] for row in sorted(data, key=lambda x: x["index"])]


def _normalize_hf_vector(raw: Any) -> list[float]:
    if isinstance(raw, list) and raw and isinstance(raw[0], (int, float)):
        return [float(x) for x in raw]
    if isinstance(raw, list) and raw and isinstance(raw[0], list):
        if raw and isinstance(raw[0][0], (int, float)):
            return [float(x) for x in raw[0]]
        if raw[0] and isinstance(raw[0][0], list):
            return [float(x) for x in raw[0][0]]
    raise RuntimeError("Unexpected HuggingFace embedding response shape")
