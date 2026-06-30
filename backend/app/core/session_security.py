"""Shared JWT session revocation checks."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError


def validate_token_session(db: Session, payload: dict[str, Any]) -> None:
    """Reject tokens tied to revoked enterprise sessions."""
    session_id = payload.get("sid") or payload.get("jti")
    if not session_id:
        return
    from app.services.enterprise_security_service import EnterpriseSecurityService

    if not EnterpriseSecurityService.validate_session(db, session_id):
        raise UnauthorizedError("Session revoked or expired")
