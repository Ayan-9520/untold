"""Watch progress, continue watching, watch history."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import User, Video
from app.models.monetization import VideoProgress, WatchHistory


class WatchService:
    @staticmethod
    def save_progress(
        db: Session,
        user: User,
        video_id: int,
        position_seconds: int,
        duration_seconds: int | None = None,
    ) -> VideoProgress:
        video = db.query(Video).filter(Video.id == video_id, Video.is_active.is_(True)).first()
        if not video:
            from app.core.exceptions import NotFoundError

            raise NotFoundError("Video")

        duration = duration_seconds or video.duration_seconds or 0
        percent = (position_seconds / duration * 100) if duration > 0 else 0
        completed = percent >= 90

        progress = (
            db.query(VideoProgress)
            .filter(VideoProgress.user_id == user.id, VideoProgress.video_id == video_id)
            .first()
        )
        if progress:
            progress.position_seconds = position_seconds
            progress.duration_seconds = duration or progress.duration_seconds
            progress.progress_percent = min(percent, 100.0)
            progress.updated_at = datetime.now(timezone.utc)
        else:
            progress = VideoProgress(
                user_id=user.id,
                video_id=video_id,
                position_seconds=position_seconds,
                duration_seconds=duration,
                progress_percent=min(percent, 100.0),
            )
            db.add(progress)

        if completed or position_seconds > 30:
            history = WatchHistory(
                user_id=user.id,
                video_id=video_id,
                watched_seconds=position_seconds,
                completed=completed,
            )
            db.add(history)

        db.commit()
        db.refresh(progress)
        return progress

    @staticmethod
    def get_continue_watching(db: Session, user: User, limit: int = 12) -> list[dict]:
        rows = (
            db.query(VideoProgress)
            .filter(
                VideoProgress.user_id == user.id,
                VideoProgress.progress_percent > 2,
                VideoProgress.progress_percent < 95,
            )
            .order_by(VideoProgress.updated_at.desc())
            .limit(limit)
            .all()
        )

        items = []
        for row in rows:
            video = db.query(Video).filter(Video.id == row.video_id).first()
            if not video:
                continue
            items.append(
                {
                    "video_id": video.id,
                    "title": video.title,
                    "image_url": video.image_url or video.hero_image_url,
                    "position_seconds": row.position_seconds,
                    "duration_seconds": row.duration_seconds or video.duration_seconds,
                    "progress_percent": row.progress_percent,
                    "updated_at": row.updated_at,
                }
            )
        return items
