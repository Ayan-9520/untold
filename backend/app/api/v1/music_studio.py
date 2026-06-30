"""AI Music Studio REST API."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models import User
from app.models.studio_platform import AIGeneration
from app.schemas.ai_studio import AIPromptResponse
from app.schemas.music_studio import (
    MusicGenerateCreate,
    MusicHistoryResponse,
    MusicJobResponse,
    MusicPreviewCreate,
    MusicPreviewResponse,
    MusicQueueResponse,
    MusicSaveAssetResponse,
    MusicStudioOverviewResponse,
    MusicVersionResponse,
)
from app.services.ai_studio_service import AIStudioService
from app.services.music_studio_service import MusicStudioService
from app.services.studio_platform_service import StudioPlatformService

router = APIRouter(prefix="/studio/platform/music-studio", tags=["AI Music Studio"])


@router.get("/overview", response_model=MusicStudioOverviewResponse)
def music_studio_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return MusicStudioService.get_overview(db, user)


@router.post("/generate", response_model=MusicJobResponse, status_code=201)
def create_music_generation(
    data: MusicGenerateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    gen = MusicStudioService.create_generation(db, user, data)
    return MusicStudioService._job_dict(gen, user.full_name)


@router.post("/preview", response_model=MusicPreviewResponse)
def preview_music(
    data: MusicPreviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return MusicStudioService.preview(db, user, data)


@router.get("/queue", response_model=MusicQueueResponse)
def music_queue(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return MusicStudioService.get_queue(db, user)


@router.get("/history", response_model=MusicHistoryResponse)
def music_history(
    category: str | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return MusicStudioService.get_history(db, user, category, limit, offset)


@router.get("/favorites", response_model=list[MusicJobResponse])
def music_favorites(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return MusicStudioService.get_favorites(db, user)


@router.post("/jobs/{job_id}/favorite")
def toggle_favorite(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return MusicStudioService.toggle_favorite(db, user, job_id)


@router.get("/jobs/{job_id}/versions", response_model=list[MusicVersionResponse])
def music_versions(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return MusicStudioService.list_versions(db, user, job_id)


@router.post("/jobs/{job_id}/save-asset", response_model=MusicSaveAssetResponse)
def save_to_assets(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return MusicStudioService.save_to_asset_library(db, user, job_id)


@router.get("/jobs/{job_id}/download")
def download_music(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    StudioPlatformService.require_permission(db, user, None, "ai.generate")
    row = db.query(AIGeneration).filter(AIGeneration.id == job_id).first()
    if row and row.result_url:
        return RedirectResponse(url=row.result_url)
    raise NotFoundError("Audio file")


@router.get("/prompts", response_model=list[AIPromptResponse])
def music_prompts(
    category: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return MusicStudioService.list_prompts(db, user, category)


@router.post("/jobs/{job_id}/retry", response_model=MusicJobResponse)
def retry_music_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.retry_job(db, user, job_id)
    return MusicStudioService._job_dict(gen, user.full_name)


@router.post("/jobs/{job_id}/cancel", response_model=MusicJobResponse)
def cancel_music_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.cancel_job(db, user, job_id)
    return MusicStudioService._job_dict(gen, user.full_name)
