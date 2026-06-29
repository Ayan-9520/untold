import json

from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError, NotFoundError
from app.models import Analytics, AnalyticsEventType, User, Video, Watchlist
from app.schemas.watchlist import WatchlistCreateRequest


class WatchlistService:
    @staticmethod
    def list_user_watchlist(db: Session, user: User) -> list[Watchlist]:
        return (
            db.query(Watchlist)
            .options(joinedload(Watchlist.video).joinedload(Video.category))
            .filter(Watchlist.user_id == user.id)
            .order_by(Watchlist.added_at.desc())
            .all()
        )

    @staticmethod
    def add_to_watchlist(db: Session, user: User, data: WatchlistCreateRequest) -> Watchlist:
        video = db.query(Video).filter(Video.id == data.video_id, Video.is_active.is_(True)).first()
        if not video:
            raise NotFoundError("Video")

        existing = (
            db.query(Watchlist)
            .filter(Watchlist.user_id == user.id, Watchlist.video_id == data.video_id)
            .first()
        )
        if existing:
            raise ConflictError("Video already in watchlist")

        item = Watchlist(user_id=user.id, video_id=data.video_id)
        db.add(item)

        event = Analytics(
            event_type=AnalyticsEventType.WATCHLIST_ADD,
            user_id=user.id,
            video_id=data.video_id,
        )
        db.add(event)
        db.commit()
        db.refresh(item)

        return (
            db.query(Watchlist)
            .options(joinedload(Watchlist.video).joinedload(Video.category))
            .filter(Watchlist.id == item.id)
            .first()
        )

    @staticmethod
    def remove_from_watchlist(db: Session, user: User, video_id: int) -> None:
        item = (
            db.query(Watchlist)
            .filter(Watchlist.user_id == user.id, Watchlist.video_id == video_id)
            .first()
        )
        if not item:
            raise NotFoundError("Watchlist item")

        db.delete(item)
        event = Analytics(
            event_type=AnalyticsEventType.WATCHLIST_REMOVE,
            user_id=user.id,
            video_id=video_id,
        )
        db.add(event)
        db.commit()

    @staticmethod
    def is_in_watchlist(db: Session, user: User, video_id: int) -> bool:
        return (
            db.query(Watchlist)
            .filter(Watchlist.user_id == user.id, Watchlist.video_id == video_id)
            .first()
            is not None
        )

    @staticmethod
    def toggle_watchlist(db: Session, user: User, video_id: int) -> tuple[bool, Watchlist | None]:
        if WatchlistService.is_in_watchlist(db, user, video_id):
            WatchlistService.remove_from_watchlist(db, user, video_id)
            return False, None

        item = WatchlistService.add_to_watchlist(db, user, WatchlistCreateRequest(video_id=video_id))
        return True, item
