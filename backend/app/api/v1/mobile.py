"""Mobile platform REST API — device registration, studio & originals mobile surfaces."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, get_current_studio_user, get_optional_user
from app.db.session import get_db
from app.models import User
from app.schemas.mobile import ApprovalAction, MobileDeviceRegister
from app.services.mobile_platform_service import MobilePlatformService
from app.services.studio_analytics_service import StudioAnalyticsService

router = APIRouter(prefix="/mobile", tags=["Mobile"])


@router.post("/devices/register", status_code=201)
def register_device(
    data: MobileDeviceRegister,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return MobilePlatformService.register_device(
        db,
        user,
        app_type=data.app_type,
        platform=data.platform,
        device_token=data.device_token,
        device_name=data.device_name,
        push_enabled=data.push_enabled,
        meta=data.meta,
    )


@router.delete("/devices/{device_id}", status_code=204)
def unregister_device(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    MobilePlatformService.unregister_device(db, user, device_id)


@router.get("/devices")
def list_devices(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return MobilePlatformService.list_devices(db, user)


@router.get("/offline-manifest")
def offline_manifest(
    app_type: str = Query(..., pattern="^(studio|originals)$"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return MobilePlatformService.offline_manifest(db, user, app_type=app_type)


# — Studio Mobile —

@router.get("/studio/overview")
def studio_mobile_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return MobilePlatformService.studio_overview(db, user)


@router.get("/studio/approvals")
def studio_approvals_inbox(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    limit: int = Query(50, ge=1, le=100),
):
    return MobilePlatformService.approvals_inbox(db, user, limit=limit)


@router.post("/studio/approvals/{approval_id}/action")
def studio_approval_action(
    approval_id: int,
    data: ApprovalAction,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return MobilePlatformService.resolve_approval(db, user, approval_id, action=data.action, notes=data.notes)


@router.get("/studio/ai-jobs")
def studio_ai_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return MobilePlatformService.ai_jobs(db, user)


@router.get("/studio/analytics")
def studio_mobile_analytics(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return StudioAnalyticsService.get_overview(db, user)


@router.post("/studio/assets/upload")
async def studio_mobile_upload(
    file: UploadFile = File(...),
    project_id: int | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    from app.schemas.asset_library import AssetUploadMetadata
    from app.services.asset_library_service import AssetLibraryService

    data = await file.read()
    meta = AssetUploadMetadata(
        filename=file.filename or "upload.bin",
        folder="images",
        project_id=project_id,
        mime_type=file.content_type,
    )
    asset = AssetLibraryService.upload_asset(db, user, meta, data)
    return AssetLibraryService._asset_dict(asset, user)


# — Originals Mobile —

@router.get("/originals/home")
def originals_mobile_home(db: Session = Depends(get_db), user: User | None = Depends(get_optional_user)):
    return MobilePlatformService.originals_home(db, user)
