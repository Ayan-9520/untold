import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.cache import cache_get, cache_key, cache_set
from app.core.cache import cache_get, cache_key, cache_set
from app.core.deps import get_current_admin, get_optional_user
from app.db.session import get_db
from app.models import User
from app.schemas.common import PaginatedResponse
from app.schemas.video import VideoCreateRequest, VideoListParams, VideoResponse, VideoUpdateRequest
from app.services.video_service import VideoService

router = APIRouter(tags=["Videos"])
_TRENDING_CACHE_TTL = 120
_TRENDING_CACHE_TTL = 120


@router.get("/videos", response_model=PaginatedResponse[VideoResponse])
def list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = None,
    video_type: str | None = None,
    featured: bool | None = None,
    trending: bool | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    cacheable = trending is True and not search and not category and page == 1
    key = cache_key("videos", "trending", str(page_size), str(featured)) if cacheable else None
    if key:
        cached = cache_get(key)
        if cached:
            return PaginatedResponse[VideoResponse](**cached)

    params = VideoListParams(
        page=page,
        page_size=page_size,
        category=category,
        video_type=video_type,
        featured=featured,
        trending=trending,
        search=search,
    )
    videos, total = VideoService.list_videos(db, params)
    response = PaginatedResponse(
        items=videos,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )
    if key:
        cache_set(key, response.model_dump(mode="json"), ttl=_TRENDING_CACHE_TTL)
    return response


@router.get("/videos/{video_id}", response_model=VideoResponse)
def get_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return VideoService.get_by_id(db, video_id)


@router.get("/video/{video_id}", response_model=VideoResponse, include_in_schema=True)
def get_video_singular(video_id: int, db: Session = Depends(get_db)):
    """Alias endpoint: GET /video/{id}"""
    return VideoService.get_by_id(db, video_id)


@router.post("/videos", response_model=VideoResponse, status_code=201)
def create_video(
    data: VideoCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return VideoService.create(db, data)


@router.patch("/videos/{video_id}", response_model=VideoResponse)
def update_video(
    video_id: int,
    data: VideoUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return VideoService.update(db, video_id, data)


@router.delete("/videos/{video_id}", status_code=204)
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    VideoService.delete(db, video_id)
