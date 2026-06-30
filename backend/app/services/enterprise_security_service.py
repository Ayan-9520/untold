"""Enterprise Security service — SSO, MFA, RBAC, audit, secrets, sessions, compliance."""

from __future__ import annotations

import base64
import hashlib
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_mfa_challenge_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
)
from app.domain.security.audit import log_audit_event
from app.domain.security.compliance import compliance_report
from app.domain.security.encryption import decrypt_value, encrypt_value
from app.domain.security.ip_rules import check_ip_access
from app.domain.security.mfa import (
    encrypt_totp_secret,
    generate_backup_codes,
    generate_totp_secret,
    hash_backup_code,
    totp_provisioning_uri,
    verify_backup_code,
    verify_totp,
)
from app.domain.studio.enums import StudioRole
from app.domain.studio.rbac import PERMISSIONS
from app.models import User
from app.models.studio_platform import (
    EnterpriseAuditEvent,
    EnterpriseIdpProvider,
    EnterpriseIpRule,
    EnterpriseMfaEnrollment,
    EnterpriseSecret,
    EnterpriseSession,
    StudioSecurityLog,
)
from app.schemas.auth import TokenResponse
from app.services.auth_service import AuthService
from app.services.studio_admin_service import StudioAdminService


DEFAULT_IDP_PROVIDERS = [
    {
        "slug": "google",
        "name": "Google Workspace",
        "provider_type": "oidc",
        "enabled": True,
        "is_default": True,
        "issuer_url": "https://accounts.google.com",
        "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://openidconnect.googleapis.com/v1/userinfo",
        "scopes": ["openid", "email", "profile"],
    },
    {
        "slug": "azure-ad",
        "name": "Microsoft Azure AD",
        "provider_type": "oidc",
        "enabled": False,
        "issuer_url": "https://login.microsoftonline.com/{tenant}/v2.0",
        "authorization_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
        "userinfo_url": "https://graph.microsoft.com/oidc/userinfo",
        "scopes": ["openid", "email", "profile"],
    },
    {
        "slug": "okta-saml",
        "name": "Okta SAML",
        "provider_type": "saml",
        "enabled": False,
        "saml_entity_id": "http://www.okta.com/exk...",
        "saml_sso_url": "https://your-org.okta.com/app/untold/exk.../sso/saml",
        "email_domains": [],
    },
]


