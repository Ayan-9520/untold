"""Sandbox API Gateway — sample data, no production side effects."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.domain.gateway.auth import GatewayAuth, get_gateway_auth
from app.services.api_gateway_service import ApiGatewayService

router = APIRouter(tags=["Sandbox API Gateway"])

SANDBOX_VIDEOS = [
    {
        "id": 9001,
        "title": "[Sandbox] UNTOLD: Sample Documentary",
        "slug": "sandbox-sample-doc",
        "description": "Sandbox sample video — not real production data.",
        "image_url": None,
        "video_url": None,
        "duration_seconds": 3600,
        "video_type": "documentary",
        "is_featured": True,
        "is_trending": False,
        "views_count": 1200,
        "created_at": "2026-01-01T00:00:00Z",
    },
    {
        "id": 9002,
        "title": "[Sandbox] Rise of a Legend",
        "slug": "sandbox-rise-legend",
        "description": "Second sandbox title for integration tests.",
        "image_url": None,
        "video_url": None,
        "duration_seconds": 2700,
        "video_type": "original",
        "is_featured": False,
        "is_trending": True,
        "views_count": 890,
        "created_at": "2026-01-15T00:00:00Z",
    },
]

SANDBOX_PROJECTS = [
    {
        "id": 8001,
        "title": "[Sandbox] Research Project Alpha",
        "stage": "research",
        "description": "Sample studio project in sandbox.",
        "updated_at": "2026-02-01T00:00:00Z",
        "created_at": "2026-01-01T00:00:00Z",
    },
]


def _respond(auth: GatewayAuth, data, **meta):
    if auth.api_version == "v2":
        return ApiGatewayService.wrap_v2(data, auth, **meta)
    return data


@router.get("/v1/me")
@router.get("/v2/me")
def sandbox_me(auth: GatewayAuth = Depends(get_gateway_auth)):
    payload = {
        "user_id": auth.user.id,
        "email": auth.user.email,
        "environment": "sandbox",
        "auth_type": auth.auth_type,
        "api_version": auth.api_version,
        "scopes": auth.scopes,
    }
    return _respond(auth, payload)


@router.get("/v1/videos")
@router.get("/v2/videos")
def sandbox_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    auth: GatewayAuth = Depends(get_gateway_auth),
):
    auth.require_scope("videos.read")
    items = SANDBOX_VIDEOS[(page - 1) * page_size : page * page_size]
    data = {"items": items, "total": len(SANDBOX_VIDEOS), "page": page, "page_size": page_size, "pages": 1}
    return _respond(auth, data, page=page, total=len(SANDBOX_VIDEOS))


@router.get("/v1/videos/{video_id}")
@router.get("/v2/videos/{video_id}")
def sandbox_video(video_id: int, auth: GatewayAuth = Depends(get_gateway_auth)):
    auth.require_scope("videos.read")
    for v in SANDBOX_VIDEOS:
        if v["id"] == video_id:
            return _respond(auth, v)
    return _respond(auth, {**SANDBOX_VIDEOS[0], "id": video_id})


@router.get("/v1/projects")
@router.get("/v2/projects")
def sandbox_projects(limit: int = Query(50, ge=1, le=200), auth: GatewayAuth = Depends(get_gateway_auth)):
    auth.require_scope("projects.read")
    data = {"items": SANDBOX_PROJECTS[:limit], "total": len(SANDBOX_PROJECTS)}
    return _respond(auth, data, total=len(SANDBOX_PROJECTS))
