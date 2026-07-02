"""Multi-tenant SaaS API — organizations, teams, workspaces, invitations."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.tenant_deps import get_tenant_context, require_org_permission
from app.db.session import get_db
from app.domain.tenancy.context import TenantContext
from app.models import User
from app.core.deps import get_current_active_user, get_current_studio_user
from app.domain.tenancy.enums import OrganizationRole
from app.schemas.tenancy import (
    BrandingUpdate,
    InvitationAccept,
    InvitationAcceptResponse,
    InvitationCreate,
    InvitationResponse,
    OrganizationCreate,
    OrganizationMemberResponse,
    OrganizationMemberUpdate,
    OrganizationResponse,
    OrganizationUpdate,
    SettingsUpdate,
    TeamCreate,
    TeamResponse,
    TenantAuditEventResponse,
    UsageLimitsResponse,
    WorkspaceCreate,
    WorkspaceResponse,
)
from app.services.tenancy_service import TenancyService

router = APIRouter(prefix="/studio/tenancy", tags=["Tenancy"])


@router.get("/organizations", response_model=list[OrganizationResponse])
def list_organizations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TenancyService.list_user_organizations(db, user)


@router.post("/organizations", response_model=OrganizationResponse, status_code=201)
def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TenancyService.create_organization(db, user, data)


@router.get("/organizations/current", response_model=OrganizationResponse)
def get_current_organization(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    return TenancyService.get_organization(db, ctx)


@router.patch("/organizations/current", response_model=OrganizationResponse)
def update_current_organization(
    data: OrganizationUpdate,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.update")),
):
    return TenancyService.update_organization(db, ctx, data)


@router.get("/organizations/current/usage", response_model=UsageLimitsResponse)
def get_usage(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.read")),
):
    return TenancyService.get_usage(db, ctx)


@router.get("/organizations/current/members", response_model=list[OrganizationMemberResponse])
def list_members(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.read")),
):
    return TenancyService.list_members(db, ctx)


@router.patch("/organizations/current/members/{member_user_id}", response_model=OrganizationMemberResponse)
def update_member(
    member_user_id: int,
    data: OrganizationMemberUpdate,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.members.manage")),
):
    return TenancyService.update_member_role(db, ctx, member_user_id, data.role)


@router.delete("/organizations/current/members/{member_user_id}", status_code=204)
def remove_member(
    member_user_id: int,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.members.manage")),
):
    TenancyService.remove_member(db, ctx, member_user_id)


@router.post("/organizations/current/invitations", response_model=InvitationResponse, status_code=201)
def create_invitation(
    data: InvitationCreate,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.invite")),
):
    raw_token, invite = TenancyService.create_invitation(db, ctx, data)
    response = InvitationResponse.model_validate(invite)
    # Token returned once via response header for production clients (not stored)
    return response


@router.post("/invitations/accept", response_model=InvitationAcceptResponse)
def accept_invitation(
    data: InvitationAccept,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    org = TenancyService.accept_invitation(db, user, data.token)
    member = next(
        (m for m in org.members if m.user_id == user.id),
        None,
    )
    return InvitationAcceptResponse(
        organization_id=org.id,
        organization_slug=org.slug,
        role=member.role if member else OrganizationRole.MEMBER,
    )


@router.get("/organizations/current/teams", response_model=list[TeamResponse])
def list_teams(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("org.read")),
):
    return TenancyService.list_teams(db, ctx)


@router.post("/organizations/current/teams", response_model=TeamResponse, status_code=201)
def create_team(
    data: TeamCreate,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("team.manage")),
):
    return TenancyService.create_team(db, ctx, data)


@router.get("/organizations/current/workspaces", response_model=list[WorkspaceResponse])
def list_workspaces(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("workspace.read")),
):
    return TenancyService.list_workspaces(db, ctx)


@router.post("/organizations/current/workspaces", response_model=WorkspaceResponse, status_code=201)
def create_workspace(
    data: WorkspaceCreate,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("workspace.manage")),
):
    return TenancyService.create_workspace(db, ctx, data)


@router.patch("/organizations/current/branding", response_model=OrganizationResponse)
def update_branding(
    data: BrandingUpdate,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("branding.manage")),
):
    branding = data.branding.model_dump(exclude_none=True) if data.branding else None
    white_label = data.white_label.model_dump(exclude_none=True) if data.white_label else None
    return TenancyService.update_branding(db, ctx, branding, white_label)


@router.patch("/organizations/current/settings", response_model=OrganizationResponse)
def update_settings(
    data: SettingsUpdate,
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("settings.manage")),
):
    return TenancyService.update_settings(db, ctx, data.settings.model_dump())


@router.get("/organizations/current/audit", response_model=list[TenantAuditEventResponse])
def list_audit(
    db: Session = Depends(get_db),
    ctx: TenantContext = Depends(require_org_permission("audit.read")),
    limit: int = Query(100, ge=1, le=500),
):
    events = TenancyService.list_audit_events(db, ctx, limit=limit)
    return [TenantAuditEventResponse.model_validate(e) for e in events]
