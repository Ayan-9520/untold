"""AI Image Studio REST API."""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.models import User
from app.schemas.ai_studio import AIPromptResponse
from app.schemas.image_studio import (
    ImageCollectionCreate,
    ImageCollectionResponse,
    ImageGenerateCreate,
    ImageHistoryResponse,
    ImageJobResponse,
    ImageQueueResponse,
    ImageSaveAssetResponse,
    ImageStudioOverviewResponse,
    ImageVariationRequest,
    ImageVersionResponse,
)
from app.services.ai_studio_service import AIStudioService
from app.services.image_studio_service import ImageStudioService

router = APIRouter(prefix="/studio/platform/image-studio", tags=["AI Image Studio"])
_settings = get_settings()


@router.get("/overview", response_model=ImageStudioOverviewResponse)
def image_studio_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ImageStudioService.get_overview(db, user)


@router.post("/generate", response_model=ImageJobResponse, status_code=201)
@limiter.limit(_settings.rate_limit_ai)
def create_image_generation(
    request: Request,
    data: ImageGenerateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    gen = ImageStudioService.create_generation(db, user, data)
    return ImageStudioService._job_dict(gen, user.full_name)


@router.get("/queue", response_model=ImageQueueResponse)
def image_queue(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ImageStudioService.get_queue(db, user)


@router.get("/history", response_model=ImageHistoryResponse)
def image_history(
    image_type: str | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ImageStudioService.get_history(db, user, image_type, limit, offset)


@router.get("/favorites", response_model=list[ImageJobResponse])
def image_favorites(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ImageStudioService.get_favorites(db, user)


@router.post("/jobs/{job_id}/favorite")
def toggle_favorite(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ImageStudioService.toggle_favorite(db, user, job_id)


@router.post("/jobs/{job_id}/upscale", response_model=ImageJobResponse, status_code=201)
def upscale_image(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    gen = ImageStudioService.upscale(db, user, job_id)
    return ImageStudioService._job_dict(gen, user.full_name)


@router.post("/jobs/{job_id}/variation", response_model=ImageJobResponse, status_code=201)
def image_variation(
    job_id: int,
    data: ImageVariationRequest | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    gen = ImageStudioService.create_variation(db, user, job_id, data.prompt if data else None)
    return ImageStudioService._job_dict(gen, user.full_name)


@router.get("/jobs/{job_id}/versions", response_model=list[ImageVersionResponse])
def image_versions(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ImageStudioService.list_versions(db, user, job_id)


@router.post("/jobs/{job_id}/save-asset", response_model=ImageSaveAssetResponse)
def save_to_assets(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ImageStudioService.save_to_asset_library(db, user, job_id)


@router.get("/jobs/{job_id}/download")
def download_image(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    from app.models.studio_platform import AIGeneration

    job = AIStudioService.get_job(db, user, job_id)
    if job.get("result_url"):
        return RedirectResponse(url=job["result_url"])
    from app.core.exceptions import NotFoundError
    raise NotFoundError("Image file")


@router.get("/collections", response_model=list[ImageCollectionResponse])
def list_collections(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return ImageStudioService.list_collections(db, user)


@router.post("/collections", response_model=ImageCollectionResponse, status_code=201)
def create_collection(
    data: ImageCollectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    col = ImageStudioService.create_collection(db, user, data)
    return {
        "id": col.id,
        "name": col.name,
        "description": col.description,
        "project_id": col.project_id,
        "item_count": 0,
        "created_at": col.created_at,
    }


@router.post("/collections/{collection_id}/items/{generation_id}", status_code=204)
def add_collection_item(
    collection_id: int,
    generation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    ImageStudioService.add_to_collection(db, user, collection_id, generation_id)


@router.get("/prompts", response_model=list[AIPromptResponse])
def image_prompts(
    image_type: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return ImageStudioService.list_prompts(db, user, image_type)


@router.post("/jobs/{job_id}/retry", response_model=ImageJobResponse)
def retry_image_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    AIStudioService.retry_job(db, user, job_id)
    return AIStudioService.get_job(db, user, job_id)


@router.post("/jobs/{job_id}/cancel", response_model=ImageJobResponse)
def cancel_image_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    AIStudioService.cancel_job(db, user, job_id)
    return AIStudioService.get_job(db, user, job_id)
