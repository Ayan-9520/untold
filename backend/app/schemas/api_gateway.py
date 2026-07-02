"""API Gateway admin schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class GatewayApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    scopes: list[str] = Field(default_factory=list)
    permissions: list[str] | None = None
    rate_limit_tier: str = "standard"
    api_version: str = "v1"
    expires_at: datetime | None = None


class GatewayApiKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    environment: str = "production"
    scopes: list[str]
    rate_limit_tier: str
    api_version: str
    is_active: bool
    total_requests: int
    last_used_at: datetime | None
    expires_at: datetime | None
    created_at: datetime | None


class GatewayApiKeyCreateResponse(GatewayApiKeyResponse):
    secret_key: str


class GatewayWebhookCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    url: str = Field(min_length=8, max_length=2000)
    events: list[str] = Field(min_length=1)


class GatewayWebhookResponse(BaseModel):
    id: int
    name: str
    url: str
    events: list[str]
    is_active: bool
    failure_count: int
    last_triggered_at: datetime | None
    created_at: datetime | None


class GatewayOverviewResponse(BaseModel):
    active_api_keys: int
    requests_24h: int
    requests_7d: int
    avg_latency_ms: float
    error_rate_24h_pct: float
    active_webhooks: int
    supported_versions: list[str]
    rate_limit_tiers: dict
    by_version: dict
    by_protocol: dict
