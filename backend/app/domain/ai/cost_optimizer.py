"""AI cost optimization — model selection, caching, pricing."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.domain.ai.telemetry import estimate_cost_usd, estimate_tokens

# USD per token (input, output)
MODEL_PRICING: dict[str, tuple[float, float]] = {
    "demo-sim-v1": (0.0000005, 0.000002),
    "gpt-4o-mini": (0.00000015, 0.0000006),
    "gpt-4o": (0.0000025, 0.00001),
    "claude-3-5-sonnet": (0.000003, 0.000015),
    "claude-3-haiku": (0.00000025, 0.00000125),
    "gemini-2.0-flash": (0.0000001, 0.0000004),
    "gemini-1.5-pro": (0.00000125, 0.000005),
}

MODULE_MODEL_DEFAULTS: dict[str, dict[str, str]] = {
    "research": {"cheapest": "gpt-4o-mini", "quality": "gpt-4o", "provider": "openai"},
    "script": {"cheapest": "gpt-4o-mini", "quality": "gpt-4o", "provider": "openai"},
    "seo": {"cheapest": "gpt-4o-mini", "quality": "gpt-4o", "provider": "openai"},
    "translation": {"cheapest": "gpt-4o-mini", "quality": "gpt-4o", "provider": "openai"},
    "thumbnail": {"cheapest": "demo-sim-v1", "quality": "gpt-4o", "provider": "demo"},
    "image": {"cheapest": "demo-sim-v1", "quality": "demo-sim-v1", "provider": "demo"},
    "video": {"cheapest": "demo-sim-v1", "quality": "demo-sim-v1", "provider": "demo"},
    "voice": {"cheapest": "demo-sim-v1", "quality": "demo-sim-v1", "provider": "demo"},
    "music": {"cheapest": "gpt-4o-mini", "quality": "gpt-4o", "provider": "openai"},
    "*": {"cheapest": "gpt-4o-mini", "quality": "gpt-4o", "provider": "openai"},
}

DEFAULT_FALLBACK_CHAIN: list[dict[str, str]] = [
    {"provider": "openai", "model": "gpt-4o-mini"},
    {"provider": "gemini", "model": "gemini-2.0-flash"},
    {"provider": "demo", "model": "demo-sim-v1"},
]


@dataclass
class ModelSelection:
    provider: str
    model: str
    estimated_cost_usd: float
    selection_mode: str
    from_cache: bool = False


def model_rates(model: str) -> tuple[float, float]:
    if model in MODEL_PRICING:
        return MODEL_PRICING[model]
    if "mini" in model or "haiku" in model or "flash" in model:
        return (0.00000015, 0.0000006)
    if model.startswith("demo"):
        return MODEL_PRICING["demo-sim-v1"]
    return (0.0000025, 0.00001)


def estimate_request_cost(prompt: str, *, model: str, expected_output_tokens: int | None = None) -> float:
    inp = estimate_tokens(prompt)
    out = expected_output_tokens or max(64, inp // 2)
    return estimate_cost_usd(inp, out, model)


def select_model(
    module: str,
    prompt: str,
    *,
    selection_mode: str = "auto",
    primary_model: str | None = None,
    primary_provider: str | None = None,
    max_cost_per_request: float | None = None,
) -> ModelSelection:
    defaults = MODULE_MODEL_DEFAULTS.get(module) or MODULE_MODEL_DEFAULTS["*"]
    mode = selection_mode or "auto"

    if mode == "fixed" and primary_model:
        model = primary_model
        provider = primary_provider or defaults["provider"]
    elif mode == "cheapest":
        model = defaults["cheapest"]
        provider = defaults["provider"]
    elif mode == "quality":
        model = defaults["quality"]
        provider = defaults["provider"]
    else:
        # auto: short prompts → cheapest, long → quality
        tokens = estimate_tokens(prompt)
        if tokens < 800:
            model = defaults["cheapest"]
        else:
            model = defaults["quality"]
        provider = defaults["provider"]

    cost = estimate_request_cost(prompt, model=model)
    if max_cost_per_request is not None and cost > max_cost_per_request:
        model = defaults["cheapest"]
        provider = defaults["provider"]
        cost = estimate_request_cost(prompt, model=model)

    return ModelSelection(provider=provider, model=model, estimated_cost_usd=cost, selection_mode=mode)


def build_cache_key(module: str, prompt: str, parameters: dict[str, Any] | None = None) -> str:
    payload = {
        "module": module,
        "prompt": prompt.strip(),
        "parameters": parameters or {},
    }
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.strip().encode()).hexdigest()[:16]
