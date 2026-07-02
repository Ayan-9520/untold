"""Plugin SDK REST API — marketplace, settings, runtime, documentation."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.plugin_sdk import (
    PluginDefinitionResponse,
    PluginEventLogItem,
    PluginInstallationHistoryItem,
    PluginInstallationResponse,
    PluginInstallRequest,
    PluginMarketplaceOverviewResponse,
    PluginPermissionsUpdate,
    PluginSdkDocsResponse,
    PluginSettingsUpdate,
)
from app.services.plugin_sdk_service import PluginSdkService

router = APIRouter(prefix="/studio/platform/plugins", tags=["Plugin SDK"])


class PublishPluginVersionRequest(BaseModel):
    changelog: str = Field(min_length=1, max_length=500)
    release_notes: str | None = None


class RegisterPluginRequest(BaseModel):
    manifest: dict[str, Any]


class EmitTestEventRequest(BaseModel):
    event_name: str = Field(min_length=1, max_length=120)
    payload: dict[str, Any] = Field(default_factory=dict)


class PluginRatingRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    review: str | None = Field(None, max_length=2000)


@router.get("/overview", response_model=PluginMarketplaceOverviewResponse)
def plugin_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return PluginSdkService.overview(db, user)


@router.get("/catalog", response_model=list[PluginDefinitionResponse])
def list_plugins(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    category: str | None = Query(None),
    search: str | None = Query(None),
):
    return PluginSdkService.list_plugins(db, user, category=category, search=search)


@router.get("/catalog/{slug}")
def get_plugin(slug: str, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return PluginSdkService.get_plugin(db, user, slug)


@router.get("/installed", response_model=list[PluginInstallationResponse])
def list_installed_plugins(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return PluginSdkService.list_installed(db, user)


@router.post("/catalog/{slug}/install", response_model=PluginInstallationResponse, status_code=201)
def install_plugin(
    slug: str,
    data: PluginInstallRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PluginSdkService.install(db, user, slug, data)


@router.post("/installations/{installation_id}/enable", response_model=PluginInstallationResponse)
def enable_plugin(
    installation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)
):
    return PluginSdkService.enable(db, user, installation_id)


@router.post("/installations/{installation_id}/disable", response_model=PluginInstallationResponse)
def disable_plugin(
    installation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)
):
    return PluginSdkService.disable(db, user, installation_id)


@router.patch("/installations/{installation_id}/settings", response_model=PluginInstallationResponse)
def update_plugin_settings(
    installation_id: int,
    data: PluginSettingsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PluginSdkService.update_settings(db, user, installation_id, data)


@router.patch("/installations/{installation_id}/permissions", response_model=PluginInstallationResponse)
def update_plugin_permissions(
    installation_id: int,
    data: PluginPermissionsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PluginSdkService.update_permissions(db, user, installation_id, data)


@router.post("/installations/{installation_id}/update", response_model=PluginInstallationResponse)
def update_plugin_version(
    installation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)
):
    return PluginSdkService.update_version(db, user, installation_id)


@router.get("/installations/{installation_id}/history", response_model=list[PluginInstallationHistoryItem])
def plugin_installation_history(
    installation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)
):
    return PluginSdkService.installation_history(db, user, installation_id)


@router.delete("/installations/{installation_id}", status_code=204)
def uninstall_plugin(
    installation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)
):
    PluginSdkService.uninstall(db, user, installation_id)


@router.get("/docs", response_model=PluginSdkDocsResponse)
def plugin_sdk_docs():
    return PluginSdkService.sdk_docs()


@router.get("/runtime")
def plugin_runtime_manifest(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return PluginSdkService.runtime_manifest(db, user)


@router.get("/event-log", response_model=list[PluginEventLogItem])
def plugin_event_log(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    limit: int = Query(50, ge=1, le=200),
):
    return PluginSdkService.event_log(db, user, limit=limit)


@router.get("/catalog/{slug}/versions")
def list_plugin_versions(slug: str, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return PluginSdkService.list_versions(db, user, slug)


@router.get("/catalog/{slug}/ratings")
def list_plugin_ratings(
    slug: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    limit: int = Query(20, ge=1, le=100),
):
    return PluginSdkService.list_ratings(db, user, slug, limit=limit)


@router.post("/catalog/{slug}/ratings")
def rate_plugin(
    slug: str,
    data: PluginRatingRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PluginSdkService.rate_plugin(db, user, slug, rating=data.rating, review=data.review)


@router.get("/hooks")
def plugin_hooks_catalog():
    from app.domain.plugins.hooks import HOOK_POINTS

    return {"hooks": HOOK_POINTS}


@router.get("/events")
def plugin_events_catalog():
    from app.domain.plugins.events import STUDIO_EVENTS

    return {"events": STUDIO_EVENTS}


@router.post("/catalog/{slug}/publish-version")
def publish_plugin_version(
    slug: str,
    data: PublishPluginVersionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PluginSdkService.publish_plugin(db, user, slug, changelog=data.changelog, release_notes=data.release_notes)


@router.post("/register", response_model=PluginDefinitionResponse, status_code=201)
def register_plugin(
    data: RegisterPluginRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return PluginSdkService.register_plugin(db, user, data.manifest)


@router.post("/test-event")
def test_emit_event(
    data: EmitTestEventRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    from app.domain.plugins.registry import PluginEventBus

    results = PluginEventBus.emit(db, data.event_name, data.payload, user_id=user.id)
    return {"event": data.event_name, "dispatched_to": len(results), "results": results}
