"""Public developer platform API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DeveloperRegister(BaseModel):
    company_name: str | None = Field(None, max_length=200)
    website: str | None = Field(None, max_length=500)


class DeveloperAccountResponse(BaseModel):
    id: int
    user_id: int
    company_name: str | None
    website: str | None
    tier: str
    sandbox_enabled: bool
    approved_at: datetime | None
    created_at: datetime | None


class DeveloperApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    scopes: list[str] = Field(default_factory=list)
    environment: str = Field(default="production", pattern="^(sandbox|production)$")
    rate_limit_tier: str = "standard"
    api_version: str = "v1"
    expires_at: datetime | None = None


class DeveloperApiKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    environment: str
    scopes: list[str]
    rate_limit_tier: str
    api_version: str
    is_active: bool
    total_requests: int
    last_used_at: datetime | None
    expires_at: datetime | None
    created_at: datetime | None


class DeveloperApiKeyCreateResponse(DeveloperApiKeyResponse):
    secret_key: str
