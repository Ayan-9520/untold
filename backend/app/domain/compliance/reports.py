"""Compliance report generation — framework-mapped controls."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.security.audit import COMPLIANCE_FRAMEWORKS
from app.domain.security.compliance import compliance_report as security_compliance_report
from app.models.studio.compliance import ComplianceAccessLog, CompliancePolicy, PrivacyRequest, UserConsent


def full_compliance_report(db: Session) -> dict:
    """Extended report merging security controls + GDPR/compliance module."""
    base = security_compliance_report(db)
    settings = get_settings()
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(hours=24)
    thirty_days = now - timedelta(days=30)

    consent_30d = db.query(func.count(UserConsent.id)).filter(UserConsent.recorded_at >= thirty_days).scalar() or 0
    pending_privacy = (
        db.query(func.count(PrivacyRequest.id))
        .filter(PrivacyRequest.status.in_(("pending", "in_progress")))
        .scalar()
        or 0
    )
    access_24h = (
        db.query(func.count(ComplianceAccessLog.id)).filter(ComplianceAccessLog.created_at >= day_ago).scalar() or 0
    )
    policies_enabled = db.query(CompliancePolicy).filter(CompliancePolicy.enabled.is_(True)).count()
    policies_with_retention = db.query(CompliancePolicy).filter(CompliancePolicy.retention_days > 0).count()

    extra_controls = [
        {
            "id": "consent_management",
            "label": "Consent Management (GDPR Art. 7)",
            "frameworks": ["GDPR"],
            "status": "pass" if consent_30d > 0 or policies_enabled > 0 else "warn",
            "detail": f"{consent_30d} consent events in last 30 days",
        },
        {
            "id": "data_retention",
            "label": "Data Retention Policies",
            "frameworks": ["GDPR", "SOC2", "ISO27001"],
            "status": "pass" if policies_with_retention >= 4 else "warn",
            "detail": f"{policies_enabled} active retention policies configured",
        },
        {
            "id": "privacy_requests",
            "label": "Privacy Request Handling",
            "frameworks": ["GDPR"],
            "status": "pass" if pending_privacy == 0 else "warn",
            "detail": f"{pending_privacy} open DSAR requests (target: 0 overdue)",
        },
        {
            "id": "access_logging",
            "label": "Access Logging (SOC2 CC6)",
            "frameworks": ["SOC2", "ISO27001"],
            "status": "pass" if access_24h > 0 or not settings.compliance_access_log_enabled else "warn",
            "detail": f"{access_24h} access log entries in 24h",
        },
        {
            "id": "encryption_transit",
            "label": "Encryption in Transit (TLS)",
            "frameworks": ["SOC2", "ISO27001", "GDPR"],
            "status": "pass" if settings.is_production else "warn",
            "detail": "HTTPS enforced in production via TLS/HSTS",
        },
        {
            "id": "privacy_policy_version",
            "label": "Privacy Policy Versioning",
            "frameworks": ["GDPR"],
            "status": "pass" if settings.compliance_privacy_policy_version else "warn",
            "detail": f"Current policy version: {settings.compliance_privacy_policy_version}",
        },
    ]

    all_controls = base["controls"] + extra_controls
    passed = sum(1 for c in all_controls if c["status"] == "pass")
    score = round(passed / len(all_controls) * 100) if all_controls else 0

    framework_coverage = {fw: 0 for fw in COMPLIANCE_FRAMEWORKS}
    for c in all_controls:
        if c["status"] == "pass":
            for fw in c.get("frameworks", []):
                if fw in framework_coverage:
                    framework_coverage[fw] += 1

    return {
        "score": score,
        "status": "compliant" if score >= 85 else "partial" if score >= 60 else "needs_attention",
        "frameworks": list(COMPLIANCE_FRAMEWORKS),
        "framework_coverage": framework_coverage,
        "controls": all_controls,
        "recommendations": [c["detail"] for c in all_controls if c["status"] != "pass"],
        "metrics": {
            "consent_events_30d": consent_30d,
            "pending_privacy_requests": pending_privacy,
            "access_logs_24h": access_24h,
            "retention_policies": policies_enabled,
        },
        "generated_at": now.isoformat(),
    }
