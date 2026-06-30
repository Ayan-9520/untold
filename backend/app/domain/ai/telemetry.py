"""AI telemetry helpers — token estimates, cost, model resolution."""

from __future__ import annotations

from typing import Any

_DEFAULT_MODELS: dict[str, str] = {
    "demo": "demo-sim-v1",
    "openai": "gpt-4o-mini",
    "gemini": "gemini-2.0-flash",
    "anthropic": "claude-3-5-sonnet",
}


def estimate_tokens(text: str | None) -> int:
    if not text:
        return 0
    return max(1, len(text) // 4)


def resolve_model(provider: str | None, meta: dict[str, Any] | None = None) -> str:
    if meta and meta.get("model"):
        return str(meta["model"])
    if provider and provider in _DEFAULT_MODELS:
        return _DEFAULT_MODELS[provider]
    return f"{provider or 'demo'}-default"


def estimate_cost_usd(input_tokens: int, output_tokens: int, model: str) -> float:
    from app.domain.ai.cost_optimizer import model_rates

    rate_in, rate_out = model_rates(model)
    return round(input_tokens * rate_in + output_tokens * rate_out, 6)
