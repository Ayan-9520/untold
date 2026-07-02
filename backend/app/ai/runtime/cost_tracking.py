"""AI cost tracking helpers."""

from __future__ import annotations

from typing import Any

from app.domain.ai.telemetry import estimate_cost_usd, estimate_tokens, resolve_model


def attach_cost_metadata(
    result: Any,
    *,
    capability: str,
    provider_id: str,
    prompt: str | None = None,
    output_text: str | None = None,
    meta: dict | None = None,
) -> dict[str, Any]:
    """Return telemetry dict suitable for AIGeneration rows and API meta."""
    meta = dict(meta or {})
    if hasattr(result, "meta") and result.meta:
        meta = {**result.meta, **meta}
    inp = estimate_tokens(prompt or "")
    out = estimate_tokens(output_text or getattr(result, "output_text", None) or "")
    model = resolve_model(provider_id, meta)
    cost = estimate_cost_usd(inp, out, model)
    telemetry = {
        "capability": capability,
        "provider": provider_id,
        "model": model,
        "input_tokens": inp,
        "output_tokens": out,
        "estimated_cost_usd": cost,
    }
    meta.setdefault("telemetry", {}).update(telemetry)
    return meta


def record_generation_cost(db, generation_id: int, meta: dict) -> None:
    """Persist cost fields on an AIGeneration row when present."""
    telemetry = (meta or {}).get("telemetry") or meta
    if not telemetry:
        return
    from app.models.studio import AIGeneration

    row = db.query(AIGeneration).filter(AIGeneration.id == generation_id).first()
    if not row:
        return
    if telemetry.get("input_tokens") is not None:
        row.input_tokens = telemetry["input_tokens"]
    if telemetry.get("output_tokens") is not None:
        row.output_tokens = telemetry["output_tokens"]
    if telemetry.get("estimated_cost_usd") is not None:
        row.cost_usd = float(telemetry["estimated_cost_usd"])
    elif telemetry.get("cost_usd") is not None:
        row.cost_usd = float(telemetry["cost_usd"])
    if telemetry.get("model"):
        row.model = telemetry["model"]

    org_id = (meta or {}).get("organization_id")
    if org_id is None and row.project_id:
        from app.models.studio.core import Production

        prod = db.query(Production).filter(Production.id == row.project_id).first()
        org_id = prod.organization_id if prod else None
    if org_id:
        from app.models.studio.billing import UsageMeterType
        from app.services.billing.usage_service import UsageMeterService

        tokens = int(telemetry.get("input_tokens") or 0) + int(telemetry.get("output_tokens") or 0)
        credits = max(1, tokens // 1000) if tokens else 1
        UsageMeterService.record(db, int(org_id), UsageMeterType.AI_CREDITS, float(credits))
