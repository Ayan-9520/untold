"""AI Translation Studio REST API."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models import User
from app.schemas.translation_studio import (
    TranslationApprovalRequest,
    TranslationGenerateCreate,
    TranslationHistoryResponse,
    TranslationJobResponse,
    TranslationMemoryResponse,
    TranslationQueueResponse,
    TranslationStudioOverviewResponse,
    TranslationSubtitlesResponse,
    TranslationVersionResponse,
)
from app.services.ai_studio_service import AIStudioService
from app.services.translation_studio_service import TranslationStudioService

router = APIRouter(prefix="/studio/platform/translation-studio", tags=["AI Translation Studio"])


@router.get("/overview", response_model=TranslationStudioOverviewResponse)
def translation_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return TranslationStudioService.get_overview(db, user)


@router.post("/generate", response_model=TranslationJobResponse, status_code=201)
def create_translation(
    data: TranslationGenerateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    gen = TranslationStudioService.create_generation(db, user, data)
    return TranslationStudioService._job_dict(gen, user.full_name)


@router.get("/queue", response_model=TranslationQueueResponse)
def translation_queue(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return TranslationStudioService.get_queue(db, user)


@router.get("/history", response_model=TranslationHistoryResponse)
def translation_history(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TranslationStudioService.get_history(db, user, limit, offset)


@router.get("/translation-memory", response_model=TranslationMemoryResponse)
def translation_memory(
    source_lang: str | None = None,
    target_lang: str | None = None,
    content_type: str | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TranslationStudioService.list_translation_memory(
        db, user, source_lang, target_lang, content_type, limit, offset,
    )


@router.delete("/translation-memory/{entry_id}")
def delete_translation_memory(
    entry_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TranslationStudioService.delete_translation_memory(db, user, entry_id)


@router.get("/jobs/{job_id}/versions", response_model=list[TranslationVersionResponse])
def translation_versions(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TranslationStudioService.list_versions(db, user, job_id)


@router.get("/jobs/{job_id}/subtitles", response_model=TranslationSubtitlesResponse)
def translation_subtitles(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TranslationStudioService.get_job_subtitles(db, user, job_id)


@router.get("/jobs/{job_id}/subtitles.srt")
def download_srt(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    data = TranslationStudioService.get_job_subtitles(db, user, job_id)
    if data.get("srt"):
        return PlainTextResponse(content=data["srt"], media_type="text/plain")
    if data.get("srt_url"):
        return RedirectResponse(url=data["srt_url"])
    raise NotFoundError("SRT file")


@router.get("/jobs/{job_id}/subtitles.vtt")
def download_vtt(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    data = TranslationStudioService.get_job_subtitles(db, user, job_id)
    if data.get("vtt"):
        return PlainTextResponse(content=data["vtt"], media_type="text/vtt")
    if data.get("vtt_url"):
        return RedirectResponse(url=data["vtt_url"])
    raise NotFoundError("VTT file")


@router.post("/jobs/{job_id}/request-approval")
def request_approval(
    job_id: int,
    data: TranslationApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TranslationStudioService.request_approval(db, user, job_id, data or TranslationApprovalRequest())


@router.post("/jobs/{job_id}/approve")
def approve_translation(
    job_id: int,
    data: TranslationApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TranslationStudioService.approve(db, user, job_id, data)


@router.post("/jobs/{job_id}/reject")
def reject_translation(
    job_id: int,
    data: TranslationApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return TranslationStudioService.reject(db, user, job_id, data)


@router.post("/jobs/{job_id}/retry", response_model=TranslationJobResponse)
def retry_translation(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.retry_job(db, user, job_id)
    return TranslationStudioService._job_dict(gen, user.full_name)


@router.post("/jobs/{job_id}/cancel", response_model=TranslationJobResponse)
def cancel_translation(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.cancel_job(db, user, job_id)
    return TranslationStudioService._job_dict(gen, user.full_name)
