"""AI Shorts Studio REST API."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models import User
from app.models.studio_platform import AIGeneration
from app.schemas.shorts_studio import (
    ShortsGenerateCreate,
    ShortsHistoryResponse,
    ShortsJobResponse,
    ShortsPublishQueueResponse,
    ShortsQueuePublishCreate,
    ShortsQueueResponse,
    ShortsSaveAssetResponse,
    ShortsStudioOverviewResponse,
)
from app.services.ai_studio_service import AIStudioService
from app.services.shorts_studio_service import ShortsStudioService
from app.services.studio_platform_service import StudioPlatformService

router = APIRouter(prefix="/studio/platform/shorts-studio", tags=["AI Shorts Studio"])


@router.get("/overview", response_model=ShortsStudioOverviewResponse)
def shorts_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ShortsStudioService.get_overview(db, user)


@router.post("/generate", response_model=ShortsJobResponse, status_code=201)
def create_shorts(
    data: ShortsGenerateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    gen = ShortsStudioService.create_generation(db, user, data)
    return ShortsStudioService._job_dict(gen, user.full_name)


@router.get("/queue", response_model=ShortsQueueResponse)
def shorts_queue(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ShortsStudioService.get_queue(db, user)


@router.get("/history", response_model=ShortsHistoryResponse)
def shorts_history(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ShortsStudioService.get_history(db, user, limit, offset)


@router.post("/jobs/{job_id}/queue-publish", response_model=ShortsPublishQueueResponse)
def queue_publish(
    job_id: int,
    data: ShortsQueuePublishCreate | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ShortsStudioService.queue_for_publishing(db, user, job_id, data or ShortsQueuePublishCreate())


@router.post("/jobs/{job_id}/save-asset", response_model=ShortsSaveAssetResponse)
def save_shorts_asset(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ShortsStudioService.save_to_asset_library(db, user, job_id)


@router.get("/jobs/{job_id}/download")
def download_shorts(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    StudioPlatformService.require_permission(db, user, None, "ai.generate")
    row = db.query(AIGeneration).filter(AIGeneration.id == job_id).first()
    if row and row.result_url:
        return RedirectResponse(url=row.result_url)
    raise NotFoundError("Short clip")


@router.post("/jobs/{job_id}/retry", response_model=ShortsJobResponse)
def retry_shorts(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.retry_job(db, user, job_id)
    return ShortsStudioService._job_dict(gen, user.full_name)


@router.post("/jobs/{job_id}/cancel", response_model=ShortsJobResponse)
def cancel_shorts(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.cancel_job(db, user, job_id)
    return ShortsStudioService._job_dict(gen, user.full_name)
