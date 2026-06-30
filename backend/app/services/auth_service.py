import json
import secrets
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from app.domain.studio.enums import StudioRole
from app.domain.studio.rbac import PERMISSIONS, role_has_permission
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models import (
    Analytics,
    AnalyticsEventType,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    User,
    UserRole,
)
from app.schemas.auth import LoginRequest, RegisterRequest, StudioUserResponse, TokenResponse


class AuthService:
    @staticmethod
    def register(db: Session, data: RegisterRequest) -> User:
        existing = db.query(User).filter(User.email == data.email.lower()).first()
        if existing:
            raise ConflictError("Email already registered")

        user = User(
            email=data.email.lower(),
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            role=UserRole.USER,
        )
        db.add(user)
        db.flush()

        subscription = Subscription(
            user_id=user.id,
            plan=SubscriptionPlan.FREE,
            status=SubscriptionStatus.ACTIVE,
        )
        db.add(subscription)

        event = Analytics(
            event_type=AnalyticsEventType.REGISTER,
            user_id=user.id,
            metadata_json=json.dumps({"email": user.email}),
        )
        db.add(event)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, data: LoginRequest) -> tuple[User, TokenResponse]:
        user = db.query(User).filter(User.email == data.email.lower()).first()
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        tokens = AuthService.create_tokens(user)
        event = Analytics(
            event_type=AnalyticsEventType.LOGIN,
            user_id=user.id,
        )
        db.add(event)
        db.commit()
        return user, tokens

    @staticmethod
    def create_tokens(user: User, *, session_id: str | None = None) -> TokenResponse:
        studio_role = AuthService.resolve_studio_role(user)
        claims = {
            "role": user.role.value,
            "is_admin": user.is_admin,
            "studio_role": studio_role.value,
        }
        if session_id:
            claims["sid"] = session_id
        return TokenResponse(
            access_token=create_access_token(user.id, claims, session_id=session_id),
            refresh_token=create_refresh_token(user.id, session_id=session_id),
        )

    @staticmethod
    def resolve_studio_role(user: User) -> StudioRole:
        if user.is_admin:
            return StudioRole.ADMIN
        if user.studio_role:
            try:
                return StudioRole(user.studio_role)
            except ValueError:
                pass
        return StudioRole.VIEWER

    @staticmethod
    def studio_permissions(user: User) -> list[str]:
        role = AuthService.resolve_studio_role(user)
        return sorted(p for p, roles in PERMISSIONS.items() if role in roles)

    @staticmethod
    def studio_user_response(user: User) -> StudioUserResponse:
        return StudioUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            role=user.role.value,
            studio_role=AuthService.resolve_studio_role(user).value,
            created_at=user.created_at,
            permissions=AuthService.studio_permissions(user),
        )

    @staticmethod
    def require_studio_access(user: User) -> None:
        if user.is_admin:
            return
        if not user.studio_role:
            raise ForbiddenError("Studio access not granted")

    @staticmethod
    def login_google(db: Session, id_token: str) -> tuple[User, TokenResponse]:
        settings = get_settings()
        if not settings.google_client_id:
            raise ForbiddenError("Google login is not configured")

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(
                    "https://oauth2.googleapis.com/tokeninfo",
                    params={"id_token": id_token},
                )
                resp.raise_for_status()
                payload = resp.json()
        except httpx.HTTPError as exc:
            raise UnauthorizedError("Invalid Google token") from exc

        if payload.get("aud") != settings.google_client_id:
            raise UnauthorizedError("Google token audience mismatch")

        google_id = payload.get("sub")
        email = (payload.get("email") or "").lower()
        name = payload.get("name") or email.split("@")[0]
        if not google_id or not email:
            raise UnauthorizedError("Google token missing required claims")

        if settings.studio_allowed_email_domains:
            domain = email.split("@")[-1]
            allowed = {d.strip().lower() for d in settings.studio_allowed_email_domains.split(",") if d.strip()}
            if domain not in allowed:
                raise ForbiddenError("Email domain not authorized for Studio")

        user = db.query(User).filter((User.google_id == google_id) | (User.email == email)).first()
        if user:
            if not user.google_id:
                user.google_id = google_id
            if not user.is_active:
                raise UnauthorizedError("Account is deactivated")
        else:
            user = User(
                email=email,
                full_name=name,
                hashed_password=get_password_hash(secrets.token_urlsafe(32)),
                google_id=google_id,
                studio_role=StudioRole.VIEWER.value,
                role=UserRole.USER,
            )
            db.add(user)
            db.flush()
            db.add(
                Subscription(
                    user_id=user.id,
                    plan=SubscriptionPlan.FREE,
                    status=SubscriptionStatus.ACTIVE,
                )
            )

        if not user.is_admin and not user.studio_role:
            user.studio_role = StudioRole.VIEWER.value

        tokens = AuthService.create_tokens(user)
        db.add(Analytics(event_type=AnalyticsEventType.LOGIN, user_id=user.id, metadata_json=json.dumps({"provider": "google"})))
        db.commit()
        db.refresh(user)
        return user, tokens

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except ValueError as exc:
            raise UnauthorizedError("Invalid refresh token") from exc

        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        user = db.query(User).filter(User.id == int(payload["sub"])).first()
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        session_id = payload.get("sid") or payload.get("jti")
        if session_id:
            from app.services.enterprise_security_service import EnterpriseSecurityService

            if not EnterpriseSecurityService.validate_session(db, session_id):
                raise UnauthorizedError("Session revoked or expired")

        return AuthService.create_tokens(user, session_id=session_id)
