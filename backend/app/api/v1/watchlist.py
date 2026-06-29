from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models import User
from app.schemas.common import MessageResponse
from app.schemas.watchlist import WatchlistCreateRequest, WatchlistResponse, WatchlistToggleResponse
from app.services.watchlist_service import WatchlistService

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.get("", response_model=list[WatchlistResponse])
def get_watchlist(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return WatchlistService.list_user_watchlist(db, current_user)


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    data: WatchlistCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return WatchlistService.add_to_watchlist(db, current_user, data)


@router.post("/toggle/{video_id}", response_model=WatchlistToggleResponse)
def toggle_watchlist(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    in_list, item = WatchlistService.toggle_watchlist(db, current_user, video_id)
    return WatchlistToggleResponse(
        message="Added to watchlist" if in_list else "Removed from watchlist",
        in_watchlist=in_list,
        item=item,
    )


@router.delete("/{video_id}", response_model=MessageResponse)
def remove_from_watchlist(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    WatchlistService.remove_from_watchlist(db, current_user, video_id)
    return MessageResponse(message="Removed from watchlist")
