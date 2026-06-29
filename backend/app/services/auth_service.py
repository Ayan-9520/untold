import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
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
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


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
    def create_tokens(user: User) -> TokenResponse:
        claims = {"role": user.role.value, "is_admin": user.is_admin}
        return TokenResponse(
            access_token=create_access_token(user.id, claims),
            refresh_token=create_refresh_token(user.id),
        )

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

        return AuthService.create_tokens(user)
