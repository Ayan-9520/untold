from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.models import Category, Video, VideoType
from app.schemas.video import VideoCreateRequest, VideoListParams, VideoUpdateRequest


class VideoService:
    @staticmethod
    def list_videos(db: Session, params: VideoListParams) -> tuple[list[Video], int]:
        query = (
            db.query(Video)
            .options(joinedload(Video.category))
            .filter(Video.is_active.is_(True))
        )

        if params.category:
            query = query.join(Category).filter(
                or_(Category.slug == params.category, Category.name.ilike(params.category))
            )

        if params.video_type:
            try:
                query = query.filter(Video.video_type == VideoType(params.video_type))
            except ValueError:
                pass

        if params.featured is not None:
            query = query.filter(Video.is_featured == params.featured)

        if params.trending is not None:
            query = query.filter(Video.is_trending == params.trending)

        if params.search:
            term = f"%{params.search}%"
            query = query.filter(or_(Video.title.ilike(term), Video.description.ilike(term)))

        total = query.count()
        videos = (
            query.order_by(Video.is_featured.desc(), Video.views_count.desc())
            .offset((params.page - 1) * params.page_size)
            .limit(params.page_size)
            .all()
        )
        return videos, total

    @staticmethod
    def get_by_id(db: Session, video_id: int, increment_views: bool = True) -> Video:
        video = (
            db.query(Video)
            .options(joinedload(Video.category))
            .filter(Video.id == video_id, Video.is_active.is_(True))
            .first()
        )
        if not video:
            raise NotFoundError("Video")

        if increment_views:
            video.views_count += 1
            db.commit()
            db.refresh(video)

        return video

    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Video:
        video = (
            db.query(Video)
            .options(joinedload(Video.category))
            .filter(Video.slug == slug, Video.is_active.is_(True))
            .first()
        )
        if not video:
            raise NotFoundError("Video")
        return video

    @staticmethod
    def create(db: Session, data: VideoCreateRequest) -> Video:
        video = Video(
            title=data.title,
            slug=data.slug,
            description=data.description,
            category_id=data.category_id,
            duration=data.duration,
            duration_seconds=data.duration_seconds,
            year=data.year,
            rating=data.rating,
            image_url=data.image_url,
            hero_image_url=data.hero_image_url,
            video_url=data.video_url,
            video_type=VideoType(data.video_type),
            is_featured=data.is_featured,
            is_trending=data.is_trending,
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return video

    @staticmethod
    def update(db: Session, video_id: int, data: VideoUpdateRequest) -> Video:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise NotFoundError("Video")

        update_data = data.model_dump(exclude_unset=True)
        if "video_type" in update_data:
            update_data["video_type"] = VideoType(update_data["video_type"])

        for field, value in update_data.items():
            setattr(video, field, value)

        db.commit()
        db.refresh(video)
        return video

    @staticmethod
    def delete(db: Session, video_id: int) -> None:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise NotFoundError("Video")
        video.is_active = False
        db.commit()
