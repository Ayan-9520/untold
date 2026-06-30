"""API Gateway REST endpoints — v1 and v2."""

from __future__ import annotations

import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.domain.gateway.auth import GatewayAuth, get_gateway_auth
from app.schemas.api_gateway import GatewayWebhookCreate
from app.schemas.video import VideoListParams
from app.services.api_gateway_service import ApiGatewayService
from app.services.studio_service import StudioService
from app.services.video_service import VideoService

router = APIRouter(tags=["API Gateway"])


def _video_dict(v) -> dict:
    return {
        "id": v.id,
        "title": v.title,
        "slug": v.slug,
        "description": v.description,
        "image_url": v.image_url,
        "video_url": v.video_url,
        "duration_seconds": v.duration_seconds,
        "video_type": v.video_type.value if hasattr(v.video_type, "value") else str(v.video_type),
        "is_featured": v.is_featured,
        "is_trending": v.is_trending,
        "views_count": v.views_count,
        "created_at": v.created_at,
    }


def _project_dict(p) -> dict:
    return {
        "id": p.id,
        "title": p.title,
        "stage": p.stage,
        "description": p.description,
        "updated_at": p.updated_at,
        "created_at": p.created_at,
    }


def _respond(auth: GatewayAuth, data, **meta):
    if auth.api_version == "v2":
        return ApiGatewayService.wrap_v2(data, auth, **meta)
    return data


@router.get("/v1/me")
@router.get("/v2/me")
def gateway_me(auth: GatewayAuth = Depends(get_gateway_auth)):
    payload = {
        "user_id": auth.user.id,
        "email": auth.user.email,
        "auth_type": auth.auth_type,
        "api_version": auth.api_version,
        "scopes": auth.scopes,
        "rate_limit_tier": auth.api_key.rate_limit_tier if auth.api_key else "jwt",
    }
    return _respond(auth, payload)


@router.get("/v1/videos")
@router.get("/v2/videos")
def gateway_list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    auth: GatewayAuth = Depends(get_gateway_auth),
):
    auth.require_scope("videos.read")
    params = VideoListParams(page=page, page_size=page_size, search=search, category=category)
    videos, total = VideoService.list_videos(db, params)
    data = {
        "items": [_video_dict(v) for v in videos],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if total else 0,
    }
    return _respond(auth, data, page=page, total=total)


@router.get("/v1/videos/{video_id}")
@router.get("/v2/videos/{video_id}")
def gateway_get_video(
    video_id: int,
    db: Session = Depends(get_db),
    auth: GatewayAuth = Depends(get_gateway_auth),
):
    auth.require_scope("videos.read")
    video = VideoService.get_by_id(db, video_id)
    return _respond(auth, _video_dict(video))


@router.get("/v1/projects")
@router.get("/v2/projects")
def gateway_list_projects(
    stage: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    auth: GatewayAuth = Depends(get_gateway_auth),
):
    auth.require_scope("projects.read")
    items, total = StudioService.list_productions(db, stage=stage, limit=limit)
    data = {"items": [_project_dict(p) for p in items], "total": total}
    return _respond(auth, data, total=total)


@router.get("/v1/projects/{project_id}")
@router.get("/v2/projects/{project_id}")
def gateway_get_project(
    project_id: int,
    db: Session = Depends(get_db),
    auth: GatewayAuth = Depends(get_gateway_auth),
):
    auth.require_scope("projects.read")
    project = StudioService.get_production(db, project_id)
    if not project:
        raise NotFoundError("Project not found")
    return _respond(auth, _project_dict(project))


@router.get("/v1/analytics/overview")
@router.get("/v2/analytics/overview")
def gateway_analytics_overview(
    db: Session = Depends(get_db),
    auth: GatewayAuth = Depends(get_gateway_auth),
):
    auth.require_scope("analytics.read")
    overview = ApiGatewayService.overview(db, auth.user)
    public = {
        "requests_24h": overview["requests_24h"],
        "requests_7d": overview["requests_7d"],
        "avg_latency_ms": overview["avg_latency_ms"],
        "by_protocol": overview["by_protocol"],
    }
    return _respond(auth, public)


@router.get("/v1/webhooks")
def gateway_list_webhooks(
    db: Session = Depends(get_db),
    auth: GatewayAuth = Depends(get_gateway_auth),
):
    auth.require_scope("webhooks.manage")
    from app.models.studio_platform import ApiGatewayWebhook

    rows = db.query(ApiGatewayWebhook).filter(ApiGatewayWebhook.user_id == auth.user.id).all()
    return [ApiGatewayService._webhook_dict(w) for w in rows]


@router.post("/v1/webhooks", status_code=201)
def gateway_create_webhook(
    data: GatewayWebhookCreate,
    db: Session = Depends(get_db),
    auth: GatewayAuth = Depends(get_gateway_auth),
):
    auth.require_scope("webhooks.manage")
    return ApiGatewayService.create_webhook(
        db, auth.user, data, api_key_id=auth.api_key.id if auth.api_key else None
    )


@router.delete("/v1/webhooks/{webhook_id}", status_code=204)
def gateway_delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    auth: GatewayAuth = Depends(get_gateway_auth),
):
    auth.require_scope("webhooks.manage")
    ApiGatewayService.delete_webhook(db, auth.user, webhook_id)
