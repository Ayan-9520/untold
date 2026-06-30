"""AI SEO Studio REST API."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.seo_studio import (
    SEOApprovalRequest,
    SEOApplyProjectRequest,
    SEOApplyProjectResponse,
    SEOExportResponse,
    SEOGenerateCreate,
    SEOHistoryResponse,
    SEOJobResponse,
    SEOQueueResponse,
    SEOSelectVariantRequest,
    SEOStudioOverviewResponse,
    SEOVariantResponse,
)
from app.services.ai_studio_service import AIStudioService
from app.services.seo_studio_service import SEOStudioService

router = APIRouter(prefix="/studio/platform/seo-studio", tags=["AI SEO Studio"])


@router.get("/overview", response_model=SEOStudioOverviewResponse)
def seo_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return SEOStudioService.get_overview(db, user)


@router.post("/generate", response_model=SEOJobResponse, status_code=201)
def create_seo(
    data: SEOGenerateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    gen = SEOStudioService.create_generation(db, user, data)
    return SEOStudioService._job_dict(gen, user.full_name)


@router.get("/queue", response_model=SEOQueueResponse)
def seo_queue(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return SEOStudioService.get_queue(db, user)


@router.get("/history", response_model=SEOHistoryResponse)
def seo_history(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return SEOStudioService.get_history(db, user, limit, offset)


@router.get("/jobs/{job_id}/variants", response_model=list[SEOVariantResponse])
def seo_variants(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return SEOStudioService.list_variants(db, user, job_id)


@router.post("/jobs/{job_id}/select-variant")
def select_variant(
    job_id: int,
    data: SEOSelectVariantRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return SEOStudioService.select_variant(db, user, job_id, data)


@router.post("/jobs/{job_id}/request-approval")
def request_approval(
    job_id: int,
    data: SEOApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return SEOStudioService.request_approval(db, user, job_id, data or SEOApprovalRequest())


@router.post("/jobs/{job_id}/approve")
def approve_seo(
    job_id: int,
    data: SEOApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return SEOStudioService.approve(db, user, job_id, data)


@router.post("/jobs/{job_id}/reject")
def reject_seo(
    job_id: int,
    data: SEOApprovalRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return SEOStudioService.reject(db, user, job_id, data)


@router.get("/jobs/{job_id}/export", response_model=SEOExportResponse)
def export_seo_pack(
    job_id: int,
    variant_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return SEOStudioService.export_pack(db, user, job_id, variant_id)


@router.post("/jobs/{job_id}/apply-project", response_model=SEOApplyProjectResponse)
def apply_seo_to_project(
    job_id: int,
    data: SEOApplyProjectRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return SEOStudioService.apply_to_project(db, user, job_id, data or SEOApplyProjectRequest())


@router.post("/jobs/{job_id}/retry", response_model=SEOJobResponse)
def retry_seo(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.retry_job(db, user, job_id)
    return SEOStudioService._job_dict(gen, user.full_name)


@router.post("/jobs/{job_id}/cancel", response_model=SEOJobResponse)
def cancel_seo(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = AIStudioService.cancel_job(db, user, job_id)
    return SEOStudioService._job_dict(gen, user.full_name)
