"""AI Video Studio REST API."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models import User
from app.schemas.ai_studio import AIPromptResponse
from app.schemas.video_studio import (
    VideoGenerateCreate,
    VideoHistoryResponse,
    VideoJobResponse,
    VideoQueueResponse,
    VideoSaveAssetResponse,
    VideoStudioOverviewResponse,
    VideoVersionResponse,
)
from app.services.ai_studio_service import AIStudioService
from app.services.video_studio_service import VideoStudioService

router = APIRouter(prefix="/studio/platform/video-studio", tags=["AI Video Studio"])


@router.get("/overview", response_model=VideoStudioOverviewResponse)
def video_studio_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return VideoStudioService.get_overview(db, user)


@router.post("/generate", response_model=VideoJobResponse, status_code=201)
def create_video_generation(
    data: VideoGenerateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    gen = VideoStudioService.create_generation(db, user, data)
    return VideoStudioService._job_dict(gen, user.full_name)


@router.get("/queue", response_model=VideoQueueResponse)
def video_queue(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return VideoStudioService.get_queue(db, user)


@router.get("/history", response_model=VideoHistoryResponse)
def video_history(
    video_type: str | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return VideoStudioService.get_history(db, user, video_type, limit, offset)


@router.get("/jobs/{job_id}/versions", response_model=list[VideoVersionResponse])
def video_versions(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return VideoStudioService.list_versions(db, user, job_id)


@router.post("/jobs/{job_id}/save-asset", response_model=VideoSaveAssetResponse)
def save_to_assets(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return VideoStudioService.save_to_asset_library(db, user, job_id)


@router.get("/jobs/{job_id}/download")
def download_video(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    job = AIStudioService.get_job(db, user, job_id)
    if job.get("result_url"):
        return RedirectResponse(url=job["result_url"])
    raise NotFoundError("Video file")


@router.get("/prompts", response_model=list[AIPromptResponse])
def video_prompts(
    video_type: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return VideoStudioService.list_prompts(db, user, video_type)


@router.post("/jobs/{job_id}/retry", response_model=VideoJobResponse)
def retry_video_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.retry_job(db, user, job_id)
    return VideoStudioService._job_dict(gen, user.full_name)


@router.post("/jobs/{job_id}/cancel", response_model=VideoJobResponse)
def cancel_video_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.cancel_job(db, user, job_id)
    return VideoStudioService._job_dict(gen, user.full_name)
