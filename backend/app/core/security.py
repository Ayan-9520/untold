import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _base_claims(subject: str | int, token_type: str, *, session_id: str | None = None) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "sub": str(subject),
        "iat": now,
        "type": token_type,
        "jti": session_id or str(uuid.uuid4()),
        "iss": settings.jwt_issuer,
    }


def create_access_token(
    subject: str | int,
    extra_claims: dict[str, Any] | None = None,
    *,
    session_id: str | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {**_base_claims(subject, "access", session_id=session_id), "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_mfa_challenge_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    payload = {**_base_claims(user_id, "mfa_challenge"), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str | int, *, session_id: str | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {**_base_claims(subject, "refresh", session_id=session_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc

    token_iss = payload.get("iss")
    if token_iss and token_iss != settings.jwt_issuer:
        raise ValueError("Invalid token issuer")

    return payload
