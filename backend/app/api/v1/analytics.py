from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_optional_user
from app.db.session import get_db
from app.models import User
from app.schemas.analytics import (
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    AnalyticsSummary,
    DashboardStats,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsSummary)
def get_analytics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return AnalyticsService.get_summary(db)


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return AnalyticsService.get_dashboard_stats(db)


@router.get("/events", response_model=list[AnalyticsEventResponse])
def list_events(
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return AnalyticsService.list_recent_events(db, limit)


@router.post("/events", response_model=AnalyticsEventResponse, status_code=201)
def track_event(
    data: AnalyticsEventCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return AnalyticsService.track_event(
        db,
        data,
        user_id=current_user.id if current_user else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
