"""Record and derive AI generation telemetry (tokens, latency, cost)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.domain.ai.telemetry import estimate_cost_usd, estimate_tokens, resolve_model
from app.models.studio_platform import AIGeneration


def latency_ms(started_at: datetime | None, completed_at: datetime | None) -> int | None:
    if not started_at or not completed_at:
        return None
    delta = completed_at - started_at
    return max(0, int(delta.total_seconds() * 1000))


def extract_temperature(parameters: dict[str, Any] | None) -> float | None:
    if not parameters:
        return None
    temp = parameters.get("temperature")
    if temp is None:
        return None
    try:
        return float(temp)
    except (TypeError, ValueError):
        return None


def extract_prompt_version(parameters: dict[str, Any] | None) -> str | None:
    if not parameters:
        return None
    for key in ("prompt_version", "version", "template_version"):
        if parameters.get(key) is not None:
            return str(parameters[key])
    return None


def extract_approval_status(gen: AIGeneration) -> str:
    if gen.approval_status and gen.approval_status != "none":
        return gen.approval_status
    params = gen.parameters or {}
    meta = gen.output_meta or {}
    return str(params.get("approval_status") or meta.get("approval_status") or "none")


def apply_create_defaults(gen: AIGeneration) -> None:
    params = gen.parameters or {}
    if gen.temperature is None:
        gen.temperature = extract_temperature(params)
    if not gen.prompt_version:
        gen.prompt_version = extract_prompt_version(params)
    if not gen.approval_status or gen.approval_status == "none":
        approval = params.get("approval_status") or ("pending" if params.get("requires_approval") else "none")
        gen.approval_status = str(approval)


def apply_success(
    gen: AIGeneration,
    *,
    started_at: datetime | None,
    output_text: str | None = None,
    meta: dict[str, Any] | None = None,
    model: str | None = None,
) -> None:
    meta = meta or {}
    completed_at = gen.completed_at or datetime.now(timezone.utc)
    prompt = gen.prompt or ""
    output = output_text if output_text is not None else (gen.output_text or "")

    input_tokens = int(meta.get("input_tokens") or gen.input_tokens or estimate_tokens(prompt))
    output_tokens = int(meta.get("output_tokens") or gen.output_tokens or estimate_tokens(output))
    resolved_model = model or meta.get("model") or gen.model or resolve_model(gen.provider, meta)

    gen.model = resolved_model
    gen.input_tokens = input_tokens
    gen.output_tokens = output_tokens
    gen.latency_ms = int(meta.get("latency_ms") or gen.latency_ms or latency_ms(started_at, completed_at) or 0)
    gen.cost_usd = float(meta.get("cost_usd") or gen.cost_usd or estimate_cost_usd(input_tokens, output_tokens, resolved_model))
    if gen.temperature is None:
        gen.temperature = extract_temperature(gen.parameters)
    if not gen.prompt_version:
        gen.prompt_version = extract_prompt_version(gen.parameters)


def apply_failure(gen: AIGeneration, *, started_at: datetime | None = None) -> None:
    gen.failure_count = (gen.failure_count or 0) + 1
    if started_at and not gen.latency_ms:
        gen.latency_ms = latency_ms(started_at, datetime.now(timezone.utc))


def telemetry_dict(gen: AIGeneration) -> dict[str, Any]:
    meta = gen.output_meta or {}
    params = gen.parameters or {}
    prompt = gen.prompt or ""
    output = gen.output_text or ""
    model = gen.model or meta.get("model") or resolve_model(gen.provider, meta)
    input_tokens = int(gen.input_tokens or meta.get("input_tokens") or estimate_tokens(prompt))
    output_tokens = int(gen.output_tokens or meta.get("output_tokens") or estimate_tokens(output))
    lat = gen.latency_ms if gen.latency_ms is not None else meta.get("latency_ms")
    if lat is None:
        lat = latency_ms(gen.started_at, gen.completed_at)
    cost = gen.cost_usd
    if cost is None:
        cost = meta.get("cost_usd")
    if cost is None:
        cost = estimate_cost_usd(input_tokens, output_tokens, model)

    status_val = gen.status.value if hasattr(gen.status, "value") else str(gen.status)
    failures = gen.failure_count or (1 if status_val == "failed" else 0)

    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": lat,
        "cost_usd": float(cost) if cost is not None else None,
        "failure_count": failures,
        "retries": gen.retry_count or 0,
        "approval_status": extract_approval_status(gen),
        "prompt_version": gen.prompt_version or extract_prompt_version(params),
        "temperature": gen.temperature if gen.temperature is not None else extract_temperature(params),
    }
