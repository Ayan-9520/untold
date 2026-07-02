from collections.abc import Callable, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.core.session_security import validate_token_session
from app.db.session import get_db
from app.domain.studio.rbac import role_has_permission
from app.domain.studio.enums import StudioRole
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError()

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

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise ForbiddenError("Admin access required")
    return current_user


def get_current_studio_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Requires JWT and Studio access (admin, studio_role, or organization member)."""
    user = get_current_user(credentials, db)
    if user.is_admin or user.studio_role:
        return user
    from app.domain.tenancy.context import TenantContextService

    if TenantContextService.user_has_org_access(db, user.id):
        return user
    raise ForbiddenError("Studio access required")


def _resolve_studio_role(user: User, member_role: str | None = None) -> StudioRole:
    if user.is_admin:
        return StudioRole.ADMIN
    if member_role:
        try:
            return StudioRole(member_role)
        except ValueError:
            pass
    if user.studio_role:
        try:
            return StudioRole(user.studio_role)
        except ValueError:
            pass
    return StudioRole.VIEWER


def require_studio_permission(permission: str) -> Callable:
    """Dependency factory: studio user + platform-level permission (no project context)."""

    def _checker(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_studio_user),
    ) -> User:
        from app.domain.studio.permissions import StudioPermissionService

        StudioPermissionService.require_permission(db, user, None, permission)
        return user

    return _checker


def require_project_permission(permission: str) -> Callable:
    """Dependency factory: studio user + project-scoped permission from path `project_id`."""

    def _checker(
        project_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_studio_user),
    ) -> User:
        from app.domain.studio.permissions import StudioPermissionService

        StudioPermissionService.require_permission(db, user, project_id, permission)
        return user

    return _checker


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if not credentials:
        return None
    try:
        return get_current_user(credentials, db)
    except Exception:
        return None
