"""Studio Analytics REST API."""

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.studio_analytics import RealtimeMetrics, StudioAnalyticsOverview
from app.services.studio_analytics_service import StudioAnalyticsService

router = APIRouter(prefix="/studio/platform/analytics", tags=["Studio Analytics"])


@router.get("/overview", response_model=StudioAnalyticsOverview)
def analytics_overview(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return StudioAnalyticsService.get_overview(db, user)


@router.get("/realtime", response_model=RealtimeMetrics)
def analytics_realtime(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return StudioAnalyticsService.get_realtime(db, user)


@router.get("/export/csv")
def export_analytics_csv(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    csv_data = StudioAnalyticsService.export_csv(db, user)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=untold-analytics.csv"},
    )


@router.get("/export/pdf")
def export_analytics_pdf(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    report = StudioAnalyticsService.export_pdf_text(db, user)
    return PlainTextResponse(
        content=report,
        headers={"Content-Disposition": "attachment; filename=untold-analytics-report.txt"},
    )
