"""Enterprise Security auth extensions — SSO, MFA challenge."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.core.config import get_settings
from app.schemas.enterprise_security import LoginResponse, MfaChallengeRequest, SsoStartResponse
from app.schemas.auth import LoginRequest
from app.services.enterprise_security_service import EnterpriseSecurityService

router = APIRouter(prefix="/auth/security", tags=["Enterprise Security Auth"])
settings = get_settings()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post("/login", response_model=LoginResponse)
@limiter.limit(settings.rate_limit_auth)
def secure_login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    return EnterpriseSecurityService.login_with_security(
        db,
        data.email,
        data.password,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )


@router.post("/mfa/verify", response_model=LoginResponse)
@limiter.limit(settings.rate_limit_auth)
def mfa_challenge(request: Request, data: MfaChallengeRequest, db: Session = Depends(get_db)):
    tokens = EnterpriseSecurityService.verify_mfa_challenge(
        db, data.mfa_token, data.code, ip_address=_client_ip(request)
    )
    return LoginResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.get("/sso/{slug}/start", response_model=SsoStartResponse)
def sso_start(
    slug: str,
    redirect_uri: str = Query(...),
    db: Session = Depends(get_db),
):
    return EnterpriseSecurityService.start_sso(db, slug, redirect_uri=redirect_uri)


@router.post("/sso/{slug}/callback", response_model=LoginResponse)
@limiter.limit(settings.rate_limit_auth)
def sso_oauth_callback(
    slug: str,
    request: Request,
    code: str = Query(...),
    redirect_uri: str = Query(...),
    db: Session = Depends(get_db),
):
    _, tokens = EnterpriseSecurityService.complete_oauth_sso(
        db,
        slug,
        code=code,
        redirect_uri=redirect_uri,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    return LoginResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.post("/sso/{slug}/saml/acs", response_model=LoginResponse)
@limiter.limit(settings.rate_limit_auth)
def sso_saml_acs(
    slug: str,
    request: Request,
    SAMLResponse: str = Query(...),
    db: Session = Depends(get_db),
):
    _, tokens = EnterpriseSecurityService.complete_saml_sso(
        db,
        slug,
        saml_response=SAMLResponse,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    return LoginResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)
