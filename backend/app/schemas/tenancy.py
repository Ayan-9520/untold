"""Pydantic schemas for multi-tenant SaaS API."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.domain.tenancy.enums import (
    InvitationStatus,
    OrganizationPlan,
    OrganizationRole,
    OrganizationStatus,
    TeamRole,
    WorkspaceRole,
)
from app.schemas.common import ORMBase


class OrganizationBranding(BaseModel):
    logo_url: str | None = None
    favicon_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    custom_css: str | None = None


class OrganizationWhiteLabel(BaseModel):
    hide_untold_branding: bool = False
    product_name: str | None = None
    support_email: str | None = None
    custom_domain: str | None = None


class OrganizationSettings(BaseModel):
    timezone: str = "UTC"
    default_language: str = "en"
    require_mfa: bool = False
    allowed_email_domains: list[str] = Field(default_factory=list)


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str | None = Field(default=None, max_length=120, pattern=r"^[a-z0-9-]+$")
    plan: OrganizationPlan = OrganizationPlan.FREE


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    status: OrganizationStatus | None = None


class OrganizationResponse(ORMBase):
    id: int
    slug: str
    name: str
    status: OrganizationStatus
    plan: OrganizationPlan
    seat_limit: int
    seats_used: int
    storage_quota_bytes: int
    storage_used_bytes: int
    api_rate_limit_tier: str
    settings: dict
    branding: dict
    white_label: dict
    usage_limits: dict
    usage_counters: dict
    created_at: datetime | None
    updated_at: datetime | None


class OrganizationMemberResponse(ORMBase):
    user_id: int
    email: str
    full_name: str
    role: OrganizationRole
    is_primary: bool
    joined_at: datetime | None


class OrganizationMemberUpdate(BaseModel):
    role: OrganizationRole


class InvitationCreate(BaseModel):
    email: EmailStr
    role: OrganizationRole = OrganizationRole.MEMBER
    workspace_ids: list[int] | None = None


class InvitationResponse(ORMBase):
    id: int
    email: str
    role: OrganizationRole
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime | None


class InvitationAccept(BaseModel):
    token: str


class InvitationAcceptResponse(BaseModel):
    organization_id: int
    organization_slug: str
    role: OrganizationRole


class TeamCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    slug: str | None = Field(default=None, max_length=120)
    description: str | None = None


class TeamResponse(ORMBase):
    id: int
    organization_id: int
    name: str
    slug: str
    description: str | None
    created_at: datetime | None


class TeamMemberResponse(ORMBase):
    user_id: int
    email: str
    full_name: str
    role: TeamRole
    joined_at: datetime | None


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    slug: str | None = Field(default=None, max_length=120)
    description: str | None = None
    team_id: int | None = None


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    team_id: int | None = None
    settings: dict | None = None


class WorkspaceResponse(ORMBase):
    id: int
    organization_id: int
    team_id: int | None
    name: str
    slug: str
    description: str | None
    settings: dict
    is_default: bool
    created_at: datetime | None


class UsageLimitsResponse(BaseModel):
    plan: OrganizationPlan
    limits: dict
    usage: dict
    seats_used: int
    seat_limit: int
    storage_used_bytes: int
    storage_quota_bytes: int


class BrandingUpdate(BaseModel):
    branding: OrganizationBranding | None = None
    white_label: OrganizationWhiteLabel | None = None


class SettingsUpdate(BaseModel):
    settings: OrganizationSettings


class TenantAuditEventResponse(ORMBase):
    id: int
    organization_id: int
    user_id: int | None
    action: str
    resource_type: str | None
    resource_id: str | None
    ip_address: str | None
    meta: dict | None
    created_at: datetime | None
