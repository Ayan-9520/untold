"""Studio dashboard aggregation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.studio.enums import (
    AIGenerationStatus,
    ApprovalStatus,
    PROJECT_STAGES,
    PublishingStatus,
    TaskStatus,
)
from app.domain.studio.permissions import StudioPermissionService
from app.models import User, Video
from app.models.studio import (
    AIGeneration,
    PublishJob,
    StudioApproval,
    StudioAsset,
    StudioNotification,
    StudioTask,
)
from app.models.studio.core import Production
from app.repositories.activity_repository import ActivityRepository
from app.schemas.studio_platform import (
    DashboardOverview,
    DashboardResponse,
    MonthlyMetric,
    PipelineStageCount,
    StatusCount,
)
from app.services.analytics_service import AnalyticsService
from app.services.revenue_service import RevenueService
from app.services.studio.project_service import StudioProjectService


class StudioDashboardService:
    @staticmethod
    def get_dashboard(db: Session, user: User) -> DashboardResponse:
        if not user.is_admin:
            StudioPermissionService.require_permission(db, user, None, "studio.access")
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        deadline_horizon = today + timedelta(days=14)

        active_projects = db.query(func.count(Production.id)).filter(Production.status == "active").scalar() or 0
        todays_tasks_count = (
            db.query(func.count(StudioTask.id))
            .filter(StudioTask.due_date >= today, StudioTask.status != TaskStatus.DONE)
            .scalar()
            or 0
        )
        pending_reviews = (
            db.query(func.count(StudioApproval.id))
            .filter(StudioApproval.status == ApprovalStatus.PENDING)
            .scalar()
            or 0
        )
        ai_running = (
            db.query(func.count(AIGeneration.id))
            .filter(AIGeneration.status == AIGenerationStatus.RUNNING)
            .scalar()
            or 0
        )
        ai_queued = (
            db.query(func.count(AIGeneration.id))
            .filter(AIGeneration.status == AIGenerationStatus.QUEUED)
            .scalar()
            or 0
        )
        published_videos = (
            db.query(func.count(Production.id))
            .filter(Production.publishing_status == PublishingStatus.PUBLISHED)
            .scalar()
            or 0
        )
        if published_videos == 0:
            published_videos = db.query(func.count(Video.id)).filter(Video.is_active.is_(True)).scalar() or 0

        storage_bytes = db.query(func.coalesce(func.sum(StudioAsset.size_bytes), 0)).scalar() or 0
        publishing_queue = db.query(func.count(PublishJob.id)).filter(PublishJob.status == "pending").scalar() or 0
        revenue = RevenueService.get_summary(db)
        analytics = AnalyticsService.get_summary(db)

        pipeline_rows = (
            db.query(Production.stage, func.count(Production.id))
            .filter(Production.status == "active")
            .group_by(Production.stage)
            .all()
        )
        pipeline_map = {row[0]: row[1] for row in pipeline_rows}
        production_pipeline = [
            PipelineStageCount(stage=s, count=pipeline_map.get(s, 0)) for s in PROJECT_STAGES
        ]
        for stage, count in pipeline_map.items():
            if stage not in PROJECT_STAGES:
                production_pipeline.append(PipelineStageCount(stage=stage, count=count))

        status_rows = db.query(Production.status, func.count(Production.id)).group_by(Production.status).all()
        project_status = [StatusCount(label=row[0], count=row[1]) for row in status_rows]

        monthly_analytics: list[MonthlyMetric] = []
        for entry in revenue.monthly_revenue:
            monthly_analytics.append(
                MonthlyMetric(
                    month=entry["month"],
                    revenue=float(entry.get("revenue", 0)),
                    views=int(analytics.total_views / 6),
                    productions=max(1, active_projects // 6),
                )
            )

        projects, _ = StudioProjectService.list_projects(db, user, limit=8)
        activity = ActivityRepository(db).recent(12)
        approvals = (
            db.query(StudioApproval)
            .filter(StudioApproval.status == ApprovalStatus.PENDING)
            .order_by(StudioApproval.created_at.desc())
            .limit(5)
            .all()
        )
        tasks_today = (
            db.query(StudioTask)
            .filter(StudioTask.due_date >= today, StudioTask.status != TaskStatus.DONE)
            .order_by(StudioTask.due_date.asc())
            .limit(5)
            .all()
        )
        upcoming_deadlines = (
            db.query(StudioTask)
            .filter(
                StudioTask.due_date.isnot(None),
                StudioTask.due_date <= deadline_horizon,
                StudioTask.status != TaskStatus.DONE,
            )
            .order_by(StudioTask.due_date.asc())
            .limit(8)
            .all()
        )
        notifications = (
            db.query(StudioNotification)
            .filter(StudioNotification.user_id == user.id)
            .order_by(StudioNotification.created_at.desc())
            .limit(8)
            .all()
        )

        return DashboardResponse(
            overview=DashboardOverview(
                active_projects=active_projects,
                pending_reviews=pending_reviews,
                todays_tasks=todays_tasks_count,
                ai_jobs_running=ai_running,
                published_videos=published_videos,
                storage_bytes=int(storage_bytes),
                publishing_queue=publishing_queue,
                ai_jobs_queued=ai_queued,
                revenue_mrr=float(revenue.mrr),
                total_views=analytics.total_views,
            ),
            production_pipeline=production_pipeline,
            monthly_analytics=monthly_analytics,
            project_status=project_status,
            recent_projects=projects,
            recent_activity=activity,
            upcoming_deadlines=upcoming_deadlines,
            notifications=notifications,
            pending_approvals=approvals,
            todays_tasks=tasks_today,
        )
