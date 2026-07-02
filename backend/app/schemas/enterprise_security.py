"""Enterprise Security API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SecurityOverviewResponse(BaseModel):
    mfa_enrolled_users: int
    active_sessions: int
    idp_providers_enabled: int
    ip_rules_count: int
    secrets_count: int
    audit_events_24h: int
    security_events_24h: int
    compliance_score: int
    compliance_status: str


class IdpProviderResponse(BaseModel):
    id: int
    slug: str
    name: str
    provider_type: str
    enabled: bool
    is_default: bool
    issuer_url: str | None
    authorization_url: str | None
    saml_sso_url: str | None
    email_domains: list[str]
    scopes: list[str]
    created_at: datetime | None


class IdpProviderCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    provider_type: str = Field(pattern="^(oauth|oidc|saml)$")
    enabled: bool = False
    is_default: bool = False
    client_id: str | None = None
    client_secret: str | None = None
    issuer_url: str | None = None
    authorization_url: str | None = None
    token_url: str | None = None
    userinfo_url: str | None = None
    saml_sso_url: str | None = None
    saml_entity_id: str | None = None
    saml_certificate: str | None = None
    scopes: list[str] = Field(default_factory=lambda: ["openid", "email", "profile"])
    email_domains: list[str] = Field(default_factory=list)


class IdpProviderUpdate(BaseModel):
    name: str | None = None
    enabled: bool | None = None
    is_default: bool | None = None
    client_id: str | None = None
    client_secret: str | None = None
    issuer_url: str | None = None
    authorization_url: str | None = None
    token_url: str | None = None
    userinfo_url: str | None = None
    saml_sso_url: str | None = None
    saml_entity_id: str | None = None
    saml_certificate: str | None = None
    scopes: list[str] | None = None
    email_domains: list[str] | None = None


class MfaSetupResponse(BaseModel):
    provisioning_uri: str
    secret_preview: str
    backup_codes: list[str]


class MfaVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=8)


class MfaChallengeRequest(BaseModel):
    mfa_token: str
    code: str = Field(min_length=6, max_length=16)


class SessionResponse(BaseModel):
    id: int
    session_id: str
    auth_method: str
    ip_address: str | None
    user_agent: str | None
    is_active: bool
    expires_at: datetime
    last_seen_at: datetime | None
    created_at: datetime | None


class IpRuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    rule_type: str = Field(pattern="^(allow|deny)$")
    cidr: str = Field(min_length=3, max_length=64)
    scope: str = "studio"
    notes: str | None = None


class IpRuleResponse(BaseModel):
    id: int
    name: str
    rule_type: str
    cidr: str
    scope: str
    enabled: bool
    notes: str | None
    created_at: datetime | None


class SecretCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    secret_key: str = Field(min_length=1, max_length=120)
    value: str = Field(min_length=1)
    rotation_days: int | None = Field(None, ge=1, le=365)


class SecretResponse(BaseModel):
    id: int
    name: str
    secret_key: str
    version: int
    rotation_days: int | None
    last_rotated_at: datetime | None
    created_at: datetime | None


class AuditEventResponse(BaseModel):
    id: int
    actor_email: str | None
    action: str
    category: str
    severity: str
    resource_type: str | None
    resource_id: str | None
    ip_address: str | None
    compliance_tags: list[str]
    checksum: str | None
    created_at: datetime | None


class ComplianceReportResponse(BaseModel):
    score: int
    status: str
    frameworks: list[str]
    controls: list[dict]
    recommendations: list[str]
    framework_coverage: dict | None = None
    metrics: dict | None = None
    generated_at: str | None = None


class SsoStartResponse(BaseModel):
    authorization_url: str
    provider: str
    state: str


class LoginResponse(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    mfa_required: bool = False
    mfa_token: str | None = None
