"""Project-scoped RBAC — domain service (no service-layer coupling)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError
from app.domain.studio.enums import StudioRole
from app.domain.studio.rbac import resolve_user_studio_role, role_has_permission
from app.models import User
from app.models.studio import StudioProjectMember


class StudioPermissionService:
    """Central permission checks for Studio — used by API deps and application services."""

    @staticmethod
    def member_role(db: Session, user: User, project_id: int) -> StudioRole:
        if user.is_admin:
            return StudioRole.ADMIN
        member = (
            db.query(StudioProjectMember)
            .filter(
                StudioProjectMember.project_id == project_id,
                StudioProjectMember.user_id == user.id,
            )
            .first()
        )
        return resolve_user_studio_role(user.is_admin, member.role.value if member else None)

    @staticmethod
    def require_permission(
        db: Session,
        user: User,
        project_id: int | None,
        permission: str,
    ) -> None:
        if user.is_admin:
            return
        role = StudioRole.VIEWER
        if project_id is not None:
            role = StudioPermissionService.member_role(db, user, project_id)
        if not role_has_permission(role, permission):
            raise ForbiddenError(f"Missing permission: {permission}")
