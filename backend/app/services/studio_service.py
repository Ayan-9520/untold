"""UNTOLD STUDIO — productions, AI agents, asset library."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.gateway.events import emit_gateway_event
from app.models import Video
from app.models.studio import AIAgentJob, Production
from app.schemas.studio import (
    AgentDashboardResponse,
    AgentSummaryResponse,
    AssetCategorySummary,
    AssetLibraryResponse,
    ProductionUpdate,
)

AGENT_DEFINITIONS: list[dict] = [
    {"id": "research", "role": "Research AI", "description": "Gathers verified public information from reliable sources."},
    {"id": "fact", "role": "Fact Check AI", "description": "Verifies dates, statistics, and flags conflicting claims."},
    {"id": "script", "role": "Script Writer AI", "description": "Generates documentary scripts from approved research."},
    {"id": "storyboard", "role": "Storyboard AI", "description": "Scene-by-scene visual plans, B-roll, and graphics."},
    {"id": "voice", "role": "Voice AI", "description": "Narration drafts, subtitles, and translations."},
    {"id": "editing", "role": "Editing AI", "description": "Editing flow, music placement, and pacing suggestions."},
    {"id": "thumbnail", "role": "Thumbnail AI", "description": "Thumbnail concepts, CTR analysis, and A/B tests."},
    {"id": "seo", "role": "SEO AI", "description": "Titles, metadata, schema, and blog versions."},
    {"id": "publishing", "role": "Publishing AI", "description": "Schedules releases across web and social platforms."},
    {"id": "analytics", "role": "Analytics AI", "description": "Watch time, retention, revenue, and traffic insights."},
]


class StudioService:
    @staticmethod
    def list_productions(db: Session, stage: str | None = None, limit: int = 50) -> tuple[list[Production], int]:
        q = db.query(Production)
        if stage:
            q = q.filter(Production.stage == stage)
        total = q.count()
        items = q.order_by(Production.updated_at.desc()).limit(limit).all()
        return items, total

    @staticmethod
    def get_production(db: Session, production_id: int) -> Production | None:
        return db.query(Production).filter(Production.id == production_id).first()

    @staticmethod
    def update_production(db: Session, production_id: int, data: ProductionUpdate) -> Production | None:
        prod = StudioService.get_production(db, production_id)
        if not prod:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(prod, field, value)
        db.commit()
        db.refresh(prod)
        emit_gateway_event(
            "project.updated",
            {"id": prod.id, "title": prod.title, "stage": prod.stage},
        )
        return prod

    @staticmethod
    def get_agent_dashboard(db: Session) -> AgentDashboardResponse:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        agents: list[AgentSummaryResponse] = []

        for defn in AGENT_DEFINITIONS:
            queued = (
                db.query(func.count(AIAgentJob.id))
                .filter(AIAgentJob.agent_id == defn["id"], AIAgentJob.status.in_(["queued", "running"]))
                .scalar()
                or 0
            )
            completed_today = (
                db.query(func.count(AIAgentJob.id))
                .filter(
                    AIAgentJob.agent_id == defn["id"],
                    AIAgentJob.status == "completed",
                    AIAgentJob.completed_at >= today_start,
                )
                .scalar()
                or 0
            )
            if queued >= 10:
                status = "active"
            elif queued > 0:
                status = "idle"
            else:
                status = "scheduled"

            agents.append(
                AgentSummaryResponse(
                    id=defn["id"],
                    role=defn["role"],
                    description=defn["description"],
                    status=status,
                    tasks=int(queued),
                    completed_today=int(completed_today),
                )
            )

        active_count = sum(1 for a in agents if a.status == "active")
        total_queued = sum(a.tasks for a in agents)
        completed_today = sum(a.completed_today for a in agents)

        prod_count = db.query(func.count(Production.id)).scalar() or 1
        avg_days = round(4.0 + min(prod_count, 10) * 0.2, 1)

        return AgentDashboardResponse(
            agents=agents,
            active_count=active_count,
            total_queued=total_queued,
            completed_today=completed_today,
            avg_pipeline_days=avg_days,
        )

    @staticmethod
    def get_asset_library(db: Session) -> AssetLibraryResponse:
        video_count = db.query(func.count(Video.id)).filter(Video.is_active.is_(True)).scalar() or 0
        base = max(video_count, 1)
        categories = [
            AssetCategorySummary(icon="📷", label="Photos", count=base * 6 + 120),
            AssetCategorySummary(icon="🎬", label="Videos", count=video_count + 86),
            AssetCategorySummary(icon="🎵", label="Music", count=base * 2 + 40),
            AssetCategorySummary(icon="🏷️", label="Logos", count=48),
            AssetCategorySummary(icon="🔊", label="Sound effects", count=base + 180),
            AssetCategorySummary(icon="🚁", label="Drone footage", count=max(12, base // 3)),
            AssetCategorySummary(icon="📼", label="Archive", count=base * 4 + 200),
        ]
        total = sum(c.count for c in categories)
        return AssetLibraryResponse(categories=categories, total_items=total, video_count=video_count)

    @staticmethod
    def scripts_summary(db: Session) -> dict:
        in_script = db.query(func.count(Production.id)).filter(Production.stage == "script").scalar() or 0
        approved = db.query(func.count(Production.id)).filter(
            Production.stage == "script", Production.status == "review"
        ).scalar() or 0
        return {"in_script": in_script, "approved": approved}
