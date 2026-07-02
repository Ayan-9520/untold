"""Tenant audit logging — isolated per organization."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.studio.tenancy import TenantAuditEvent


class TenantAuditService:
    @staticmethod
    def log(
        db: Session,
        *,
        organization_id: int,
        user_id: int | None,
        action: str,
        resource_type: str | None = None,
        resource_id: str | int | None = None,
        ip_address: str | None = None,
        meta: dict | None = None,
    ) -> TenantAuditEvent:
        payload = {
            "organization_id": organization_id,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": str(resource_id) if resource_id is not None else None,
            "ts": datetime.now(timezone.utc).isoformat(),
            "meta": meta or {},
        }
        checksum = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        row = TenantAuditEvent(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            ip_address=ip_address,
            meta=meta,
            checksum=checksum,
        )
        db.add(row)
        db.flush()
        return row
