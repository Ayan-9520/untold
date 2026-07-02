"""Enterprise compliance REST API — GDPR, consent, retention, privacy, access logs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, get_current_admin, get_optional_user
from app.core.exceptions import BadRequestError
from app.db.session import get_db
from app.models import User
from app.schemas.compliance import (
    CompliancePolicyResponse,
    CompliancePolicyUpdate,
    ConsentRecordRequest,
    ConsentRecordResponse,
    FullComplianceReportResponse,
    AccessLogResponse,
    PrivacyRequestCreate,
    PrivacyRequestResponse,
    PrivacyRequestUpdate,
)
from app.services.compliance_service import ComplianceService

router = APIRouter(prefix="/compliance", tags=["Enterprise Compliance"])
admin_router = APIRouter(prefix="/studio/platform/compliance", tags=["Enterprise Compliance"])


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


# --- Public / authenticated privacy endpoints ---

@router.get("/privacy")
def privacy_notice():
    return ComplianceService.privacy_notice()


@router.get("/policies", response_model=list[CompliancePolicyResponse])
def public_retention_summary(db: Session = Depends(get_db)):
    """Public summary of retention policies (no secrets)."""
    ComplianceService.ensure_default_policies(db)
    from app.models.studio.compliance import CompliancePolicy

    policies = db.query(CompliancePolicy).filter(CompliancePolicy.enabled.is_(True)).order_by(CompliancePolicy.policy_key).all()
    return [ComplianceService._policy_dict(p) for p in policies]


@router.post("/consent", response_model=ConsentRecordResponse, status_code=201)
def record_consent(
    data: ConsentRecordRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    if not user and not data.subject_email:
        raise BadRequestError("subject_email required when not authenticated")
    return ComplianceService.record_consent(
        db,
        user=user,
        subject_email=data.subject_email or (user.email if user else None),
        consent_type=data.consent_type,
        granted=data.granted,
        policy_version=data.policy_version,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )


@router.get("/consent/me", response_model=list[ConsentRecordResponse])
def my_consents(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    return ComplianceService.my_consents(db, user)


@router.post("/privacy-requests", response_model=PrivacyRequestResponse, status_code=201)
def submit_privacy_request(
    data: PrivacyRequestCreate,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    if not user and not data.subject_email:
        raise BadRequestError("subject_email required when not authenticated")
    return ComplianceService.submit_privacy_request(
        db,
        user=user,
        subject_email=data.subject_email,
        request_type=data.request_type,
        details=data.details,
    )


# --- Admin compliance console ---

@admin_router.get("/report", response_model=FullComplianceReportResponse)
def compliance_report(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return ComplianceService.get_report(db, user)


@admin_router.get("/policies", response_model=list[CompliancePolicyResponse])
def list_policies(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return ComplianceService.list_policies(db, user)


@admin_router.patch("/policies/{policy_key}", response_model=CompliancePolicyResponse)
def update_policy(
    policy_key: str,
    data: CompliancePolicyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return ComplianceService.update_policy(db, user, policy_key, data)


@admin_router.get("/consents", response_model=list[ConsentRecordResponse])
def list_consents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
    limit: int = Query(100, ge=1, le=500),
):
    return ComplianceService.list_consents(db, user, limit=limit)


@admin_router.get("/privacy-requests", response_model=list[PrivacyRequestResponse])
def list_privacy_requests(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
    status: str | None = None,
    limit: int = Query(100, ge=1, le=500),
):
    return ComplianceService.list_privacy_requests(db, user, status=status, limit=limit)


@admin_router.patch("/privacy-requests/{request_id}", response_model=PrivacyRequestResponse)
def update_privacy_request(
    request_id: int,
    data: PrivacyRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return ComplianceService.update_privacy_request(db, user, request_id, data)


@admin_router.post("/privacy-requests/{request_id}/erasure", response_model=PrivacyRequestResponse)
def process_erasure(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return ComplianceService.process_erasure(db, user, request_id)


@admin_router.post("/privacy-requests/{request_id}/export")
def export_subject_data(
    request_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return ComplianceService.export_subject_data(db, user, request_id)


@admin_router.get("/access-logs", response_model=list[AccessLogResponse])
def list_access_logs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
    limit: int = Query(200, ge=1, le=1000),
):
    return ComplianceService.list_access_logs(db, user, limit=limit)


@admin_router.post("/retention/run")
def run_retention(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return ComplianceService.run_retention(db, user)
