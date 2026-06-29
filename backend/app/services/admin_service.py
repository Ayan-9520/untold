from sqlalchemy.orm import Session

from app.services.analytics_service import AnalyticsService
from app.services.category_service import CategoryService
from app.services.user_service import UserService
from app.services.video_service import VideoService
from app.schemas.category import CategoryCreateRequest
from app.schemas.video import VideoCreateRequest


class AdminService:
    @staticmethod
    def get_dashboard(db: Session):
        return AnalyticsService.get_dashboard_stats(db)

    @staticmethod
    def create_category(db: Session, data: CategoryCreateRequest):
        return CategoryService.create(db, data)

    @staticmethod
    def create_video(db: Session, data: VideoCreateRequest):
        return VideoService.create(db, data)

    @staticmethod
    def deactivate_user(db: Session, user_id: int):
        return UserService.deactivate_user(db, user_id)
