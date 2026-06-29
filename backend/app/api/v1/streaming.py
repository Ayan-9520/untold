from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.access import get_user_plan, require_video_access
from app.core.deps import get_current_active_user, get_optional_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models import User, Video
from app.schemas.monetization import (
    ContinueWatchingItem,
    StreamResponse,
    WatchProgressRequest,
    WatchProgressResponse,
)
from app.services.streaming_service import StreamingService
from app.services.watch_service import WatchService

router = APIRouter(tags=["OTT Streaming"])


@router.get("/stream/{video_id}", response_model=StreamResponse)
def get_stream_url(
    video_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    video = db.query(Video).filter(Video.id == video_id, Video.is_active.is_(True)).first()
    if not video:
        raise NotFoundError("Video")

    if video.access_tier and video.access_tier != "free":
        if not current_user:
            from app.core.exceptions import UnauthorizedError

            raise UnauthorizedError("Login required for premium content")
        require_video_access(db, current_user, video, request)

    url, expires_in, fmt = StreamingService.get_signed_stream_url(
        video.id, video.stream_key, video.hls_url or video.video_url
    )
    return StreamResponse(
        video_id=video.id,
        stream_url=url,
        expires_in=expires_in,
        access_tier=video.access_tier or "free",
        format=fmt,
    )


@router.post("/watch-progress", response_model=WatchProgressResponse)
def save_watch_progress(
    data: WatchProgressRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    progress = WatchService.save_progress(
        db, current_user, data.video_id, data.position_seconds, data.duration_seconds
    )
    return WatchProgressResponse(message="Progress saved", progress_percent=progress.progress_percent)


@router.get("/continue-watching", response_model=list[ContinueWatchingItem])
def continue_watching(
    limit: int = Query(12, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return WatchService.get_continue_watching(db, current_user, limit=limit)
