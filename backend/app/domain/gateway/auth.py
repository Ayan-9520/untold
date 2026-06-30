"""API Gateway authentication — JWT Bearer or X-API-Key."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.deps import bearer_scheme
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.core.session_security import validate_token_session
from app.db.session import get_db
from app.domain.gateway.scopes import DEFAULT_API_KEY_SCOPES, GATEWAY_SCOPES
from app.domain.gateway.rate_limit import check_rate_limit
from app.models import User
from app.models.studio_platform import StudioApiKey


@dataclass
class GatewayAuth:
    user: User
    api_key: StudioApiKey | None
    auth_type: str  # jwt | api_key
    api_version: str
    scopes: list[str]
    request_id: str | None = None

    def has_scope(self, scope: str) -> bool:
        if self.user.is_admin:
            return True
        return scope in self.scopes

    def require_scope(self, scope: str) -> None:
        if not self.has_scope(scope):
            raise ForbiddenError(f"Missing scope: {scope}")


def _hash_key(secret: str) -> str:
    """SHA-256 hash for API key lookup (keys are high-entropy `unt_*` secrets)."""
    return hashlib.sha256(secret.encode()).hexdigest()


def hash_api_key(secret: str) -> str:
    """Public helper for persisting API key hashes."""
    return _hash_key(secret)


def _resolve_api_key(db: Session, secret: str) -> StudioApiKey:
    if not secret.startswith("unt_"):
        raise UnauthorizedError("Invalid API key format")
    key_hash = _hash_key(secret)
    row = db.query(StudioApiKey).filter(StudioApiKey.key_hash == key_hash, StudioApiKey.is_active.is_(True)).first()
    if not row:
        raise UnauthorizedError("Invalid or revoked API key")
    if row.expires_at and row.expires_at < datetime.now(timezone.utc):
        raise UnauthorizedError("API key expired")
    return row


def _scopes_for_key(row: StudioApiKey) -> list[str]:
    scopes = list(row.scopes or [])
    if not scopes:
        scopes = list(row.permissions or [])
    return [s for s in scopes if s in GATEWAY_SCOPES]


def resolve_gateway_auth(
    request: Request,
    db: Session,
    *,
    credentials=None,
    x_api_key: str | None = None,
    x_api_version: str | None = None,
    accept_version: str | None = None,
) -> GatewayAuth:
    """Authenticate gateway requests via JWT or API key."""
    version = (x_api_version or accept_version or "v1").lower()
    if version not in ("v1", "v2"):
        version = "v1"

    request_id = request.headers.get("X-Request-ID")
    if x_api_key is None:
        x_api_key = request.headers.get("X-API-Key")
    if x_api_version is None:
        x_api_version = request.headers.get("X-API-Version")
    if accept_version is None:
        accept_version = request.headers.get("Accept-Version")
    if credentials is None:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.lower().startswith("bearer "):
            from fastapi.security import HTTPAuthorizationCredentials

            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=auth_header[7:])

    if x_api_key:
        row = _resolve_api_key(db, x_api_key)
        user = db.query(User).filter(User.id == row.created_by_id).first()
        if not user or not user.is_active:
            raise UnauthorizedError("API key owner inactive")
        version = (row.api_version or version).lower()
        auth = GatewayAuth(
            user=user,
            api_key=row,
            auth_type="api_key",
            api_version=version,
            scopes=_scopes_for_key(row),
            request_id=request_id,
        )
        check_rate_limit(api_key=row, auth_type="api_key", identifier=str(row.id))
        request.state.gateway_auth = auth
        return auth

    if credentials and credentials.scheme.lower() == "bearer":
        try:
            payload = decode_token(credentials.credentials)
        except ValueError as exc:
            raise UnauthorizedError() from exc
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError()
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")
        validate_token_session(db, payload)
        scopes = list(GATEWAY_SCOPES.keys()) if user.is_admin else DEFAULT_API_KEY_SCOPES.copy()
        auth = GatewayAuth(
            user=user,
            api_key=None,
            auth_type="jwt",
            api_version=version,
            scopes=scopes,
            request_id=request_id,
        )
        client_ip = request.client.host if request.client else "unknown"
        check_rate_limit(api_key=None, auth_type="jwt", identifier=client_ip)
        request.state.gateway_auth = auth
        return auth

    raise UnauthorizedError("Authentication required — use Bearer token or X-API-Key header")


def get_gateway_auth(
    request: Request,
    db: Session = Depends(get_db),
    credentials=Depends(bearer_scheme),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    x_api_version: str | None = Header(None, alias="X-API-Version"),
    accept_version: str | None = Header(None, alias="Accept-Version"),
) -> GatewayAuth:
    return resolve_gateway_auth(
        request,
        db,
        credentials=credentials,
        x_api_key=x_api_key,
        x_api_version=x_api_version,
        accept_version=accept_version,
    )
