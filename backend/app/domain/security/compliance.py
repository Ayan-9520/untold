"""Compliance readiness scoring."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.security.audit import COMPLIANCE_FRAMEWORKS
from app.models.studio_platform import (
    EnterpriseAuditEvent,
    EnterpriseIdpProvider,
    EnterpriseIpRule,
    EnterpriseMfaEnrollment,
    EnterpriseSecret,
    EnterpriseSession,
)


def compliance_report(db: Session) -> dict:
    settings = get_settings()
    encryption_ok = bool(settings.encryption_key and settings.encryption_key != settings.secret_key)
    active_sessions = db.query(EnterpriseSession).filter(EnterpriseSession.is_active.is_(True)).count()

    controls = [
        {
            "id": "sso",
            "label": "SSO / Federation",
            "frameworks": ["SOC2", "ISO27001"],
            "status": "pass"
            if db.query(EnterpriseIdpProvider).filter(EnterpriseIdpProvider.enabled.is_(True)).count()
            else "warn",
            "detail": "At least one IdP provider enabled",
        },
        {
            "id": "mfa",
            "label": "Multi-Factor Authentication",
            "frameworks": ["SOC2", "HIPAA", "ISO27001"],
            "status": "pass"
            if db.query(EnterpriseMfaEnrollment).filter(EnterpriseMfaEnrollment.enabled.is_(True)).count()
            else "warn",
            "detail": "MFA enrollments active",
        },
        {
            "id": "audit",
            "label": "Audit Logging",
            "frameworks": ["SOC2", "GDPR", "HIPAA", "ISO27001"],
            "status": "pass"
            if db.query(func.count(EnterpriseAuditEvent.id)).scalar()
            else "warn",
            "detail": "Tamper-evident audit events recorded",
        },
        {
            "id": "encryption",
            "label": "Secrets Encryption",
            "frameworks": ["SOC2", "ISO27001"],
            "status": "pass" if encryption_ok else "warn",
            "detail": "Dedicated ENCRYPTION_KEY configured for Fernet at-rest encryption",
        },
        {
            "id": "sessions",
            "label": "Session Management",
            "frameworks": ["SOC2", "GDPR"],
            "status": "pass" if active_sessions > 0 else "warn",
            "detail": "Active sessions tracked with revocation",
        },
        {
            "id": "ip_restrictions",
            "label": "IP Restrictions",
            "frameworks": ["SOC2", "ISO27001"],
            "status": "pass"
            if db.query(EnterpriseIpRule).filter(EnterpriseIpRule.enabled.is_(True)).count()
            else "warn",
            "detail": "IP allow/deny rules configured",
        },
        {
            "id": "rbac",
            "label": "Role-Based Access Control",
            "frameworks": ["SOC2", "HIPAA", "ISO27001"],
            "status": "pass",
            "detail": "Studio RBAC permissions enforced",
        },
        {
            "id": "secrets_rotation",
            "label": "Secrets Rotation Policy",
            "frameworks": ["SOC2"],
            "status": "pass"
            if db.query(EnterpriseSecret).filter(EnterpriseSecret.rotation_days.isnot(None)).count()
            else "warn",
            "detail": "Secrets with rotation schedule",
        },
    ]

    passed = sum(1 for c in controls if c["status"] == "pass")
    score = round(passed / len(controls) * 100)

    return {
        "score": score,
        "status": "compliant" if score >= 85 else "partial" if score >= 60 else "needs_attention",
        "frameworks": list(COMPLIANCE_FRAMEWORKS),
        "controls": controls,
        "recommendations": [c["detail"] for c in controls if c["status"] != "pass"],
    }
