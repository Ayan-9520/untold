"""AI Cost Intelligence — modality pricing, predictions, optimization, routing."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.domain.ai.cost_optimizer import MODEL_PRICING, model_rates, select_model
from app.domain.ai.telemetry import estimate_cost_usd, estimate_tokens, resolve_model

# USD per unit by modality (model -> unit price)
IMAGE_PRICING: dict[str, float] = {
    "dall-e-3": 0.04,
    "dall-e-2": 0.02,
    "imagen-3": 0.03,
    "stable-diffusion-xl": 0.008,
    "demo-sim-v1": 0.001,
}

VIDEO_PRICING: dict[str, float] = {
    "runway-gen3": 0.05,  # per second
    "sora": 0.08,
    "demo-sim-v1": 0.01,
}

VOICE_PRICING: dict[str, float] = {
    "elevenlabs-multilingual": 0.00003,  # per character
    "openai-tts-1": 0.000015,
    "demo-sim-v1": 0.000005,
}

MUSIC_PRICING: dict[str, float] = {
    "suno-v3": 0.02,  # per second
    "udio": 0.015,
    "demo-sim-v1": 0.005,
}

TRANSLATION_PRICING: dict[str, float] = {
    "deepl-pro": 0.00002,  # per character
    "gpt-4o-mini": 0.00001,
    "demo-sim-v1": 0.000005,
}

MODULE_MODALITY: dict[str, str] = {
    "research": "tokens",
    "script": "tokens",
    "storyboard": "tokens",
    "seo": "tokens",
    "thumbnail": "image",
    "image": "image",
    "video": "video",
    "shorts": "video",
    "voice": "voice",
    "music": "music",
    "translation": "translation",
}


class CostModality(str, enum.Enum):
    TOKENS = "tokens"
    IMAGE = "image"
    VIDEO = "video"
    VOICE = "voice"
    MUSIC = "music"
    TRANSLATION = "translation"


@dataclass
class CostEstimate:
    modality: str
    provider: str
    model: str
    cost_usd: float
    units: dict[str, float]
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class RoutingDecision:
    provider: str
    model: str
    estimated_cost_usd: float
    selection_mode: str
    fallback_chain: list[dict[str, str]]
    rationale: str


def modality_for_module(module: str) -> str:
    return MODULE_MODALITY.get(module, "tokens")


def _rate_for_modality(modality: str, model: str) -> float:
    tables = {
        "image": IMAGE_PRICING,
        "video": VIDEO_PRICING,
        "voice": VOICE_PRICING,
        "music": MUSIC_PRICING,
        "translation": TRANSLATION_PRICING,
    }
    table = tables.get(modality, {})
    if model in table:
        return table[model]
    if model.startswith("demo"):
        return table.get("demo-sim-v1", 0.001)
    return next(iter(table.values()), 0.01) if table else 0.0


def estimate_modality_cost(
    module: str,
    *,
    prompt: str | None = None,
    output_text: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    parameters: dict | None = None,
    meta: dict | None = None,
) -> CostEstimate:
    """Estimate cost for any AI module using modality-appropriate units."""
    meta = meta or {}
    params = parameters or {}
    module = module or "*"
    modality = modality_for_module(module)
    resolved_model = model or meta.get("model") or resolve_model(provider, meta)
    resolved_provider = provider or meta.get("provider") or "demo"

    if modality == "tokens":
        inp = int(meta.get("input_tokens") or estimate_tokens(prompt or ""))
        out = int(meta.get("output_tokens") or estimate_tokens(output_text or ""))
        cost = float(meta.get("cost_usd") or meta.get("estimated_cost_usd") or estimate_cost_usd(inp, out, resolved_model))
        return CostEstimate(
            modality=modality,
            provider=resolved_provider,
            model=resolved_model,
            cost_usd=round(cost, 6),
            units={"input_tokens": inp, "output_tokens": out},
            input_tokens=inp,
            output_tokens=out,
        )

    if modality == "image":
        count = float(params.get("image_count") or meta.get("image_count") or 1)
        rate = _rate_for_modality("image", resolved_model)
        cost = float(meta.get("cost_usd") or count * rate)
        return CostEstimate(
            modality=modality,
            provider=resolved_provider,
            model=resolved_model,
            cost_usd=round(cost, 6),
            units={"images": count},
        )

    if modality == "video":
        seconds = float(
            meta.get("duration_seconds")
            or params.get("duration_seconds")
            or 8
        )
        rate = _rate_for_modality("video", resolved_model)
        cost = float(meta.get("cost_usd") or seconds * rate)
        return CostEstimate(
            modality=modality,
            provider=resolved_provider,
            model=resolved_model,
            cost_usd=round(cost, 6),
            units={"video_seconds": seconds},
        )

    if modality == "voice":
        text = output_text or prompt or ""
        chars = float(meta.get("characters") or len(text))
        rate = _rate_for_modality("voice", resolved_model)
        seconds = float(meta.get("duration_seconds") or params.get("duration_seconds") or max(1, chars / 15))
        cost = float(meta.get("cost_usd") or chars * rate)
        return CostEstimate(
            modality=modality,
            provider=resolved_provider,
            model=resolved_model,
            cost_usd=round(cost, 6),
            units={"characters": chars, "audio_seconds": seconds},
        )

    if modality == "music":
        seconds = float(meta.get("duration_seconds") or params.get("duration_seconds") or 60)
        rate = _rate_for_modality("music", resolved_model)
        cost = float(meta.get("cost_usd") or seconds * rate)
        return CostEstimate(
            modality=modality,
            provider=resolved_provider,
            model=resolved_model,
            cost_usd=round(cost, 6),
            units={"audio_seconds": seconds},
        )

    if modality == "translation":
        source = params.get("source_text") or prompt or ""
        chars = float(meta.get("characters") or len(source))
        inp = int(meta.get("input_tokens") or estimate_tokens(source))
        out = int(meta.get("output_tokens") or estimate_tokens(output_text or ""))
        rate = _rate_for_modality("translation", resolved_model)
        token_cost = estimate_cost_usd(inp, out, resolved_model)
        cost = float(meta.get("cost_usd") or max(chars * rate, token_cost))
        return CostEstimate(
            modality=modality,
            provider=resolved_provider,
            model=resolved_model,
            cost_usd=round(cost, 6),
            units={"characters": chars, "input_tokens": inp, "output_tokens": out},
            input_tokens=inp,
            output_tokens=out,
        )

    inp = estimate_tokens(prompt or "")
    out = estimate_tokens(output_text or "")
    return CostEstimate(
        modality="tokens",
        provider=resolved_provider,
        model=resolved_model,
        cost_usd=estimate_cost_usd(inp, out, resolved_model),
        units={"input_tokens": inp, "output_tokens": out},
        input_tokens=inp,
        output_tokens=out,
    )


def build_cost_telemetry(
    module: str,
    prompt: str | None,
    output_text: str | None,
    meta: dict | None,
    parameters: dict | None,
    *,
    provider: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Enrich meta with full cost intelligence telemetry."""
    meta = dict(meta or {})
    estimate = estimate_modality_cost(
        module,
        prompt=prompt,
        output_text=output_text,
        provider=provider,
        model=model,
        parameters=parameters,
        meta=meta,
    )
    telemetry = {
        "capability": module,
        "modality": estimate.modality,
        "provider": estimate.provider,
        "model": estimate.model,
        "cost_usd": estimate.cost_usd,
        "estimated_cost_usd": estimate.cost_usd,
        "units": estimate.units,
        "input_tokens": estimate.input_tokens,
        "output_tokens": estimate.output_tokens,
    }
    meta.setdefault("telemetry", {}).update(telemetry)
    meta["cost_usd"] = estimate.cost_usd
    return meta


