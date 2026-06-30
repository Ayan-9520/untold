"""Admin Panel schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class RbacPermission(BaseModel):
    permission: str
    roles: list[str]


class AdminUserItem(BaseModel):
    id: int
    full_name: str
    email: str
    is_admin: bool
    is_active: bool
    studio_role: str | None = None
    created_at: datetime


class AuditLogItem(ORMBase):
    id: int
    project_id: int | None
    user_id: int
    action: str
    entity_type: str | None
    entity_id: int | None
    meta: dict | None
    created_at: datetime


class AIUsageSummary(BaseModel):
    total_generations: int
    running: int
    queued: int
    completed: int
    failed: int
    tokens_estimated: int
    by_module: dict[str, int]


class StorageUsageSummary(BaseModel):
    total_bytes: int
    total_assets: int
    by_folder: dict[str, int]


class BillingSummary(BaseModel):
    mrr: float
    arr: float
    active_subscriptions: int
    revenue_by_plan: dict[str, float]


class ApiKeyItem(ORMBase):
    id: int
    name: str
    key_prefix: str
    permissions: list
    is_active: bool
    last_used_at: datetime | None
    created_at: datetime


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    permissions: list[str] = Field(default_factory=list)


class ApiKeyCreateResponse(ApiKeyItem):
    secret_key: str


class FeatureFlagItem(ORMBase):
    id: int
    key: str
    label: str
    description: str | None
    enabled: bool
    updated_at: datetime | None


class FeatureFlagUpdate(BaseModel):
    enabled: bool


class SystemSettingItem(BaseModel):
    key: str
    value: dict


class SystemSettingsUpdate(BaseModel):
    settings: dict[str, dict]


class SecurityLogItem(ORMBase):
    id: int
    event_type: str
    severity: str
    user_id: int | None
    ip_address: str | None
    message: str
    created_at: datetime


class BackupItem(ORMBase):
    id: int
    label: str
    backup_type: str
    status: str
    size_bytes: int
    storage_path: str | None
    created_at: datetime


class SystemHealth(BaseModel):
    api: str
    database: str
    redis: str
    celery: str
    storage: str
    uptime_pct: float
    version: str


class AdminOverview(BaseModel):
    users_count: int
    active_users: int
    api_keys: int
    feature_flags_enabled: int
    pending_approvals: int
    security_events_24h: int
    last_backup_at: datetime | None
    health: SystemHealth
