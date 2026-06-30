"""AI Studio REST API."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.middleware.rate_limit import limiter
from app.models import User
from app.schemas.ai_studio import (
    AIGenerationCreate,
    AIGenerationJobResponse,
    AIHistoryResponse,
    AIPromptCreate,
    AIPromptResponse,
    AIPromptUpdate,
    AIQueueResponse,
    AIStudioOverviewResponse,
    AITelemetryResponse,
)
from app.services.ai_studio_service import AIStudioService
from app.ai.providers.registry import get_ai_registry
from app.domain.vectorstore.types import VectorRecord, VectorSearchRequest, VectorUpsertRequest
from app.schemas.vectorstore import (
    VectorSearchBody,
    VectorSearchResponse,
    VectorSearchHitResponse,
    VectorUpsertBody,
    VectorUpsertResponse,
)

router = APIRouter(prefix="/studio/platform/ai-studio", tags=["AI Studio"])
_settings = get_settings()


@router.get("/providers")
def ai_provider_registry(user: User = Depends(get_current_studio_user)):
    return get_ai_registry().overview()


@router.post("/vectorstore/upsert", response_model=VectorUpsertResponse)
@limiter.limit(_settings.rate_limit_ai)
def vectorstore_upsert(
    request: Request,
    body: VectorUpsertBody,
    user: User = Depends(get_current_studio_user),
):
    result = get_ai_registry().upsert_vectors(
        VectorUpsertRequest(
            collection=body.collection,
            records=[
                VectorRecord(
                    id=r.id,
                    text=r.text,
                    vector=r.vector,
                    metadata=r.metadata,
                )
                for r in body.records
            ],
            dimension=body.dimension,
        ),
        provider_id=body.provider,
    )
    return VectorUpsertResponse(
        upserted=result.upserted,
        collection=result.collection,
        provider=result.provider,
        meta=result.meta,
    )


@router.post("/vectorstore/search", response_model=VectorSearchResponse)
@limiter.limit(_settings.rate_limit_ai)
def vectorstore_search(
    request: Request,
    body: VectorSearchBody,
    user: User = Depends(get_current_studio_user),
):
    result = get_ai_registry().search_vectors(
        VectorSearchRequest(
            collection=body.collection,
            vector=body.vector,
            top_k=body.top_k,
            filter=body.filter,
        ),
        provider_id=body.provider,
    )
    return VectorSearchResponse(
        hits=[
            VectorSearchHitResponse(
                id=h.id,
                text=h.text,
                score=h.score,
                metadata=h.metadata,
            )
            for h in result.hits
        ],
        collection=result.collection,
        provider=result.provider,
        meta=result.meta,
    )


@router.get("/overview", response_model=AIStudioOverviewResponse)
def ai_studio_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AIStudioService.get_overview(db, user)


@router.post("/generate", response_model=AIGenerationJobResponse, status_code=201)
@limiter.limit(_settings.rate_limit_ai)
def create_ai_generation(
    request: Request,
    data: AIGenerationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    gen = AIStudioService.create_generation(db, user, data)
    return AIStudioService.get_job(db, user, gen.id)


@router.get("/queue", response_model=AIQueueResponse)
def get_ai_queue(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AIStudioService.get_queue(db, user)


@router.get("/history", response_model=AIHistoryResponse)
def get_ai_history(
    module: str | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AIStudioService.get_history(db, user, module, limit, offset)


@router.get("/telemetry", response_model=AITelemetryResponse)
def get_ai_telemetry(
    module: str | None = None,
    limit: int = Query(default=100, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AIStudioService.get_telemetry(db, user, module, limit, offset)


@router.get("/jobs/{job_id}", response_model=AIGenerationJobResponse)
def get_ai_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AIStudioService.get_job(db, user, job_id)


@router.post("/jobs/{job_id}/retry", response_model=AIGenerationJobResponse)
def retry_ai_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    AIStudioService.retry_job(db, user, job_id)
    return AIStudioService.get_job(db, user, job_id)


@router.post("/jobs/{job_id}/cancel", response_model=AIGenerationJobResponse)
def cancel_ai_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    AIStudioService.cancel_job(db, user, job_id)
    return AIStudioService.get_job(db, user, job_id)


@router.get("/prompts", response_model=list[AIPromptResponse])
def list_prompts(
    module: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AIStudioService.list_prompts(db, user, module)


@router.post("/prompts", response_model=AIPromptResponse, status_code=201)
def create_prompt(
    data: AIPromptCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    p = AIStudioService.create_prompt(db, user, data)
    return {
        "id": p.id,
        "title": p.title,
        "module": p.module,
        "prompt_template": p.prompt_template,
        "description": p.description,
        "parameters": p.parameters,
        "tags": p.tags or [],
        "is_public": p.is_public,
        "created_by_id": p.created_by_id,
        "author_name": user.full_name,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


@router.patch("/prompts/{prompt_id}", response_model=AIPromptResponse)
def update_prompt(
    prompt_id: int,
    data: AIPromptUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    p = AIStudioService.update_prompt(db, user, prompt_id, data)
    return {
        "id": p.id,
        "title": p.title,
        "module": p.module,
        "prompt_template": p.prompt_template,
        "description": p.description,
        "parameters": p.parameters,
        "tags": p.tags or [],
        "is_public": p.is_public,
        "created_by_id": p.created_by_id,
        "author_name": user.full_name,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


@router.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    AIStudioService.delete_prompt(db, user, prompt_id)