def predict_monthly_spend(
    *,
    mtd_spend_usd: float,
    mtd_requests: int,
    days_elapsed: int,
    days_in_month: int,
) -> dict[str, Any]:
    """Linear burn-rate projection for current month."""
    days_elapsed = max(1, days_elapsed)
    daily_rate = mtd_spend_usd / days_elapsed
    projected = daily_rate * days_in_month
    remaining_days = max(0, days_in_month - days_elapsed)
    projected_remaining = daily_rate * remaining_days
    return {
        "mtd_spend_usd": round(mtd_spend_usd, 4),
        "daily_burn_usd": round(daily_rate, 4),
        "projected_month_usd": round(projected, 4),
        "projected_remaining_usd": round(projected_remaining, 4),
        "mtd_requests": mtd_requests,
        "projected_requests": int(mtd_requests / days_elapsed * days_in_month) if mtd_requests else 0,
        "confidence": "linear",
    }


def optimization_recommendations(
    *,
    by_model: list[dict],
    by_provider: list[dict],
    by_module: list[dict],
    cache_savings_usd: float,
    total_cost_usd: float,
) -> list[dict[str, Any]]:
    """Rule-based cost optimization suggestions."""
    tips: list[dict[str, Any]] = []

    if cache_savings_usd > 0:
        tips.append(
            {
                "priority": "info",
                "category": "cache",
                "title": "Response cache is saving costs",
                "detail": f"${cache_savings_usd:.2f} saved this period via cache hits.",
                "action": "Enable cache on high-repeat modules (SEO, translation).",
            }
        )

    if total_cost_usd > 0 and by_model:
        top = by_model[0]
        if top.get("cost_usd", 0) > total_cost_usd * 0.4:
            tips.append(
                {
                    "priority": "high",
                    "category": "model",
                    "title": f"Model '{top.get('label')}' dominates spend",
                    "detail": f"${top.get('cost_usd', 0):.2f} ({top.get('cost_usd', 0) / total_cost_usd * 100:.0f}% of total).",
                    "action": "Switch module policy to 'cheapest' or set max_cost_per_request.",
                }
            )

    expensive_media = [m for m in by_module if m.get("key") in ("video", "image", "voice", "music") and m.get("cost_usd", 0) > 1]
    for m in expensive_media:
        tips.append(
            {
                "priority": "medium",
                "category": "modality",
                "title": f"High {m.get('label')} spend",
                "detail": f"${m.get('cost_usd', 0):.2f} on {m.get('request_count', 0)} requests.",
                "action": "Review duration/resolution settings; enable demo provider in dev.",
            }
        )

    if len(by_provider) > 1:
        costs = sorted(by_provider, key=lambda x: x.get("cost_usd", 0), reverse=True)
        if costs[0].get("cost_usd", 0) > costs[-1].get("cost_usd", 0) * 3:
            tips.append(
                {
                    "priority": "medium",
                    "category": "routing",
                    "title": "Provider cost imbalance",
                    "detail": f"{costs[0].get('label')} costs 3×+ vs {costs[-1].get('label')}.",
                    "action": "Use automatic routing with 'cheapest' selection for non-critical modules.",
                }
            )

    if not tips:
        tips.append(
            {
                "priority": "info",
                "category": "general",
                "title": "Spend is within normal range",
                "detail": "No urgent optimizations detected.",
                "action": "Set budgets with 80% alert thresholds for proactive monitoring.",
            }
        )
    return tips


