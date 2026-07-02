"""Unit tests for AI Cost Intelligence."""

import pytest

from app.domain.ai.cost_intelligence import (
    build_cost_telemetry,
    estimate_modality_cost,
    optimization_recommendations,
    predict_monthly_spend,
    route_provider,
)


@pytest.mark.unit
def test_estimate_image_cost():
    est = estimate_modality_cost("image", prompt="hero shot", model="dall-e-3")
    assert est.modality == "image"
    assert est.cost_usd == pytest.approx(0.04, abs=0.001)
    assert est.units["images"] == 1


@pytest.mark.unit
def test_estimate_video_cost():
    est = estimate_modality_cost(
        "video",
        prompt="b-roll",
        model="runway-gen3",
        parameters={"duration_seconds": 10},
    )
    assert est.modality == "video"
    assert est.cost_usd == pytest.approx(0.5, abs=0.01)
    assert est.units["video_seconds"] == 10


@pytest.mark.unit
def test_estimate_voice_cost():
    est = estimate_modality_cost("voice", prompt="Hello world narration", model="elevenlabs-multilingual")
    assert est.modality == "voice"
    assert est.units["characters"] == len("Hello world narration")
    assert est.cost_usd > 0


@pytest.mark.unit
def test_predict_monthly_spend():
    pred = predict_monthly_spend(mtd_spend_usd=100, mtd_requests=50, days_elapsed=10, days_in_month=30)
    assert pred["projected_month_usd"] == pytest.approx(300, abs=1)
    assert pred["daily_burn_usd"] == pytest.approx(10, abs=0.1)


@pytest.mark.unit
def test_route_provider_auto():
    decision = route_provider("script", "Short prompt for test", selection_mode="cheapest")
    assert decision.provider
    assert decision.model
    assert decision.estimated_cost_usd >= 0


@pytest.mark.unit
def test_build_cost_telemetry_tokens():
    meta = build_cost_telemetry("research", "Analyze this match", "Summary text", {}, {})
    assert meta["telemetry"]["modality"] == "tokens"
    assert meta["cost_usd"] >= 0


@pytest.mark.unit
def test_optimization_recommendations():
    tips = optimization_recommendations(
        by_model=[{"key": "gpt-4o", "label": "gpt-4o", "cost_usd": 80, "request_count": 10}],
        by_provider=[],
        by_module=[],
        cache_savings_usd=5,
        total_cost_usd=100,
    )
    assert any(t["category"] == "cache" for t in tips)
    assert any(t["category"] == "model" for t in tips)
