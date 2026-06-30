"""Compliance-grade audit logging."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import User
from app.models.studio_platform import EnterpriseAuditEvent, StudioSecurityLog

COMPLIANCE_FRAMEWORKS = ("SOC2", "GDPR", "HIPAA", "ISO27001")


def _checksum(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def log_audit_event(
    db: Session,
    *,
    action: str,
    actor: User | None = None,
    actor_email: str | None = None,
    category: str = "security",
    severity: str = "info",
    resource_type: str | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    compliance_tags: list[str] | None = None,
    meta: dict | None = None,
    commit: bool = False,
) -> EnterpriseAuditEvent:
    tags = list(compliance_tags or [])
    if category == "security" and "SOC2" not in tags:
        tags.append("SOC2")

    payload = {
        "action": action,
        "actor_id": actor.id if actor else None,
        "actor_email": actor_email or (actor.email if actor else None),
        "resource_type": resource_type,
        "resource_id": resource_id,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    row = EnterpriseAuditEvent(
        actor_id=actor.id if actor else None,
        actor_email=actor_email or (actor.email if actor else None),
        action=action,
        category=category,
        severity=severity,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=(user_agent or "")[:500] or None,
        compliance_tags=tags,
        meta=meta,
        checksum=_checksum(payload),
    )
    db.add(row)
    db.add(
        StudioSecurityLog(
            event_type=action,
            severity=severity,
            user_id=actor.id if actor else None,
            ip_address=ip_address,
            message=f"{action} — {resource_type or 'system'}",
            meta=meta,
        )
    )
    if commit:
        db.commit()
    return row