class EnterpriseSecurityService:
    @staticmethod
    def ensure_defaults(db: Session, admin_user: User | None = None) -> None:
        if db.query(EnterpriseIdpProvider).count():
            return
        for p in DEFAULT_IDP_PROVIDERS:
            db.add(
                EnterpriseIdpProvider(
                    slug=p["slug"],
                    name=p["name"],
                    provider_type=p["provider_type"],
                    enabled=p.get("enabled", False),
                    is_default=p.get("is_default", False),
                    issuer_url=p.get("issuer_url"),
                    authorization_url=p.get("authorization_url"),
                    token_url=p.get("token_url"),
                    userinfo_url=p.get("userinfo_url"),
                    saml_sso_url=p.get("saml_sso_url"),
                    saml_entity_id=p.get("saml_entity_id"),
                    scopes=p.get("scopes", []),
                    email_domains=p.get("email_domains", []),
                    created_by_id=admin_user.id if admin_user else None,
                )
            )
        db.commit()

    @staticmethod
    def overview(db: Session, user: User) -> dict:
        StudioAdminService._require_admin(db, user)
        EnterpriseSecurityService.ensure_defaults(db, user)
        day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
        compliance = compliance_report(db)
        return {
            "mfa_enrolled_users": db.query(EnterpriseMfaEnrollment).filter(EnterpriseMfaEnrollment.enabled.is_(True)).count(),
            "active_sessions": db.query(EnterpriseSession).filter(
                EnterpriseSession.is_active.is_(True), EnterpriseSession.expires_at > datetime.now(timezone.utc)
            ).count(),
            "idp_providers_enabled": db.query(EnterpriseIdpProvider).filter(EnterpriseIdpProvider.enabled.is_(True)).count(),
            "ip_rules_count": db.query(EnterpriseIpRule).filter(EnterpriseIpRule.enabled.is_(True)).count(),
            "secrets_count": db.query(EnterpriseSecret).count(),
            "audit_events_24h": db.query(EnterpriseAuditEvent).filter(EnterpriseAuditEvent.created_at >= day_ago).count(),
            "security_events_24h": db.query(StudioSecurityLog).filter(StudioSecurityLog.created_at >= day_ago).count(),
            "compliance_score": compliance["score"],
            "compliance_status": compliance["status"],
        }

    @staticmethod
    def get_compliance(db: Session, user: User) -> dict:
        StudioAdminService._require_admin(db, user)
        return compliance_report(db)

    @staticmethod
    def get_rbac(db: Session, user: User) -> list[dict]:
        return StudioAdminService.get_rbac(db, user)

    @staticmethod
    def list_audit(db: Session, user: User, *, limit: int = 100) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        rows = db.query(EnterpriseAuditEvent).order_by(EnterpriseAuditEvent.created_at.desc()).limit(limit).all()
        return [EnterpriseSecurityService._audit_dict(r) for r in rows]

    @staticmethod
    def _audit_dict(r: EnterpriseAuditEvent) -> dict:
        return {
            "id": r.id,
            "actor_email": r.actor_email,
            "action": r.action,
            "category": r.category,
            "severity": r.severity,
            "resource_type": r.resource_type,
            "resource_id": r.resource_id,
            "ip_address": r.ip_address,
            "compliance_tags": r.compliance_tags or [],
            "checksum": r.checksum,
            "created_at": r.created_at,
        }

    # --- IdP / SSO ---
    @staticmethod
    def list_idp(db: Session, user: User) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        EnterpriseSecurityService.ensure_defaults(db, user)
        rows = db.query(EnterpriseIdpProvider).order_by(EnterpriseIdpProvider.name).all()
        return [EnterpriseSecurityService._idp_dict(r) for r in rows]

    @staticmethod
    def _idp_dict(r: EnterpriseIdpProvider) -> dict:
        return {
            "id": r.id,
            "slug": r.slug,
            "name": r.name,
            "provider_type": r.provider_type,
            "enabled": r.enabled,
            "is_default": r.is_default,
            "issuer_url": r.issuer_url,
            "authorization_url": r.authorization_url,
            "saml_sso_url": r.saml_sso_url,
            "email_domains": r.email_domains or [],
            "scopes": r.scopes or [],
            "created_at": r.created_at,
        }

    @staticmethod
    def create_idp(db: Session, user: User, data) -> dict:
        StudioAdminService._require_admin(db, user, "admin.manage")
        if db.query(EnterpriseIdpProvider).filter(EnterpriseIdpProvider.slug == data.slug).first():
            raise ConflictError(f"IdP slug exists: {data.slug}")
        row = EnterpriseIdpProvider(
            slug=data.slug,
            name=data.name,
            provider_type=data.provider_type,
            enabled=data.enabled,
            is_default=data.is_default,
            client_id=data.client_id,
            client_secret_encrypted=encrypt_value(data.client_secret) if data.client_secret else None,
            issuer_url=data.issuer_url,
            authorization_url=data.authorization_url,
            token_url=data.token_url,
            userinfo_url=data.userinfo_url,
            saml_sso_url=data.saml_sso_url,
            saml_entity_id=data.saml_entity_id,
            saml_certificate=data.saml_certificate,
            scopes=data.scopes,
            email_domains=data.email_domains,
            created_by_id=user.id,
        )
        db.add(row)
        log_audit_event(db, action="idp.created", actor=user, resource_type="idp", resource_id=data.slug, severity="info")
        db.commit()
        db.refresh(row)
        return EnterpriseSecurityService._idp_dict(row)

    @staticmethod
    def update_idp(db: Session, user: User, slug: str, data) -> dict:
        StudioAdminService._require_admin(db, user, "admin.manage")
        row = EnterpriseSecurityService._get_idp(db, slug)
        updates = data.model_dump(exclude_unset=True)
        if "client_secret" in updates:
            secret = updates.pop("client_secret")
            if secret:
                row.client_secret_encrypted = encrypt_value(secret)
        for k, v in updates.items():
            setattr(row, k, v)
        row.updated_at = datetime.now(timezone.utc)
        log_audit_event(db, action="idp.updated", actor=user, resource_type="idp", resource_id=slug)
        db.commit()
        db.refresh(row)
        return EnterpriseSecurityService._idp_dict(row)

    @staticmethod
    def _get_idp(db: Session, slug: str) -> EnterpriseIdpProvider:
        row = db.query(EnterpriseIdpProvider).filter(EnterpriseIdpProvider.slug == slug).first()
        if not row:
            raise NotFoundError(f"IdP not found: {slug}")
        return row

    @staticmethod
    def start_sso(db: Session, slug: str, *, redirect_uri: str) -> dict:
        provider = EnterpriseSecurityService._get_idp(db, slug)
        if not provider.enabled:
            raise ForbiddenError("SSO provider is disabled")

        state = secrets.token_urlsafe(32)
        if provider.provider_type == "saml":
            if not provider.saml_sso_url:
                raise BadRequestError("SAML SSO URL not configured")
            url = provider.saml_sso_url
            if "?" in url:
                url += f"&RelayState={state}"
            else:
                url += f"?RelayState={state}"
            return {"authorization_url": url, "provider": slug, "state": state}

        if not provider.authorization_url:
            raise BadRequestError("Authorization URL not configured")

        settings = get_settings()
        client_id = provider.client_id or settings.google_client_id
        if not client_id:
            raise BadRequestError("OAuth client_id not configured")

        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(provider.scopes or ["openid", "email", "profile"]),
            "state": state,
        }
        return {
            "authorization_url": f"{provider.authorization_url}?{urlencode(params)}",
            "provider": slug,
            "state": state,
        }

    @staticmethod
    def complete_oauth_sso(
        db: Session,
        slug: str,
        *,
        code: str,
        redirect_uri: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, TokenResponse]:
        provider = EnterpriseSecurityService._get_idp(db, slug)
        if provider.provider_type == "saml":
            raise BadRequestError("Use SAML callback for SAML providers")

        settings = get_settings()
        client_id = provider.client_id or settings.google_client_id
        client_secret = (
            decrypt_value(provider.client_secret_encrypted)
            if provider.client_secret_encrypted
            else settings.google_client_secret
        )
        token_url = provider.token_url
        if not token_url or not client_id:
            raise BadRequestError("OAuth not fully configured")

        with httpx.Client(timeout=15.0) as client:
            token_resp = client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                    "client_secret": client_secret or "",
                },
            )
            token_resp.raise_for_status()
            tokens = token_resp.json()
            access = tokens.get("access_token")
            userinfo_url = provider.userinfo_url or "https://openidconnect.googleapis.com/v1/userinfo"
            ui = client.get(userinfo_url, headers={"Authorization": f"Bearer {access}"})
            ui.raise_for_status()
            profile = ui.json()

        email = (profile.get("email") or "").lower()
        if not email:
            raise UnauthorizedError("SSO profile missing email")

        if provider.email_domains:
            domain = email.split("@")[-1]
            if domain not in provider.email_domains:
                raise ForbiddenError("Email domain not allowed for this IdP")

        if ip_address:
            check_ip_access(db, ip_address)

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                full_name=profile.get("name") or email.split("@")[0],
                hashed_password=get_password_hash(secrets.token_urlsafe(32)),
                studio_role=StudioRole.VIEWER.value,
            )
            db.add(user)
            db.flush()

        return EnterpriseSecurityService._finalize_login(
            db, user, auth_method=f"sso:{slug}", ip_address=ip_address, user_agent=user_agent
        )

    @staticmethod
    def complete_saml_sso(
        db: Session,
        slug: str,
        *,
        saml_response: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, TokenResponse]:
        provider = EnterpriseSecurityService._get_idp(db, slug)
        if provider.provider_type != "saml":
            raise BadRequestError("Provider is not SAML")

        try:
            decoded = base64.b64decode(saml_response).decode("utf-8", errors="ignore")
        except Exception as exc:
            raise UnauthorizedError("Invalid SAML response") from exc

        email_match = re.search(r"<(?:saml2?:)?NameID[^>]*>([^<@]+@[^<]+)</", decoded, re.I)
        if not email_match:
            email_match = re.search(r'NameID[^>]*>([^<@]+@[^<]+)<', decoded, re.I)
        if not email_match:
            raise UnauthorizedError("Could not extract email from SAML assertion")

        email = email_match.group(1).lower()
        if provider.email_domains:
            domain = email.split("@")[-1]
            if domain not in provider.email_domains:
                raise ForbiddenError("Email domain not allowed")

        if ip_address:
            check_ip_access(db, ip_address)

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                full_name=email.split("@")[0],
                hashed_password=get_password_hash(secrets.token_urlsafe(32)),
                studio_role=StudioRole.VIEWER.value,
            )
            db.add(user)
            db.flush()

        log_audit_event(
            db,
            action="sso.saml_login",
            actor=user,
            ip_address=ip_address,
            meta={"provider": slug},
            compliance_tags=["SOC2", "ISO27001"],
        )
        return EnterpriseSecurityService._finalize_login(
            db, user, auth_method=f"saml:{slug}", ip_address=ip_address, user_agent=user_agent
        )

    # --- MFA ---
    @staticmethod
    def setup_mfa(db: Session, user: User) -> dict:
        secret = generate_totp_secret()
        backup = generate_backup_codes()
        encrypted = encrypt_totp_secret(secret)
        row = db.query(EnterpriseMfaEnrollment).filter(EnterpriseMfaEnrollment.user_id == user.id).first()
        if row:
            row.secret_encrypted = encrypted
            row.backup_codes_hash = [hash_backup_code(c) for c in backup]
            row.enabled = False
        else:
            row = EnterpriseMfaEnrollment(
                user_id=user.id,
                secret_encrypted=encrypted,
                backup_codes_hash=[hash_backup_code(c) for c in backup],
                enabled=False,
            )
            db.add(row)
        log_audit_event(db, action="mfa.setup_started", actor=user, severity="info")
        db.commit()
        return {
            "provisioning_uri": totp_provisioning_uri(secret, user.email),
            "secret_preview": f"{secret[:4]}…{secret[-4:]}",
            "backup_codes": backup,
        }

    @staticmethod
    def verify_mfa_setup(db: Session, user: User, code: str) -> dict:
        row = db.query(EnterpriseMfaEnrollment).filter(EnterpriseMfaEnrollment.user_id == user.id).first()
        if not row:
            raise NotFoundError("MFA not initialized")
        if not verify_totp(row.secret_encrypted, code, encrypted=True):
            raise UnauthorizedError("Invalid MFA code")
        row.enabled = True
        row.verified_at = datetime.now(timezone.utc)
        log_audit_event(db, action="mfa.enabled", actor=user, severity="info", compliance_tags=["SOC2"])
        db.commit()
        return {"enabled": True}

    @staticmethod
    def disable_mfa(db: Session, user: User, code: str) -> None:
        row = db.query(EnterpriseMfaEnrollment).filter(EnterpriseMfaEnrollment.user_id == user.id).first()
        if not row or not row.enabled:
            raise NotFoundError("MFA not enabled")
        if not verify_totp(row.secret_encrypted, code, encrypted=True):
            raise UnauthorizedError("Invalid MFA code")
        row.enabled = False
        log_audit_event(db, action="mfa.disabled", actor=user, severity="warn")
        db.commit()

    @staticmethod
    def mfa_status(db: Session, user: User) -> dict:
        row = db.query(EnterpriseMfaEnrollment).filter(EnterpriseMfaEnrollment.user_id == user.id).first()
        return {
            "enabled": bool(row and row.enabled),
            "required": bool(user.mfa_required),
            "verified_at": row.verified_at if row else None,
        }

    @staticmethod
    def verify_mfa_challenge(db: Session, mfa_token: str, code: str, *, ip_address: str | None = None) -> TokenResponse:
        try:
            payload = decode_token(mfa_token)
        except ValueError as exc:
            raise UnauthorizedError("Invalid MFA token") from exc
        if payload.get("type") != "mfa_challenge":
            raise UnauthorizedError("Invalid token type")

        user = db.query(User).filter(User.id == int(payload["sub"])).first()
        if not user or not user.is_active:
            raise UnauthorizedError("User not found")

        row = db.query(EnterpriseMfaEnrollment).filter(
            EnterpriseMfaEnrollment.user_id == user.id, EnterpriseMfaEnrollment.enabled.is_(True)
        ).first()
        if not row:
            raise UnauthorizedError("MFA not enabled")

        valid = verify_totp(row.secret_encrypted, code, encrypted=True)
        if not valid and row.backup_codes_hash:
            valid = verify_backup_code(code.upper(), row.backup_codes_hash)
            if valid:
                row.backup_codes_hash = [h for h in row.backup_codes_hash if h != hash_backup_code(code.upper())]

        if not valid:
            log_audit_event(db, action="mfa.challenge_failed", actor=user, ip_address=ip_address, severity="warn", commit=True)
            raise UnauthorizedError("Invalid MFA code")

        _, tokens = EnterpriseSecurityService._finalize_login(db, user, auth_method="password+mfa", ip_address=ip_address)
        return tokens

    @staticmethod
    def login_with_security(
        db: Session,
        email: str,
        password: str,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        from app.schemas.auth import LoginRequest

        if ip_address:
            check_ip_access(db, ip_address)

        user = db.query(User).filter(User.email == email.lower()).first()
        if not user:
            raise UnauthorizedError("Invalid email or password")

        from app.core.security import verify_password

        if not verify_password(password, user.hashed_password):
            log_audit_event(
                db,
                action="login.failed",
                actor_email=email,
                ip_address=ip_address,
                severity="warn",
                commit=True,
            )
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        mfa = db.query(EnterpriseMfaEnrollment).filter(
            EnterpriseMfaEnrollment.user_id == user.id, EnterpriseMfaEnrollment.enabled.is_(True)
        ).first()
        if mfa or user.mfa_required:
            token = create_mfa_challenge_token(user.id)
            log_audit_event(db, action="login.mfa_required", actor=user, ip_address=ip_address, commit=True)
            return {"mfa_required": True, "mfa_token": token, "access_token": None, "refresh_token": None}

        _, tokens = EnterpriseSecurityService._finalize_login(
            db, user, auth_method="password", ip_address=ip_address, user_agent=user_agent
        )
        return {
            "mfa_required": False,
            "mfa_token": None,
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
        }

    @staticmethod
    def _finalize_login(
        db: Session,
        user: User,
        *,
        auth_method: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[User, TokenResponse]:
        session_id = str(uuid.uuid4())
        settings = get_settings()
        expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

        session = EnterpriseSession(
            user_id=user.id,
            session_id=session_id,
            auth_method=auth_method,
            ip_address=ip_address,
            user_agent=(user_agent or "")[:500] or None,
            expires_at=expires + timedelta(days=settings.refresh_token_expire_days),
        )
        db.add(session)

        user.last_login_ip = ip_address
        user.last_login_at = datetime.now(timezone.utc)

        claims = {
            "role": user.role.value,
            "is_admin": user.is_admin,
            "studio_role": AuthService.resolve_studio_role(user).value,
            "sid": session_id,
        }
        tokens = TokenResponse(
            access_token=create_access_token(user.id, claims, session_id=session_id),
            refresh_token=create_refresh_token(user.id, session_id=session_id),
        )

        log_audit_event(
            db,
            action="login.success",
            actor=user,
            ip_address=ip_address,
            user_agent=user_agent,
            meta={"auth_method": auth_method, "session_id": session_id},
            compliance_tags=["SOC2", "GDPR"],
            commit=False,
        )
        db.commit()
        db.refresh(user)
        return user, tokens

    # --- Sessions ---
    @staticmethod
    def list_sessions(db: Session, user: User) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        rows = (
            db.query(EnterpriseSession)
            .order_by(EnterpriseSession.last_seen_at.desc())
            .limit(200)
            .all()
        )
        return [EnterpriseSecurityService._session_dict(s) for s in rows]

    @staticmethod
    def list_my_sessions(db: Session, user: User) -> list[dict]:
        rows = (
            db.query(EnterpriseSession)
            .filter(EnterpriseSession.user_id == user.id, EnterpriseSession.is_active.is_(True))
            .order_by(EnterpriseSession.last_seen_at.desc())
            .all()
        )
        return [EnterpriseSecurityService._session_dict(s) for s in rows]

    @staticmethod
    def _session_dict(s: EnterpriseSession) -> dict:
        return {
            "id": s.id,
            "session_id": s.session_id[:8] + "…",
            "auth_method": s.auth_method,
            "ip_address": s.ip_address,
            "user_agent": s.user_agent,
            "is_active": s.is_active,
            "expires_at": s.expires_at,
            "last_seen_at": s.last_seen_at,
            "created_at": s.created_at,
        }

    @staticmethod
    def revoke_session(db: Session, user: User, session_db_id: int) -> None:
        row = db.query(EnterpriseSession).filter(EnterpriseSession.id == session_db_id).first()
        if not row:
            raise NotFoundError("Session not found")
        if not user.is_admin and row.user_id != user.id:
            raise ForbiddenError("Cannot revoke this session")
        row.is_active = False
        row.revoked_at = datetime.now(timezone.utc)
        log_audit_event(db, action="session.revoked", actor=user, resource_type="session", resource_id=str(row.id))
        db.commit()

    @staticmethod
    def revoke_all_sessions(db: Session, user: User, target_user_id: int | None = None) -> int:
        uid = target_user_id if user.is_admin and target_user_id else user.id
        if not user.is_admin and uid != user.id:
            raise ForbiddenError("Cannot revoke other user sessions")
        rows = db.query(EnterpriseSession).filter(
            EnterpriseSession.user_id == uid, EnterpriseSession.is_active.is_(True)
        ).all()
        now = datetime.now(timezone.utc)
        for r in rows:
            r.is_active = False
            r.revoked_at = now
        log_audit_event(db, action="session.revoke_all", actor=user, meta={"count": len(rows), "user_id": uid})
        db.commit()
        return len(rows)

    @staticmethod
    def validate_session(db: Session, session_id: str | None) -> bool:
        if not session_id:
            return True
        row = db.query(EnterpriseSession).filter(EnterpriseSession.session_id == session_id).first()
        if not row:
            return True
        return bool(row.is_active and row.expires_at > datetime.now(timezone.utc))

    # --- IP rules ---
    @staticmethod
    def list_ip_rules(db: Session, user: User) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        rows = db.query(EnterpriseIpRule).order_by(EnterpriseIpRule.created_at.desc()).all()
        return [EnterpriseSecurityService._ip_dict(r) for r in rows]

    @staticmethod
    def _ip_dict(r: EnterpriseIpRule) -> dict:
        return {
            "id": r.id,
            "name": r.name,
            "rule_type": r.rule_type,
            "cidr": r.cidr,
            "scope": r.scope,
            "enabled": r.enabled,
            "notes": r.notes,
            "created_at": r.created_at,
        }

    @staticmethod
    def create_ip_rule(db: Session, user: User, data) -> dict:
        StudioAdminService._require_admin(db, user, "admin.manage")
        row = EnterpriseIpRule(
            name=data.name,
            rule_type=data.rule_type,
            cidr=data.cidr,
            scope=data.scope,
            notes=data.notes,
            created_by_id=user.id,
        )
        db.add(row)
        log_audit_event(db, action="ip_rule.created", actor=user, resource_type="ip_rule", meta={"cidr": data.cidr})
        db.commit()
        db.refresh(row)
        return EnterpriseSecurityService._ip_dict(row)

    @staticmethod
    def delete_ip_rule(db: Session, user: User, rule_id: int) -> None:
        StudioAdminService._require_admin(db, user, "admin.manage")
        row = db.query(EnterpriseIpRule).filter(EnterpriseIpRule.id == rule_id).first()
        if not row:
            raise NotFoundError("IP rule not found")
        db.delete(row)
        log_audit_event(db, action="ip_rule.deleted", actor=user, resource_id=str(rule_id))
        db.commit()

    # --- Secrets ---
    @staticmethod
    def list_secrets(db: Session, user: User) -> list[dict]:
        StudioAdminService._require_admin(db, user, "admin.manage")
        rows = db.query(EnterpriseSecret).order_by(EnterpriseSecret.name).all()
        return [EnterpriseSecurityService._secret_dict(r) for r in rows]

    @staticmethod
    def _secret_dict(r: EnterpriseSecret) -> dict:
        return {
            "id": r.id,
            "name": r.name,
            "secret_key": r.secret_key,
            "version": r.version,
            "rotation_days": r.rotation_days,
            "last_rotated_at": r.last_rotated_at,
            "created_at": r.created_at,
        }

    @staticmethod
    def create_secret(db: Session, user: User, data) -> dict:
        StudioAdminService._require_admin(db, user, "admin.manage")
        if db.query(EnterpriseSecret).filter(EnterpriseSecret.secret_key == data.secret_key).first():
            raise ConflictError("Secret key already exists")
        row = EnterpriseSecret(
            name=data.name,
            secret_key=data.secret_key,
            encrypted_value=encrypt_value(data.value),
            rotation_days=data.rotation_days,
            created_by_id=user.id,
        )
        db.add(row)
        log_audit_event(db, action="secret.created", actor=user, resource_type="secret", resource_id=data.secret_key)
        db.commit()
        db.refresh(row)
        return EnterpriseSecurityService._secret_dict(row)

    @staticmethod
    def rotate_secret(db: Session, user: User, secret_id: int, new_value: str) -> dict:
        StudioAdminService._require_admin(db, user, "admin.manage")
        row = db.query(EnterpriseSecret).filter(EnterpriseSecret.id == secret_id).first()
        if not row:
            raise NotFoundError("Secret not found")
        row.encrypted_value = encrypt_value(new_value)
        row.version += 1
        row.last_rotated_at = datetime.now(timezone.utc)
        log_audit_event(db, action="secret.rotated", actor=user, resource_id=row.secret_key)
        db.commit()
        db.refresh(row)
        return EnterpriseSecurityService._secret_dict(row)

    @staticmethod
    def delete_secret(db: Session, user: User, secret_id: int) -> None:
        StudioAdminService._require_admin(db, user, "admin.manage")
        row = db.query(EnterpriseSecret).filter(EnterpriseSecret.id == secret_id).first()
        if not row:
            raise NotFoundError("Secret not found")
        db.delete(row)
        log_audit_event(db, action="secret.deleted", actor=user, resource_id=row.secret_key)
        db.commit()

    @staticmethod
    def get_secret_value(db: Session, user: User, secret_key: str) -> str:
        StudioAdminService._require_admin(db, user, "admin.manage")
        row = db.query(EnterpriseSecret).filter(EnterpriseSecret.secret_key == secret_key).first()
        if not row:
            raise NotFoundError("Secret not found")
        log_audit_event(db, action="secret.accessed", actor=user, resource_id=secret_key, severity="info")
        db.commit()
        return decrypt_value(row.encrypted_value)

    @staticmethod
    def saml_sp_metadata() -> str:
        settings = get_settings()
        entity_id = f"{settings.cors_origin_list[0] if settings.cors_origin_list else 'https://untold.com'}/saml/metadata"
        return f"""<?xml version="1.0"?>
<EntityDescriptor xmlns="urn:oasis:names:tc:SAML:2.0:metadata" entityID="{entity_id}">
  <SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
      Location="{entity_id.replace('/metadata', '/acs')}" index="0"/>
  </SPSSODescriptor>
</EntityDescriptor>"""
