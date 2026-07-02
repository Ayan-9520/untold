"""Unit tests for public developer platform."""

import pytest

from app.core.exceptions import BadRequestError
from app.domain.gateway.scopes import DEVELOPER_ACCOUNT_TIERS, GATEWAY_SCOPES, RATE_LIMIT_TIERS, SUPPORTED_VERSIONS
from app.domain.gateway.webhook_validation import validate_webhook_url
from app.gateway.sandbox import SANDBOX_VIDEOS
from app.services.developer_platform_service import DeveloperPlatformService


@pytest.mark.unit
def test_platform_docs_structure():
    docs = DeveloperPlatformService.platform_docs()
    assert docs["title"] == "UNTOLD Developer Platform"
    assert "production" in docs["environments"]
    assert "sandbox" in docs["environments"]
    assert docs["protocols"] == ["REST", "GraphQL"]


@pytest.mark.unit
def test_sandbox_info():
    info = DeveloperPlatformService.sandbox_info()
    assert info["environment"] == "sandbox"
    assert list(SUPPORTED_VERSIONS)[0] in info["supported_versions"]


@pytest.mark.unit
def test_gateway_scope_catalog():
    assert "videos.read" in GATEWAY_SCOPES
    assert "graphql.query" in GATEWAY_SCOPES
    assert "free" in RATE_LIMIT_TIERS


@pytest.mark.unit
def test_developer_account_tier_limits():
    free = DEVELOPER_ACCOUNT_TIERS["free"]
    assert free["max_active_keys"] == 3
    assert free["allowed_rate_tiers"] == frozenset({"free"})
    enterprise = DEVELOPER_ACCOUNT_TIERS["enterprise"]
    assert "enterprise" in enterprise["allowed_rate_tiers"]


@pytest.mark.unit
def test_webhook_url_validation_rejects_private_ips():
    with pytest.raises(BadRequestError):
        validate_webhook_url("https://10.0.0.1/hook")


@pytest.mark.unit
def test_webhook_url_validation_accepts_public_https():
    assert validate_webhook_url("https://example.com/webhooks/untold").startswith("https://")


@pytest.mark.unit
def test_sandbox_sample_data_isolated():
    assert all(v["id"] >= 9000 for v in SANDBOX_VIDEOS)
