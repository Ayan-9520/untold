"""AI Voice Studio REST API."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models import User
from app.schemas.ai_studio import AIPromptResponse
from app.schemas.voice_studio import (
    VoiceGenerateCreate,
    VoiceHistoryResponse,
    VoiceJobResponse,
    VoicePreviewCreate,
    VoicePreviewResponse,
    VoiceQueueResponse,
    VoiceSaveAssetResponse,
    VoiceStudioOverviewResponse,
    VoiceSubtitlesResponse,
    VoiceTranslateCreate,
    VoiceTranslateResponse,
    VoiceVersionResponse,
)
from app.services.ai_studio_service import AIStudioService
from app.services.studio_platform_service import StudioPlatformService
from app.services.voice_studio_service import VoiceStudioService

router = APIRouter(prefix="/studio/platform/voice-studio", tags=["AI Voice Studio"])


@router.get("/overview", response_model=VoiceStudioOverviewResponse)
def voice_studio_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return VoiceStudioService.get_overview(db, user)


@router.post("/generate", response_model=VoiceJobResponse, status_code=201)
def create_voice_generation(
    data: VoiceGenerateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    gen = VoiceStudioService.create_generation(db, user, data)
    return VoiceStudioService._job_dict(gen, user.full_name)


@router.post("/preview", response_model=VoicePreviewResponse)
def preview_voice(
    data: VoicePreviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return VoiceStudioService.preview(db, user, data)


@router.post("/translate", response_model=VoiceTranslateResponse)
def translate_narration(
    data: VoiceTranslateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return VoiceStudioService.translate_text(db, user, data)


@router.get("/queue", response_model=VoiceQueueResponse)
def voice_queue(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return VoiceStudioService.get_queue(db, user)


@router.get("/history", response_model=VoiceHistoryResponse)
def voice_history(
    language: str | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return VoiceStudioService.get_history(db, user, language, limit, offset)


@router.get("/jobs/{job_id}/versions", response_model=list[VoiceVersionResponse])
def voice_versions(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return VoiceStudioService.list_versions(db, user, job_id)


@router.get("/jobs/{job_id}/subtitles", response_model=VoiceSubtitlesResponse)
def voice_subtitles(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return VoiceStudioService.get_job_subtitles(db, user, job_id)


@router.get("/jobs/{job_id}/subtitles.srt")
def download_subtitles_srt(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    data = VoiceStudioService.get_job_subtitles(db, user, job_id)
    if data.get("srt"):
        return PlainTextResponse(content=data["srt"], media_type="text/plain")
    if data.get("subtitles_url"):
        return RedirectResponse(url=data["subtitles_url"])
    raise NotFoundError("Subtitles")


@router.post("/jobs/{job_id}/save-asset", response_model=VoiceSaveAssetResponse)
def save_to_assets(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return VoiceStudioService.save_to_asset_library(db, user, job_id)


@router.get("/jobs/{job_id}/download")
def download_voice(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    from app.models.studio_platform import AIGeneration

    StudioPlatformService.require_permission(db, user, None, "ai.generate")
    row = db.query(AIGeneration).filter(AIGeneration.id == job_id).first()
    if row and row.result_url:
        return RedirectResponse(url=row.result_url)
    raise NotFoundError("Audio file")


@router.get("/prompts", response_model=list[AIPromptResponse])
def voice_prompts(
    language: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return VoiceStudioService.list_prompts(db, user, language)


@router.post("/jobs/{job_id}/retry", response_model=VoiceJobResponse)
def retry_voice_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.retry_job(db, user, job_id)
    return VoiceStudioService._job_dict(gen, user.full_name)


@router.post("/jobs/{job_id}/cancel", response_model=VoiceJobResponse)
def cancel_voice_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.cancel_job(db, user, job_id)
    return VoiceStudioService._job_dict(gen, user.full_name)
