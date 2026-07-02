"""Multi-tenant organization, team, workspace, and invitation services."""

from __future__ import annotations

import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.domain.tenancy.audit import TenantAuditService
from app.domain.tenancy.context import TenantContext
from app.domain.tenancy.enums import (
    InvitationStatus,
    OrganizationPlan,
    OrganizationRole,
    OrganizationStatus,
    TeamRole,
    WorkspaceRole,
)
from app.domain.tenancy.limits import get_plan_limits, merge_usage_limits
from app.models import User
from app.models.studio.core import Production
from app.models.studio.tenancy import (
    Organization,
    OrganizationInvitation,
    OrganizationMember,
    Team,
    TeamMember,
    TenantAuditEvent,
    Workspace,
    WorkspaceMember,
)
from app.schemas.tenancy import (
    InvitationCreate,
    OrganizationCreate,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationUpdate,
    TeamCreate,
    TeamResponse,
    UsageLimitsResponse,
    WorkspaceCreate,
    WorkspaceResponse,
)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:120] or "org"


class TenancyService:
    @staticmethod
    def to_org_response(org: Organization) -> OrganizationResponse:
        return OrganizationResponse.model_validate(org)

    @staticmethod
    def list_user_organizations(db: Session, user: User) -> list[OrganizationResponse]:
        if user.is_admin:
            orgs = db.query(Organization).order_by(Organization.name).all()
        else:
            orgs = (
                db.query(Organization)
                .join(OrganizationMember)
                .filter(OrganizationMember.user_id == user.id)
                .order_by(Organization.name)
                .all()
            )
        return [TenancyService.to_org_response(o) for o in orgs]

    @staticmethod
    def create_organization(db: Session, user: User, data: OrganizationCreate) -> OrganizationResponse:
        slug = data.slug or _slugify(data.name)
        if db.query(Organization).filter(Organization.slug == slug).first():
            raise BadRequestError("Organization slug already exists")

        limits = get_plan_limits(data.plan.value)
        org = Organization(
            slug=slug,
            name=data.name,
            plan=data.plan,
            status=OrganizationStatus.ACTIVE,
            seat_limit=limits["seats"],
            storage_quota_bytes=limits["storage_gb"] * 1_073_741_824,
            usage_limits=limits,
        )
        db.add(org)
        db.flush()

        db.add(
            OrganizationMember(
                organization_id=org.id,
                user_id=user.id,
                role=OrganizationRole.OWNER,
                is_primary=True,
            )
        )
        ws = Workspace(
            organization_id=org.id,
            name="Default",
            slug="default",
            description="Default workspace",
            is_default=True,
        )
        db.add(ws)
        org.seats_used = 1
        db.flush()

        TenantAuditService.log(
            db,
            organization_id=org.id,
            user_id=user.id,
            action="organization.created",
            resource_type="organization",
            resource_id=org.id,
        )
        db.commit()
        db.refresh(org)
        return TenancyService.to_org_response(org)

    @staticmethod
    def get_organization(db: Session, ctx: TenantContext) -> OrganizationResponse:
        return TenancyService.to_org_response(ctx.organization)

    @staticmethod
    def update_organization(db: Session, ctx: TenantContext, data: OrganizationUpdate) -> OrganizationResponse:
        org = ctx.organization
        if data.name is not None:
            org.name = data.name
        if data.status is not None and ctx.is_platform_admin:
            org.status = data.status
        db.commit()
        db.refresh(org)
        return TenancyService.to_org_response(org)

    @staticmethod
    def get_usage(db: Session, ctx: TenantContext) -> UsageLimitsResponse:
        org = ctx.organization
        limits = merge_usage_limits(org.plan.value, org.usage_limits or None)
        project_count = (
            db.query(func.count(Production.id)).filter(Production.organization_id == org.id).scalar() or 0
        )
        workspace_count = (
            db.query(func.count(Workspace.id)).filter(Workspace.organization_id == org.id).scalar() or 0
        )
        usage = dict(org.usage_counters or {})
        usage.update(
            {
                "projects": int(project_count),
                "workspaces": int(workspace_count),
            }
        )
        return UsageLimitsResponse(
            plan=org.plan,
            limits=limits,
            usage=usage,
            seats_used=org.seats_used,
            seat_limit=org.seat_limit,
            storage_used_bytes=org.storage_used_bytes,
            storage_quota_bytes=org.storage_quota_bytes,
        )

    @staticmethod
    def list_members(db: Session, ctx: TenantContext) -> list[OrganizationMemberResponse]:
        rows = (
            db.query(OrganizationMember, User)
            .join(User, User.id == OrganizationMember.user_id)
            .filter(OrganizationMember.organization_id == ctx.organization_id)
            .all()
        )
        return [
            OrganizationMemberResponse(
                user_id=u.id,
                email=u.email,
                full_name=u.full_name,
                role=m.role,
                is_primary=m.is_primary,
                joined_at=m.joined_at,
            )
            for m, u in rows
        ]

    @staticmethod
    def update_member_role(
        db: Session, ctx: TenantContext, member_user_id: int, role: OrganizationRole
    ) -> OrganizationMemberResponse:
        if member_user_id == ctx.user.id and role != ctx.org_role:
            raise BadRequestError("Cannot change your own role via this endpoint")
        member = (
            db.query(OrganizationMember, User)
            .join(User, User.id == OrganizationMember.user_id)
            .filter(
                OrganizationMember.organization_id == ctx.organization_id,
                OrganizationMember.user_id == member_user_id,
            )
            .first()
        )
        if not member:
            raise NotFoundError("Member not found")
        m, u = member
        m.role = role
        TenantAuditService.log(
            db,
            organization_id=ctx.organization_id,
            user_id=ctx.user.id,
            action="organization.member.role_updated",
            resource_type="user",
            resource_id=member_user_id,
            meta={"role": role.value},
        )
        db.commit()
        return OrganizationMemberResponse(
            user_id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=m.role,
            is_primary=m.is_primary,
            joined_at=m.joined_at,
        )

    @staticmethod
    def remove_member(db: Session, ctx: TenantContext, member_user_id: int) -> None:
        member = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == ctx.organization_id,
                OrganizationMember.user_id == member_user_id,
            )
            .first()
        )
        if not member:
            raise NotFoundError("Member not found")
        if member.role == OrganizationRole.OWNER:
            owners = (
                db.query(OrganizationMember)
                .filter(
                    OrganizationMember.organization_id == ctx.organization_id,
                    OrganizationMember.role == OrganizationRole.OWNER,
                )
                .count()
            )
            if owners <= 1:
                raise BadRequestError("Cannot remove the last owner")
        db.delete(member)
        org = ctx.organization
        org.seats_used = max(0, org.seats_used - 1)
        TenantAuditService.log(
            db,
            organization_id=ctx.organization_id,
            user_id=ctx.user.id,
            action="organization.member.removed",
            resource_type="user",
            resource_id=member_user_id,
        )
        db.commit()

    @staticmethod
    def create_invitation(db: Session, ctx: TenantContext, data: InvitationCreate) -> tuple[str, OrganizationInvitation]:
        org = ctx.organization
        if org.seats_used >= org.seat_limit:
            raise ForbiddenError("Seat limit reached — upgrade plan or remove members")

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        invite = OrganizationInvitation(
            organization_id=ctx.organization_id,
            email=data.email.lower(),
            role=data.role,
            token_hash=token_hash,
            status=InvitationStatus.PENDING,
            workspace_ids=data.workspace_ids,
            invited_by_id=ctx.user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(invite)
        TenantAuditService.log(
            db,
            organization_id=ctx.organization_id,
            user_id=ctx.user.id,
            action="organization.invitation.created",
            resource_type="invitation",
            meta={"email": data.email},
        )
        db.commit()
        db.refresh(invite)
        return raw_token, invite

    @staticmethod
    def accept_invitation(db: Session, user: User, token: str) -> Organization:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        invite = (
            db.query(OrganizationInvitation)
            .filter(
                OrganizationInvitation.token_hash == token_hash,
                OrganizationInvitation.status == InvitationStatus.PENDING,
            )
            .first()
        )
        if not invite:
            raise BadRequestError("Invalid or expired invitation")
        if invite.expires_at < datetime.now(timezone.utc):
            invite.status = InvitationStatus.EXPIRED
            db.commit()
            raise BadRequestError("Invitation expired")
        if user.email.lower() != invite.email.lower():
            raise ForbiddenError("Invitation email does not match your account")

        existing = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == invite.organization_id,
                OrganizationMember.user_id == user.id,
            )
            .first()
        )
        if not existing:
            db.add(
                OrganizationMember(
                    organization_id=invite.organization_id,
                    user_id=user.id,
                    role=invite.role,
                    is_primary=False,
                )
            )
            org = db.query(Organization).filter(Organization.id == invite.organization_id).first()
            if org:
                org.seats_used += 1

        if invite.workspace_ids:
            for wid in invite.workspace_ids:
                if not db.query(WorkspaceMember).filter(
                    WorkspaceMember.workspace_id == wid, WorkspaceMember.user_id == user.id
                ).first():
                    db.add(WorkspaceMember(workspace_id=wid, user_id=user.id))

        invite.status = InvitationStatus.ACCEPTED
        invite.accepted_at = datetime.now(timezone.utc)
        if not user.studio_role:
            user.studio_role = "viewer"

        TenantAuditService.log(
            db,
            organization_id=invite.organization_id,
            user_id=user.id,
            action="organization.invitation.accepted",
            resource_type="invitation",
            resource_id=invite.id,
        )
        db.commit()
        org = db.query(Organization).filter(Organization.id == invite.organization_id).first()
        if not org:
            raise NotFoundError("Organization not found")
        return org

    @staticmethod
    def list_teams(db: Session, ctx: TenantContext) -> list[TeamResponse]:
        teams = (
            db.query(Team)
            .filter(Team.organization_id == ctx.organization_id)
            .order_by(Team.name)
            .all()
        )
        return [TeamResponse.model_validate(t) for t in teams]

    @staticmethod
    def create_team(db: Session, ctx: TenantContext, data: TeamCreate) -> TeamResponse:
        slug = data.slug or _slugify(data.name)
        team = Team(
            organization_id=ctx.organization_id,
            name=data.name,
            slug=slug,
            description=data.description,
        )
        db.add(team)
        db.flush()
        db.add(TeamMember(team_id=team.id, user_id=ctx.user.id, role=TeamRole.LEAD))
        TenantAuditService.log(
            db,
            organization_id=ctx.organization_id,
            user_id=ctx.user.id,
            action="team.created",
            resource_type="team",
            resource_id=team.id,
        )
        db.commit()
        db.refresh(team)
        return TeamResponse.model_validate(team)

    @staticmethod
    def list_workspaces(db: Session, ctx: TenantContext) -> list[WorkspaceResponse]:
        q = db.query(Workspace).filter(Workspace.organization_id == ctx.organization_id)
        if ctx.workspace_id and not ctx.is_platform_admin:
            q = q.filter(Workspace.id == ctx.workspace_id)
        workspaces = q.order_by(Workspace.name).all()
        return [WorkspaceResponse.model_validate(w) for w in workspaces]

    @staticmethod
    def create_workspace(db: Session, ctx: TenantContext, data: WorkspaceCreate) -> WorkspaceResponse:
        limits = merge_usage_limits(ctx.organization.plan.value, ctx.organization.usage_limits or None)
        count = (
            db.query(func.count(Workspace.id))
            .filter(Workspace.organization_id == ctx.organization_id)
            .scalar()
            or 0
        )
        if count >= limits.get("workspaces", 1):
            raise ForbiddenError("Workspace limit reached for current plan")

        slug = data.slug or _slugify(data.name)
        ws = Workspace(
            organization_id=ctx.organization_id,
            team_id=data.team_id,
            name=data.name,
            slug=slug,
            description=data.description,
        )
        db.add(ws)
        db.flush()
        db.add(WorkspaceMember(workspace_id=ws.id, user_id=ctx.user.id, role=WorkspaceRole.ADMIN))
        TenantAuditService.log(
            db,
            organization_id=ctx.organization_id,
            user_id=ctx.user.id,
            action="workspace.created",
            resource_type="workspace",
            resource_id=ws.id,
        )
        db.commit()
        db.refresh(ws)
        return WorkspaceResponse.model_validate(ws)

    @staticmethod
    def update_branding(db: Session, ctx: TenantContext, branding: dict | None, white_label: dict | None) -> OrganizationResponse:
        org = ctx.organization
        if branding is not None:
            org.branding = {**(org.branding or {}), **branding}
        if white_label is not None:
            org.white_label = {**(org.white_label or {}), **white_label}
        db.commit()
        db.refresh(org)
        return TenancyService.to_org_response(org)

    @staticmethod
    def update_settings(db: Session, ctx: TenantContext, settings: dict) -> OrganizationResponse:
        org = ctx.organization
        org.settings = {**(org.settings or {}), **settings}
        db.commit()
        db.refresh(org)
        return TenancyService.to_org_response(org)

    @staticmethod
    def list_audit_events(db: Session, ctx: TenantContext, limit: int = 100) -> list[TenantAuditEvent]:
        return (
            db.query(TenantAuditEvent)
            .filter(TenantAuditEvent.organization_id == ctx.organization_id)
            .order_by(TenantAuditEvent.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def enforce_project_limit(db: Session, organization_id: int) -> None:
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            return
        limits = merge_usage_limits(org.plan.value, org.usage_limits or None)
        count = db.query(func.count(Production.id)).filter(Production.organization_id == organization_id).scalar() or 0
        if count >= limits.get("projects", 5):
            raise ForbiddenError("Project limit reached for organization plan")

    @staticmethod
    def default_workspace_id(db: Session, organization_id: int) -> int | None:
        ws = (
            db.query(Workspace)
            .filter(Workspace.organization_id == organization_id, Workspace.is_default.is_(True))
            .first()
        )
        if ws:
            return ws.id
        return (
            db.query(Workspace.id)
            .filter(Workspace.organization_id == organization_id)
            .order_by(Workspace.id.asc())
            .limit(1)
            .scalar()
        )
