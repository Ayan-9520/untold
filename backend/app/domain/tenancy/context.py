"""Request-scoped tenant context and PostgreSQL RLS session variables."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.tenancy.enums import OrganizationRole
from app.domain.tenancy.rbac import org_role_has_permission
from app.models import User
from app.models.studio.tenancy import Organization, OrganizationMember


@dataclass(frozen=True)
class TenantContext:
    organization: Organization
    organization_id: int
    org_role: OrganizationRole
    workspace_id: int | None
    user: User

    @property
    def is_platform_admin(self) -> bool:
        return bool(self.user.is_admin)


class TenantContextService:
    @staticmethod
    def user_has_org_access(db: Session, user_id: int) -> bool:
        return (
            db.query(OrganizationMember.id)
            .filter(OrganizationMember.user_id == user_id)
            .limit(1)
            .first()
            is not None
        )

    @staticmethod
    def get_membership(db: Session, user_id: int, organization_id: int) -> OrganizationMember | None:
        return (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id,
            )
            .first()
        )

    @staticmethod
    def resolve_primary_org_id(db: Session, user_id: int) -> int | None:
        primary = (
            db.query(OrganizationMember)
            .filter(OrganizationMember.user_id == user_id, OrganizationMember.is_primary.is_(True))
            .first()
        )
        if primary:
            return primary.organization_id
        fallback = (
            db.query(OrganizationMember)
            .filter(OrganizationMember.user_id == user_id)
            .order_by(OrganizationMember.joined_at.asc())
            .first()
        )
        return fallback.organization_id if fallback else None

    @staticmethod
    def resolve_organization_id(
        db: Session,
        user: User,
        header_org_id: int | None,
    ) -> int:
        if user.is_admin and header_org_id:
            org = db.query(Organization).filter(Organization.id == header_org_id).first()
            if not org:
                raise NotFoundError("Organization not found")
            return org.id

        if header_org_id:
            membership = TenantContextService.get_membership(db, user.id, header_org_id)
            if not membership:
                raise ForbiddenError("Not a member of this organization")
            return header_org_id

        org_id = TenantContextService.resolve_primary_org_id(db, user.id)
        if org_id is None:
            raise ForbiddenError("No organization context — join or create an organization")
        return org_id

    @staticmethod
    def build_context(
        db: Session,
        user: User,
        *,
        organization_id: int,
        workspace_id: int | None = None,
    ) -> TenantContext:
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise NotFoundError("Organization not found")

        if user.is_admin:
            role = OrganizationRole.OWNER
        else:
            membership = TenantContextService.get_membership(db, user.id, organization_id)
            if not membership:
                raise ForbiddenError("Not a member of this organization")
            role = membership.role

        return TenantContext(
            organization=org,
            organization_id=organization_id,
            org_role=role,
            workspace_id=workspace_id,
            user=user,
        )

    @staticmethod
    def require_org_permission(ctx: TenantContext, permission: str) -> None:
        if ctx.is_platform_admin:
            return
        if not org_role_has_permission(ctx.org_role, permission):
            raise ForbiddenError(f"Missing organization permission: {permission}")

    @staticmethod
    def apply_rls(db: Session, organization_id: int, *, bypass: bool = False) -> None:
        """Set PostgreSQL session variables for row-level security policies."""
        if bypass:
            db.execute(text("SELECT set_config('app.bypass_rls', 'true', true)"))
        else:
            db.execute(text("SELECT set_config('app.bypass_rls', 'false', true)"))
            db.execute(
                text("SELECT set_config('app.current_organization_id', :oid, true)"),
                {"oid": str(organization_id)},
            )

    @staticmethod
    def clear_rls(db: Session) -> None:
        db.execute(text("SELECT set_config('app.current_organization_id', '', true)"))
        db.execute(text("SELECT set_config('app.bypass_rls', 'false', true)"))
