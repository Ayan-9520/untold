from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.db.session import get_db
from app.models import User
from app.schemas.studio import (
    AgentDashboardResponse,
    AssetLibraryResponse,
    ProductionListResponse,
    ProductionResponse,
    ProductionUpdate,
)
from app.services.studio_service import StudioService

router = APIRouter(prefix="/admin/studio", tags=["Admin — Studio"])


@router.get("/productions", response_model=ProductionListResponse)
def list_productions(
    stage: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    items, total = StudioService.list_productions(db, stage=stage, limit=limit)
    return ProductionListResponse(items=items, total=total)


@router.get("/productions/{production_id}", response_model=ProductionResponse)
def get_production(
    production_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    prod = StudioService.get_production(db, production_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Production not found")
    return prod


@router.patch("/productions/{production_id}", response_model=ProductionResponse)
def update_production(
    production_id: int,
    data: ProductionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    prod = StudioService.update_production(db, production_id, data)
    if not prod:
        raise HTTPException(status_code=404, detail="Production not found")
    return prod


@router.get("/agents", response_model=AgentDashboardResponse)
def agent_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return StudioService.get_agent_dashboard(db)


@router.get("/assets", response_model=AssetLibraryResponse)
def asset_library(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return StudioService.get_asset_library(db)


@router.get("/scripts/summary")
def scripts_summary(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return StudioService.scripts_summary(db)
