"""Enterprise Security REST API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.enterprise_security import (
    AuditEventResponse,
    ComplianceReportResponse,
    IpRuleCreate,
    IpRuleResponse,
    IdpProviderCreate,
    IdpProviderResponse,
    IdpProviderUpdate,
    MfaChallengeRequest,
    MfaSetupResponse,
    MfaVerifyRequest,
    SecretCreate,
    SecretResponse,
    SecurityOverviewResponse,
    SessionResponse,
    SsoStartResponse,
)
from app.schemas.studio_admin import RbacPermission
from app.services.enterprise_security_service import EnterpriseSecurityService

router = APIRouter(prefix="/studio/platform/security", tags=["Enterprise Security"])


class SecretRotateRequest(BaseModel):
    value: str = Field(min_length=1)


class SsoCallbackRequest(BaseModel):
    code: str
    redirect_uri: str


class SamlCallbackRequest(BaseModel):
    SAMLResponse: str


@router.get("/overview", response_model=SecurityOverviewResponse)
def security_overview(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return EnterpriseSecurityService.overview(db, user)


@router.get("/compliance", response_model=ComplianceReportResponse)
def security_compliance(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return EnterpriseSecurityService.get_compliance(db, user)


@router.get("/rbac", response_model=list[RbacPermission])
def security_rbac(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return EnterpriseSecurityService.get_rbac(db, user)


@router.get("/audit", response_model=list[AuditEventResponse])
def security_audit(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
    limit: int = Query(100, ge=1, le=500),
):
    return EnterpriseSecurityService.list_audit(db, user, limit=limit)


@router.get("/idp", response_model=list[IdpProviderResponse])
def list_idp_providers(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return EnterpriseSecurityService.list_idp(db, user)


@router.post("/idp", response_model=IdpProviderResponse, status_code=201)
def create_idp_provider(
    data: IdpProviderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return EnterpriseSecurityService.create_idp(db, user, data)


@router.patch("/idp/{slug}", response_model=IdpProviderResponse)
def update_idp_provider(
    slug: str,
    data: IdpProviderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return EnterpriseSecurityService.update_idp(db, user, slug, data)


@router.get("/mfa/status")
def mfa_status(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return EnterpriseSecurityService.mfa_status(db, user)


@router.post("/mfa/setup", response_model=MfaSetupResponse)
def mfa_setup(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return EnterpriseSecurityService.setup_mfa(db, user)


@router.post("/mfa/verify")
def mfa_verify(
    data: MfaVerifyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return EnterpriseSecurityService.verify_mfa_setup(db, user, data.code)


@router.post("/mfa/disable", status_code=204)
def mfa_disable(
    data: MfaVerifyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    EnterpriseSecurityService.disable_mfa(db, user, data.code)


@router.get("/sessions", response_model=list[SessionResponse])
def list_all_sessions(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return EnterpriseSecurityService.list_sessions(db, user)


@router.get("/sessions/me", response_model=list[SessionResponse])
def list_my_sessions(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return EnterpriseSecurityService.list_my_sessions(db, user)


@router.delete("/sessions/{session_id}", status_code=204)
def revoke_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    EnterpriseSecurityService.revoke_session(db, user, session_id)


@router.post("/sessions/revoke-all")
def revoke_all_sessions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    user_id: int | None = Query(None),
):
    count = EnterpriseSecurityService.revoke_all_sessions(db, user, user_id)
    return {"revoked": count}


@router.get("/ip-rules", response_model=list[IpRuleResponse])
def list_ip_rules(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return EnterpriseSecurityService.list_ip_rules(db, user)


@router.post("/ip-rules", response_model=IpRuleResponse, status_code=201)
def create_ip_rule(
    data: IpRuleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return EnterpriseSecurityService.create_ip_rule(db, user, data)


@router.delete("/ip-rules/{rule_id}", status_code=204)
def delete_ip_rule(rule_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    EnterpriseSecurityService.delete_ip_rule(db, user, rule_id)


@router.get("/secrets", response_model=list[SecretResponse])
def list_secrets(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return EnterpriseSecurityService.list_secrets(db, user)


@router.post("/secrets", response_model=SecretResponse, status_code=201)
def create_secret(
    data: SecretCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return EnterpriseSecurityService.create_secret(db, user, data)


@router.post("/secrets/{secret_id}/rotate", response_model=SecretResponse)
def rotate_secret(
    secret_id: int,
    data: SecretRotateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return EnterpriseSecurityService.rotate_secret(db, user, secret_id, data.value)


@router.delete("/secrets/{secret_id}", status_code=204)
def delete_secret(secret_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    EnterpriseSecurityService.delete_secret(db, user, secret_id)


@router.get("/saml/metadata")
def saml_metadata():
    return Response(content=EnterpriseSecurityService.saml_sp_metadata(), media_type="application/xml")
