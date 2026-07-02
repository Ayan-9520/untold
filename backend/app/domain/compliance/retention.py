"""Data retention enforcement."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.domain.security.audit import log_audit_event
from app.models.studio.compliance import ComplianceAccessLog, CompliancePolicy

logger = logging.getLogger("untold.compliance.retention")


def purge_expired_access_logs(db: Session, *, policy: CompliancePolicy) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=policy.retention_days)
    q = db.query(ComplianceAccessLog).filter(ComplianceAccessLog.created_at < cutoff)
    count = q.count()
    if count:
        q.delete(synchronize_session=False)
    return count


def run_retention_purge(db: Session) -> dict:
    """Purge data per enabled auto_purge policies."""
    results: dict[str, int] = {}
    policies = db.query(CompliancePolicy).filter(
        CompliancePolicy.enabled.is_(True), CompliancePolicy.auto_purge.is_(True)
    ).all()

    for policy in policies:
        purged = 0
        if policy.data_category == "access":
            purged = purge_expired_access_logs(db, policy=policy)
        results[policy.policy_key] = purged

    total = sum(results.values())
    if total:
        log_audit_event(
            db,
            action="compliance.retention_purge",
            category="compliance",
            severity="info",
            compliance_tags=["GDPR", "SOC2"],
            meta={"purged": results, "total": total},
            commit=False,
        )
    db.commit()
    logger.info("Retention purge completed: %s", results)
    return {"purged": results, "total": total}
