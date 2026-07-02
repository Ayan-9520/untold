"""Enterprise compliance service — GDPR, consent, retention, privacy, access logs."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.domain.compliance.policies import (
    CONSENT_TYPES,
    DEFAULT_COMPLIANCE_POLICIES,
    PRIVACY_REQUEST_STATUSES,
    PRIVACY_REQUEST_TYPES,
)
from app.domain.compliance.reports import full_compliance_report
from app.domain.compliance.retention import run_retention_purge
from app.domain.security.audit import log_audit_event
from app.models import User
from app.models.studio.compliance import ComplianceAccessLog, CompliancePolicy, PrivacyRequest, UserConsent
from app.services.studio_admin_service import StudioAdminService


class ComplianceService:
    @staticmethod
    def ensure_default_policies(db: Session) -> None:
        if db.query(CompliancePolicy).count():
            return
        for p in DEFAULT_COMPLIANCE_POLICIES:
            db.add(CompliancePolicy(**p))
        db.commit()

    @staticmethod
    def get_report(db: Session, user: User) -> dict:
        StudioAdminService._require_admin(db, user)
        ComplianceService.ensure_default_policies(db)
        return full_compliance_report(db)

    @staticmethod
    def list_policies(db: Session, user: User) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        ComplianceService.ensure_default_policies(db)
        rows = db.query(CompliancePolicy).order_by(CompliancePolicy.policy_key).all()
        return [ComplianceService._policy_dict(r) for r in rows]

    @staticmethod
    def update_policy(db: Session, user: User, policy_key: str, data) -> dict:
        StudioAdminService._require_admin(db, user, "admin.manage")
        row = db.query(CompliancePolicy).filter(CompliancePolicy.policy_key == policy_key).first()
        if not row:
            raise NotFoundError("Policy not found")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(row, field, value)
        log_audit_event(
            db,
            action="compliance.policy_updated",
            actor=user,
            category="compliance",
            resource_type="policy",
            resource_id=policy_key,
            compliance_tags=["GDPR", "SOC2", "ISO27001"],
            meta=data.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(row)
        return ComplianceService._policy_dict(row)

    @staticmethod
    def record_consent(
        db: Session,
        *,
        user: User | None,
        subject_email: str | None,
        consent_type: str,
        granted: bool,
        policy_version: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        source: str = "web",
        meta: dict | None = None,
    ) -> dict:
        if consent_type not in CONSENT_TYPES:
            raise BadRequestError(f"Invalid consent type. Allowed: {', '.join(CONSENT_TYPES)}")
        settings = get_settings()
        version = policy_version or settings.compliance_privacy_policy_version
        row = UserConsent(
            user_id=user.id if user else None,
            subject_email=subject_email or (user.email if user else None),
            consent_type=consent_type,
            granted=granted,
            policy_version=version,
            ip_address=ip_address,
            user_agent=(user_agent or "")[:500] or None,
            source=source,
            meta=meta,
        )
        db.add(row)
        if user:
            log_audit_event(
                db,
                action="consent.recorded",
                actor=user,
                category="privacy",
                resource_type="consent",
                resource_id=consent_type,
                ip_address=ip_address,
                user_agent=user_agent,
                compliance_tags=["GDPR"],
                meta={"granted": granted, "policy_version": version},
            )
        db.commit()
        db.refresh(row)
        return ComplianceService._consent_dict(row)

    @staticmethod
    def list_consents(db: Session, user: User, *, limit: int = 100) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        rows = db.query(UserConsent).order_by(UserConsent.recorded_at.desc()).limit(limit).all()
        return [ComplianceService._consent_dict(r) for r in rows]

    @staticmethod
    def my_consents(db: Session, user: User) -> list[dict]:
        rows = (
            db.query(UserConsent)
            .filter(UserConsent.user_id == user.id)
            .order_by(UserConsent.recorded_at.desc())
            .limit(50)
            .all()
        )
        return [ComplianceService._consent_dict(r) for r in rows]

    @staticmethod
    def submit_privacy_request(
        db: Session,
        *,
        user: User | None,
        subject_email: str,
        request_type: str,
        details: str | None = None,
    ) -> dict:
        if request_type not in PRIVACY_REQUEST_TYPES:
            raise BadRequestError(f"Invalid request type. Allowed: {', '.join(PRIVACY_REQUEST_TYPES)}")
        due = datetime.now(timezone.utc) + timedelta(days=30)
        row = PrivacyRequest(
            user_id=user.id if user else None,
            subject_email=subject_email.lower(),
            request_type=request_type,
            status="pending",
            details=details,
            due_at=due,
        )
        db.add(row)
        log_audit_event(
            db,
            action="privacy.request_submitted",
            actor=user,
            category="privacy",
            resource_type="privacy_request",
            resource_id=request_type,
            compliance_tags=["GDPR"],
            meta={"subject_email": subject_email, "request_type": request_type},
        )
        db.commit()
        db.refresh(row)
        return ComplianceService._privacy_dict(row)

    @staticmethod
    def list_privacy_requests(db: Session, user: User, *, status: str | None = None, limit: int = 100) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        q = db.query(PrivacyRequest).order_by(PrivacyRequest.created_at.desc())
        if status:
            q = q.filter(PrivacyRequest.status == status)
        rows = q.limit(limit).all()
        return [ComplianceService._privacy_dict(r) for r in rows]

    @staticmethod
    def update_privacy_request(db: Session, user: User, request_id: int, data) -> dict:
        StudioAdminService._require_admin(db, user, "admin.manage")
        row = db.query(PrivacyRequest).filter(PrivacyRequest.id == request_id).first()
        if not row:
            raise NotFoundError("Privacy request not found")
        if data.status and data.status not in PRIVACY_REQUEST_STATUSES:
            raise BadRequestError("Invalid status")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(row, field, value)
        if data.status == "completed":
            row.completed_at = datetime.now(timezone.utc)
            row.assigned_to_id = user.id
        log_audit_event(
            db,
            action="privacy.request_updated",
            actor=user,
            category="privacy",
            resource_type="privacy_request",
            resource_id=str(request_id),
            compliance_tags=["GDPR"],
            meta=data.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(row)
        return ComplianceService._privacy_dict(row)

    @staticmethod
    def process_erasure(db: Session, user: User, request_id: int) -> dict:
        StudioAdminService._require_admin(db, user, "admin.manage")
        row = db.query(PrivacyRequest).filter(PrivacyRequest.id == request_id).first()
        if not row:
            raise NotFoundError("Privacy request not found")
        if row.request_type != "erasure":
            raise BadRequestError("Request is not an erasure request")
        target = db.query(User).filter(User.email == row.subject_email).first()
        if target and target.is_admin:
            raise ForbiddenError("Cannot erase admin accounts via automated erasure")
        if target:
            target.is_active = False
            target.email = f"erased-{target.id}@anonymized.local"
            target.full_name = "Erased User"
            target.hashed_password = ""
        row.status = "completed"
        row.completed_at = datetime.now(timezone.utc)
        row.assigned_to_id = user.id
        row.response_notes = "Account anonymized per GDPR erasure request."
        log_audit_event(
            db,
            action="privacy.erasure_completed",
            actor=user,
            category="privacy",
            severity="warning",
            resource_type="user",
            resource_id=str(target.id if target else "unknown"),
            compliance_tags=["GDPR"],
            meta={"request_id": request_id},
        )
        db.commit()
        db.refresh(row)
        return ComplianceService._privacy_dict(row)

    @staticmethod
    def export_subject_data(db: Session, user: User, request_id: int) -> dict:
        StudioAdminService._require_admin(db, user, "admin.manage")
        row = db.query(PrivacyRequest).filter(PrivacyRequest.id == request_id).first()
        if not row:
            raise NotFoundError("Privacy request not found")
        subject = db.query(User).filter(User.email == row.subject_email).first()
        payload = {
            "subject_email": row.subject_email,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "profile": None,
            "consents": [],
        }
        if subject:
            payload["profile"] = {
                "id": subject.id,
                "email": subject.email,
                "full_name": subject.full_name,
                "created_at": subject.created_at.isoformat() if subject.created_at else None,
            }
            consents = db.query(UserConsent).filter(UserConsent.user_id == subject.id).all()
            payload["consents"] = [ComplianceService._consent_dict(c) for c in consents]
        row.export_uri = f"inline:dsar-{request_id}"
        row.status = "completed"
        row.completed_at = datetime.now(timezone.utc)
        row.assigned_to_id = user.id
        db.commit()
        return {"request_id": request_id, "package": payload}

    @staticmethod
    def list_access_logs(db: Session, user: User, *, limit: int = 200) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        rows = (
            db.query(ComplianceAccessLog).order_by(ComplianceAccessLog.created_at.desc()).limit(limit).all()
        )
        return [ComplianceService._access_dict(r) for r in rows]

    @staticmethod
    def log_access(
        db: Session,
        *,
        user_id: int | None,
        user_email: str | None,
        method: str,
        path: str,
        status_code: int,
        ip_address: str | None,
        user_agent: str | None,
        auth_method: str | None,
        latency_ms: int | None,
    ) -> None:
        row = ComplianceAccessLog(
            user_id=user_id,
            user_email=user_email,
            method=method,
            path=path[:500],
            status_code=status_code,
            ip_address=ip_address,
            user_agent=(user_agent or "")[:500] or None,
            auth_method=auth_method,
            latency_ms=latency_ms,
        )
        db.add(row)
        db.commit()

    @staticmethod
    def run_retention(db: Session, user: User) -> dict:
        StudioAdminService._require_admin(db, user, "admin.manage")
        ComplianceService.ensure_default_policies(db)
        return run_retention_purge(db)

    @staticmethod
    def privacy_notice() -> dict:
        settings = get_settings()
        return {
            "policy_version": settings.compliance_privacy_policy_version,
            "consent_types": list(CONSENT_TYPES),
            "privacy_request_types": list(PRIVACY_REQUEST_TYPES),
            "data_controller": settings.app_name,
            "retention_summary": "See /api/v1/compliance/policies for retention schedules.",
            "contact": "privacy@untold.com",
        }

    @staticmethod
    def _policy_dict(r: CompliancePolicy) -> dict:
        return {
            "id": r.id,
            "policy_key": r.policy_key,
            "name": r.name,
            "description": r.description,
            "data_category": r.data_category,
            "retention_days": r.retention_days,
            "legal_basis": r.legal_basis,
            "frameworks": r.frameworks or [],
            "auto_purge": r.auto_purge,
            "enabled": r.enabled,
            "updated_at": r.updated_at,
        }

    @staticmethod
    def _consent_dict(r: UserConsent) -> dict:
        return {
            "id": r.id,
            "user_id": r.user_id,
            "subject_email": r.subject_email,
            "consent_type": r.consent_type,
            "granted": r.granted,
            "policy_version": r.policy_version,
            "source": r.source,
            "recorded_at": r.recorded_at,
        }

    @staticmethod
    def _privacy_dict(r: PrivacyRequest) -> dict:
        return {
            "id": r.id,
            "user_id": r.user_id,
            "subject_email": r.subject_email,
            "request_type": r.request_type,
            "status": r.status,
            "details": r.details,
            "response_notes": r.response_notes,
            "due_at": r.due_at,
            "completed_at": r.completed_at,
            "created_at": r.created_at,
        }

    @staticmethod
    def _access_dict(r: ComplianceAccessLog) -> dict:
        return {
            "id": r.id,
            "user_email": r.user_email,
            "method": r.method,
            "path": r.path,
            "status_code": r.status_code,
            "ip_address": r.ip_address,
            "auth_method": r.auth_method,
            "latency_ms": r.latency_ms,
            "created_at": r.created_at,
        }