def route_provider(
    module: str,
    prompt: str,
    *,
    selection_mode: str = "auto",
    primary_model: str | None = None,
    primary_provider: str | None = None,
    max_cost_per_request: float | None = None,
    fallback_chain: list[dict[str, str]] | None = None,
) -> RoutingDecision:
    """Cost-aware provider routing decision."""
    selection = select_model(
        module,
        prompt,
        selection_mode=selection_mode,
        primary_model=primary_model,
        primary_provider=primary_provider,
        max_cost_per_request=max_cost_per_request,
    )
    chain = list(fallback_chain or [])
    if not chain:
        from app.domain.ai.cost_optimizer import DEFAULT_FALLBACK_CHAIN

        chain = list(DEFAULT_FALLBACK_CHAIN)

    rationale = f"{selection.selection_mode} routing for {module}: {selection.model} @ ${selection.estimated_cost_usd:.4f}"
    return RoutingDecision(
        provider=selection.provider,
        model=selection.model,
        estimated_cost_usd=selection.estimated_cost_usd,
        selection_mode=selection.selection_mode,
        fallback_chain=chain,
        rationale=rationale,
    )


def provider_pricing_catalog() -> dict[str, Any]:
    """Export pricing tables for dashboard."""
    return {
        "llm_models": {k: {"input_per_token": v[0], "output_per_token": v[1]} for k, v in MODEL_PRICING.items()},
        "image": IMAGE_PRICING,
        "video_per_second": VIDEO_PRICING,
        "voice_per_character": VOICE_PRICING,
        "music_per_second": MUSIC_PRICING,
        "translation_per_character": TRANSLATION_PRICING,
    }


def days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_m = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        next_m = datetime(year, month + 1, 1, tzinfo=timezone.utc)
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    return (next_m - start).days
