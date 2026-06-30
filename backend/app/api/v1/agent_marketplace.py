"""AI Agent Marketplace REST API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.agent_marketplace import (
    AgentConfigUpdate,
    AgentInstallationHistoryItem,
    AgentInstallationResponse,
    AgentInstallRequest,
    AgentPermissionsUpdate,
    MarketplaceAgentResponse,
    MarketplaceOverviewResponse,
)
from app.services.agent_marketplace_service import AgentMarketplaceService

router = APIRouter(prefix="/studio/platform/agent-marketplace", tags=["Agent Marketplace"])


class PublishVersionRequest(BaseModel):
    changelog: str = Field(min_length=1, max_length=500)
    release_notes: str | None = None


@router.get("/overview", response_model=MarketplaceOverviewResponse)
def marketplace_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AgentMarketplaceService.overview(db, user)


@router.get("/agents", response_model=list[MarketplaceAgentResponse])
def list_marketplace_agents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    category: str | None = Query(None),
):
    return AgentMarketplaceService.list_agents(db, user, category=category)


@router.get("/agents/{slug}")
def get_marketplace_agent(slug: str, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AgentMarketplaceService.get_agent(db, user, slug)


@router.get("/installed", response_model=list[AgentInstallationResponse])
def list_installed_agents(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AgentMarketplaceService.list_installed(db, user)


@router.post("/agents/{slug}/install", response_model=AgentInstallationResponse, status_code=201)
def install_agent(
    slug: str,
    data: AgentInstallRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AgentMarketplaceService.install(db, user, slug, data)


@router.post("/installations/{installation_id}/enable", response_model=AgentInstallationResponse)
def enable_agent(installation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AgentMarketplaceService.enable(db, user, installation_id)


@router.post("/installations/{installation_id}/disable", response_model=AgentInstallationResponse)
def disable_agent(installation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AgentMarketplaceService.disable(db, user, installation_id)


@router.patch("/installations/{installation_id}/config", response_model=AgentInstallationResponse)
def update_agent_config(
    installation_id: int,
    data: AgentConfigUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AgentMarketplaceService.update_config(db, user, installation_id, data)


@router.patch("/installations/{installation_id}/permissions", response_model=AgentInstallationResponse)
def update_agent_permissions(
    installation_id: int,
    data: AgentPermissionsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AgentMarketplaceService.update_permissions(db, user, installation_id, data)


@router.post("/installations/{installation_id}/update", response_model=AgentInstallationResponse)
def update_agent_version(installation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AgentMarketplaceService.update_version(db, user, installation_id)


@router.get("/installations/{installation_id}/history", response_model=list[AgentInstallationHistoryItem])
def agent_installation_history(
    installation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AgentMarketplaceService.history(db, user, installation_id)


@router.delete("/installations/{installation_id}", status_code=204)
def uninstall_agent(installation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    AgentMarketplaceService.uninstall(db, user, installation_id)


@router.post("/agents/{slug}/versions", status_code=201)
def publish_agent_version(
    slug: str,
    data: PublishVersionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AgentMarketplaceService.publish_agent_version(
        db, user, slug, changelog=data.changelog, release_notes=data.release_notes
    )
