"""User model factories for tests."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash
from app.domain.studio.enums import StudioRole
from app.models import User, UserRole


def build_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
    full_name: str = "Test User",
    is_admin: bool = False,
    studio_role: str | None = None,
    is_active: bool = True,
) -> User:
    return User(
        email=(email or f"user_{uuid.uuid4().hex[:10]}@untold.test").lower(),
        hashed_password=get_password_hash(password),
        full_name=full_name,
        is_admin=is_admin,
        studio_role=studio_role,
        is_active=is_active,
        role=UserRole.ADMIN if is_admin else UserRole.USER,
    )


def create_user(db: Session, **kwargs) -> User:
    user = build_user(**kwargs)
    db.add(user)
    db.flush()
    return user


def create_studio_user(
    db: Session,
    *,
    email: str | None = None,
    role: StudioRole = StudioRole.PRODUCER,
    **kwargs,
) -> User:
    return create_user(
        db,
        email=email,
        studio_role=role.value,
        is_admin=kwargs.pop("is_admin", False),
        **kwargs,
    )


def user_token_headers(user: User) -> dict[str, str]:
    from app.services.auth_service import AuthService

    studio_role = AuthService.resolve_studio_role(user)
    claims = {
        "role": user.role.value,
        "is_admin": user.is_admin,
        "studio_role": studio_role.value,
    }
    token = create_access_token(user.id, claims)
    return {"Authorization": f"Bearer {token}"}
