"""Admin Panel REST API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.db.session import get_db
from app.models import User
from app.schemas.studio_admin import (
    AIUsageSummary,
    AdminOverview,
    AdminUserItem,
    ApiKeyCreate,
    ApiKeyCreateResponse,
    ApiKeyItem,
    AuditLogItem,
    BackupItem,
    BillingSummary,
    FeatureFlagItem,
    FeatureFlagUpdate,
    RbacPermission,
    SecurityLogItem,
    StorageUsageSummary,
    SystemHealth,
    SystemSettingItem,
    SystemSettingsUpdate,
)
from app.services.studio_admin_service import StudioAdminService

router = APIRouter(prefix="/studio/platform/admin", tags=["Admin Panel"])


@router.get("/overview", response_model=AdminOverview)
def admin_overview(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return StudioAdminService.get_overview(db, user)


@router.get("/rbac", response_model=list[RbacPermission])
def admin_rbac(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return StudioAdminService.get_rbac(db, user)


@router.get("/users", response_model=list[AdminUserItem])
def admin_users(
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return StudioAdminService.list_users(db, user, limit)


@router.get("/audit-logs", response_model=list[AuditLogItem])
def admin_audit_logs(
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return StudioAdminService.list_audit_logs(db, user, limit)


@router.get("/ai-usage", response_model=AIUsageSummary)
def admin_ai_usage(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return StudioAdminService.get_ai_usage(db, user)


@router.get("/storage", response_model=StorageUsageSummary)
def admin_storage(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return StudioAdminService.get_storage_usage(db, user)


@router.get("/billing", response_model=BillingSummary)
def admin_billing(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return StudioAdminService.get_billing(db, user)


@router.get("/api-keys", response_model=list[ApiKeyItem])
def list_api_keys(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return StudioAdminService.list_api_keys(db, user)


@router.post("/api-keys", response_model=ApiKeyCreateResponse, status_code=201)
def create_api_key(
    data: ApiKeyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return StudioAdminService.create_api_key(db, user, data)


@router.delete("/api-keys/{key_id}", status_code=204)
def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    StudioAdminService.revoke_api_key(db, user, key_id)


@router.get("/health", response_model=SystemHealth)
def admin_health(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return StudioAdminService.get_health(db, user)


@router.get("/security-logs", response_model=list[SecurityLogItem])
def admin_security_logs(
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return StudioAdminService.list_security_logs(db, user, limit)


@router.get("/feature-flags", response_model=list[FeatureFlagItem])
def admin_feature_flags(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return StudioAdminService.list_feature_flags(db, user)


@router.patch("/feature-flags/{flag_id}", response_model=FeatureFlagItem)
def update_feature_flag(
    flag_id: int,
    data: FeatureFlagUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return StudioAdminService.update_feature_flag(db, user, flag_id, data)


@router.get("/settings", response_model=list[SystemSettingItem])
def admin_settings(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return StudioAdminService.get_settings(db, user)


@router.put("/settings", response_model=list[SystemSettingItem])
def update_settings(
    data: SystemSettingsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return StudioAdminService.update_settings(db, user, data)


@router.get("/backups", response_model=list[BackupItem])
def admin_backups(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return StudioAdminService.list_backups(db, user)


@router.post("/backups", response_model=BackupItem, status_code=201)
def create_backup(
    label: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return StudioAdminService.create_backup(db, user, label)
