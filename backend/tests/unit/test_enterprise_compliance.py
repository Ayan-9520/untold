"""Unit tests for enterprise compliance."""

import pytest

from app.domain.compliance.policies import (
    CONSENT_TYPES,
    DEFAULT_COMPLIANCE_POLICIES,
    PRIVACY_REQUEST_TYPES,
)
from app.services.compliance_service import ComplianceService


@pytest.mark.unit
def test_default_policies_cover_frameworks():
    frameworks = set()
    for p in DEFAULT_COMPLIANCE_POLICIES:
        frameworks.update(p["frameworks"])
    assert "GDPR" in frameworks
    assert "SOC2" in frameworks
    assert "ISO27001" in frameworks


@pytest.mark.unit
def test_consent_types_defined():
    assert "essential" in CONSENT_TYPES
    assert "analytics" in CONSENT_TYPES
    assert "marketing" in CONSENT_TYPES


@pytest.mark.unit
def test_privacy_request_types_gdpr():
    assert "access" in PRIVACY_REQUEST_TYPES
    assert "erasure" in PRIVACY_REQUEST_TYPES
    assert "portability" in PRIVACY_REQUEST_TYPES


@pytest.mark.unit
def test_privacy_notice_structure():
    notice = ComplianceService.privacy_notice()
    assert "policy_version" in notice
    assert "consent_types" in notice
    assert notice["contact"]
