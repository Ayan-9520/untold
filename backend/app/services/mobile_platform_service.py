"""Mobile platform service — device registration, aggregated mobile APIs."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.domain.studio.enums import AIGenerationStatus, ApprovalStatus
from app.models import User
from app.models.studio import AIGeneration, MobileDevice, Production, StudioApproval, StudioNotification
from app.services.ai_studio_service import AIStudioService
from app.services.studio.dashboard_service import StudioDashboardService
from app.services.studio_platform_service import StudioPlatformService


class MobilePlatformService:
    @staticmethod
    def register_device(
        db: Session,
        user: User,
        *,
        app_type: str,
        platform: str,
        device_token: str,
        device_name: str | None = None,
        push_enabled: bool = True,
        meta: dict | None = None,
    ) -> dict:
        if app_type not in ("studio", "originals"):
            raise BadRequestError("app_type must be studio or originals")
        if platform not in ("ios", "android"):
            raise BadRequestError("platform must be ios or android")
        row = (
            db.query(MobileDevice)
            .filter(MobileDevice.user_id == user.id, MobileDevice.device_token == device_token)
            .first()
        )
        now = datetime.now(timezone.utc)
        if row:
            row.app_type = app_type
            row.platform = platform
            row.device_name = device_name
            row.push_enabled = push_enabled
            row.meta = {**(row.meta or {}), **(meta or {})}
            row.last_seen_at = now
        else:
            row = MobileDevice(
                user_id=user.id,
                app_type=app_type,
                platform=platform,
                device_token=device_token,
                device_name=device_name,
                push_enabled=push_enabled,
                meta=meta or {},
                last_seen_at=now,
            )
            db.add(row)
        db.commit()
        db.refresh(row)
        return MobilePlatformService._device_dict(row)

    @staticmethod
    def unregister_device(db: Session, user: User, device_id: int) -> None:
        row = db.query(MobileDevice).filter(MobileDevice.id == device_id, MobileDevice.user_id == user.id).first()
        if not row:
            raise NotFoundError("Device")
        db.delete(row)
        db.commit()

    @staticmethod
    def studio_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "studio.access")
        dash = StudioDashboardService.get_dashboard(db, user)
        ov = dash.overview
        pending = (
            db.query(func.count(StudioApproval.id))
            .filter(StudioApproval.status == ApprovalStatus.PENDING)
            .scalar()
            or 0
        )
        ai_running = (
            db.query(func.count(AIGeneration.id))
            .filter(AIGeneration.status == AIGenerationStatus.RUNNING, AIGeneration.created_by_id == user.id)
            .scalar()
            or 0
        )
        unread = (
            db.query(func.count(StudioNotification.id))
            .filter(StudioNotification.user_id == user.id, StudioNotification.is_read.is_(False))
            .scalar()
            or 0
        )
        return {
            "active_projects": ov.active_projects,
            "pending_reviews": ov.pending_reviews,
            "ai_jobs_running": ov.ai_jobs_running,
            "ai_jobs_queued": ov.ai_jobs_queued,
            "published_videos": ov.published_videos,
            "pending_approvals": int(pending),
            "my_ai_running": int(ai_running),
            "unread_notifications": int(unread),
        }

    @staticmethod
    def approvals_inbox(db: Session, user: User, *, limit: int = 50) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "studio.access")
        rows = (
            db.query(StudioApproval, Production)
            .join(Production, Production.id == StudioApproval.project_id)
            .filter(StudioApproval.status == ApprovalStatus.PENDING)
            .order_by(StudioApproval.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": a.id,
                "project_id": a.project_id,
                "project_title": p.title,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "status": a.status.value if hasattr(a.status, "value") else str(a.status),
                "notes": a.notes,
                "requested_by_id": a.requested_by_id,
                "created_at": a.created_at,
            }
            for a, p in rows
        ]

    @staticmethod
    def resolve_approval(db: Session, user: User, approval_id: int, *, action: str, notes: str | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, None, "studio.access")
        if action not in ("approve", "reject"):
            raise BadRequestError("action must be approve or reject")
        approval = db.query(StudioApproval).filter(StudioApproval.id == approval_id).first()
        if not approval:
            raise NotFoundError("Approval")
        approval.status = ApprovalStatus.APPROVED if action == "approve" else ApprovalStatus.REJECTED
        approval.approver_id = user.id
        approval.resolved_at = datetime.now(timezone.utc)
        if notes:
            approval.notes = notes
        db.commit()
        from app.services.mobile_push_service import MobilePushService

        MobilePushService.notify_user(
            db,
            approval.requested_by_id,
            title=f"Approval {action}d",
            body=f"{approval.entity_type} on project #{approval.project_id}",
            payload={"approval_id": approval.id, "action": action},
        )
        return {"id": approval.id, "status": approval.status.value}

    @staticmethod
    def ai_jobs(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "ai.generate")
        return AIStudioService.get_queue(db, user)

    @staticmethod
    def originals_home(db: Session, user: User | None) -> dict:
        from app.models import Video

        featured = (
            db.query(Video)
            .filter(Video.is_active.is_(True), Video.is_featured.is_(True))
            .order_by(Video.created_at.desc())
            .limit(10)
            .all()
        )
        recent = (
            db.query(Video)
            .filter(Video.is_active.is_(True))
            .order_by(Video.created_at.desc())
            .limit(20)
            .all()
        )

        def _vid(v):
            return {
                "id": v.id,
                "title": v.title,
                "thumbnail_url": v.thumbnail_url,
                "duration_seconds": v.duration_seconds,
                "video_type": v.video_type.value if hasattr(v.video_type, "value") else str(v.video_type),
            }

        return {
            "featured": [_vid(v) for v in featured],
            "recent": [_vid(v) for v in recent],
        }

    @staticmethod
    def offline_manifest(db: Session, user: User, *, app_type: str) -> dict:
        """Endpoints and cache hints for offline-capable mobile clients."""
        base = {
            "version": 1,
            "app_type": app_type,
            "sync_interval_seconds": 300,
            "queues": ["watch_progress", "analytics_events", "approval_actions"],
        }
        if app_type == "studio":
            base["endpoints"] = {
                "overview": "/mobile/studio/overview",
                "approvals": "/mobile/studio/approvals",
                "ai_jobs": "/mobile/studio/ai-jobs",
                "projects": "/studio/platform/projects",
                "notifications": "/studio/platform/notifications",
            }
        else:
            base["endpoints"] = {
                "home": "/mobile/originals/home",
                "continue_watching": "/continue-watching",
                "watchlist": "/watchlist",
            }
        return base

    @staticmethod
    def _device_dict(d: MobileDevice) -> dict:
        return {
            "id": d.id,
            "app_type": d.app_type,
            "platform": d.platform,
            "device_name": d.device_name,
            "push_enabled": d.push_enabled,
            "last_seen_at": d.last_seen_at,
            "created_at": d.created_at,
        }
