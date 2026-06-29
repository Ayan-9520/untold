import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.db.session import get_db
from app.models import User
from app.schemas.analytics import DashboardStats
from app.schemas.auth import UserResponse
from app.schemas.category import CategoryCreateRequest, CategoryResponse
from app.schemas.common import PaginatedResponse
from app.schemas.video import VideoCreateRequest, VideoResponse
from app.services.admin_service import AdminService
from app.services.revenue_service import RevenueService
from app.services.user_service import UserService
from app.schemas.revenue import RevenueSummary

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=DashboardStats)
def admin_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return AdminService.get_dashboard(db)


@router.get("/users", response_model=PaginatedResponse[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    users, total = UserService.list_users(db, skip=(page - 1) * page_size, limit=page_size)
    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return AdminService.deactivate_user(db, user_id)


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def admin_create_category(
    data: CategoryCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return AdminService.create_category(db, data)


@router.post("/videos", response_model=VideoResponse, status_code=201)
def admin_create_video(
    data: VideoCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return AdminService.create_video(db, data)


@router.get("/revenue", response_model=RevenueSummary)
def get_revenue(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return RevenueService.get_summary(db)
