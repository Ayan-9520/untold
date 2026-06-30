"""GraphQL schema for API Gateway."""

from __future__ import annotations

from typing import Optional

import strawberry
from sqlalchemy.orm import Session
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from app.core.exceptions import UnauthorizedError
from app.db.session import SessionLocal
from app.domain.gateway.auth import GatewayAuth, resolve_gateway_auth
from app.schemas.video import VideoListParams
from app.services.studio_service import StudioService
from app.services.video_service import VideoService


@strawberry.type
class GatewayVideo:
    id: int
    title: str
    slug: str
    description: Optional[str]
    image_url: Optional[str]
    video_type: str
    views_count: int


@strawberry.type
class GatewayProject:
    id: int
    title: str
    stage: str
    description: Optional[str]


@strawberry.type
class GatewayMe:
    user_id: int
    email: str
    scopes: list[str]
    api_version: str


@strawberry.type
class VideoConnection:
    items: list[GatewayVideo]
    total: int


def _auth(info: Info) -> GatewayAuth:
    auth = info.context.get("gateway_auth")
    if not auth:
        raise UnauthorizedError("GraphQL requires gateway authentication")
    return auth


def _db(info: Info) -> Session:
    return info.context["db"]


@strawberry.type
class Query:
    @strawberry.field
    def me(self, info: Info) -> GatewayMe:
        auth = _auth(info)
        return GatewayMe(
            user_id=auth.user.id,
            email=auth.user.email,
            scopes=auth.scopes,
            api_version=auth.api_version,
        )

    @strawberry.field
    def videos(self, info: Info, page: int = 1, page_size: int = 20, search: Optional[str] = None) -> VideoConnection:
        auth = _auth(info)
        auth.require_scope("graphql.query")
        auth.require_scope("videos.read")
        db = _db(info)
        params = VideoListParams(page=page, page_size=page_size, search=search)
        rows, total = VideoService.list_videos(db, params)
        items = [
            GatewayVideo(
                id=v.id,
                title=v.title,
                slug=v.slug,
                description=v.description,
                image_url=v.image_url,
                video_type=str(v.video_type.value if hasattr(v.video_type, "value") else v.video_type),
                views_count=v.views_count,
            )
            for v in rows
        ]
        return VideoConnection(items=items, total=total)

    @strawberry.field
    def video(self, info: Info, id: int) -> Optional[GatewayVideo]:
        auth = _auth(info)
        auth.require_scope("graphql.query")
        auth.require_scope("videos.read")
        db = _db(info)
        v = VideoService.get_by_id(db, id)
        return GatewayVideo(
            id=v.id,
            title=v.title,
            slug=v.slug,
            description=v.description,
            image_url=v.image_url,
            video_type=str(v.video_type.value if hasattr(v.video_type, "value") else v.video_type),
            views_count=v.views_count,
        )

    @strawberry.field
    def projects(self, info: Info, limit: int = 20) -> list[GatewayProject]:
        auth = _auth(info)
        auth.require_scope("graphql.query")
        auth.require_scope("projects.read")
        db = _db(info)
        rows, _ = StudioService.list_productions(db, limit=limit)
        return [GatewayProject(id=p.id, title=p.title, stage=p.stage, description=p.description) for p in rows]


schema = strawberry.Schema(query=Query)


async def graphql_context_getter(request):
    db = SessionLocal()
    try:
        auth = resolve_gateway_auth(request, db)
        auth.require_scope("graphql.query")
        return {"request": request, "gateway_auth": auth, "db": db}
    except Exception:
        db.close()
        raise


def create_graphql_router() -> GraphQLRouter:
    return GraphQLRouter(schema, context_getter=graphql_context_getter)
