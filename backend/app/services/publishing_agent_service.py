"""AI Publishing Agent — multi-platform orchestration, webhooks, analytics."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.domain.publishing.providers.demo import DemoPlatformPublisher
from app.domain.publishing.types import PLATFORM_LABELS, PUBLISH_PLATFORMS, WEBHOOK_EVENTS
from app.domain.publishing.webhooks import deliver_webhooks
from app.domain.studio.enums import ApprovalStatus, PublishPlatform
from app.models import User
from app.models.studio import Production
from app.models.studio_platform import (
    PublishAgentRun,
    PublishJob,
    PublishPlatformEvent,
    PublishWebhook,
    StudioApproval,
    StudioNotification,
)
from app.schemas.publishing_agent import (
    PublishingAgentCreate,
    PublishingAgentRetryRequest,
    WebhookCreate,
    WebhookUpdate,
)
from app.services.publishing_cms_service import PublishingCmsService
from app.services.studio_platform_service import StudioPlatformService

_PUBLISHER = DemoPlatformPublisher()
_VALID_PLATFORMS = {p for p, _ in PUBLISH_PLATFORMS}


class PublishingAgentService:
    @staticmethod
    def _run_dict(run: PublishAgentRun, project: Production | None = None) -> dict:
        meta = run.output_meta or {}
        return {
            "id": run.id,
            "project_id": run.project_id,
            "project_title": project.title if project else None,
            "platforms": run.platforms or [],
            "scheduled_at": run.scheduled_at,
            "status": run.status,
            "requires_approval": run.requires_approval,
            "approval_status": run.approval_status,
            "progress": run.progress,
            "jobs": meta.get("jobs", []),
            "webhook_deliveries": meta.get("webhook_deliveries", []),
            "error_message": run.error_message,
            "created_by_id": run.created_by_id,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "created_at": run.created_at,
        }

    @staticmethod
    def _track_event(
        db: Session,
        *,
        project_id: int,
        platform: str,
        event_type: str,
        agent_run_id: int | None = None,
        publish_job_id: int | None = None,
        payload: dict | None = None,
    ) -> None:
        db.add(
            PublishPlatformEvent(
                project_id=project_id,
                agent_run_id=agent_run_id,
                publish_job_id=publish_job_id,
                platform=platform,
                event_type=event_type,
                payload=payload or {},
            )
        )

    @staticmethod
    def _notify(db: Session, user_id: int | None, title: str, body: str, data: dict) -> None:
        if not user_id:
            return
        db.add(
            StudioNotification(
                user_id=user_id,
                notification_type="publish_agent",
                title=title,
                body=body,
                data=data,
            )
        )

    @staticmethod
    def get_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.schedule")
        PublishingCmsService.seed_demo_jobs(db)

        total_runs = db.query(func.count(PublishAgentRun.id)).scalar() or 0
        active = (
            db.query(func.count(PublishAgentRun.id))
            .filter(PublishAgentRun.status.in_(["queued", "running", "pending_approval"]))
            .scalar()
            or 0
        )
        failed_jobs = db.query(func.count(PublishJob.id)).filter(PublishJob.status == "failed").scalar() or 0
        published_jobs = db.query(func.count(PublishJob.id)).filter(PublishJob.status == "published").scalar() or 0
        webhook_count = db.query(func.count(PublishWebhook.id)).filter(PublishWebhook.is_active.is_(True)).scalar() or 0

        platform_rows = (
            db.query(PublishPlatformEvent.platform, func.count(PublishPlatformEvent.id))
            .filter(PublishPlatformEvent.event_type == "publish.success")
            .group_by(PublishPlatformEvent.platform)
            .all()
        )
        analytics_by_platform = {p: c for p, c in platform_rows}

        job_counts = (
            db.query(PublishJob.status, func.count(PublishJob.id)).group_by(PublishJob.status).all()
        )
        queue_counts = {s: c for s, c in job_counts}

        return {
            "platforms": [{"id": p, "label": l} for p, l in PUBLISH_PLATFORMS],
            "webhook_events": list(WEBHOOK_EVENTS),
            "total_runs": total_runs,
            "active_runs": active,
            "failed_jobs": failed_jobs,
            "published_jobs": published_jobs,
            "webhook_count": webhook_count,
            "analytics_by_platform": analytics_by_platform,
            "queue_counts": queue_counts,
        }

    @staticmethod
    def create_run(db: Session, user: User, data: PublishingAgentCreate) -> PublishAgentRun:
        StudioPlatformService.require_permission(db, user, data.project_id, "publish.schedule")
        project = db.query(Production).filter(Production.id == data.project_id).first()
        if not project:
            raise NotFoundError("Project")

        platforms = [p for p in data.platforms if p in _VALID_PLATFORMS]
        if not platforms:
            raise ConflictError("At least one valid platform is required")

        if data.seo_title:
            project.seo_title = data.seo_title
        if data.seo_description:
            project.seo_description = data.seo_description
        if data.seo_keywords:
            project.seo_keywords = data.seo_keywords
        if data.thumbnail_url:
            project.thumbnail_url = data.thumbnail_url

        approval_status = "pending" if data.requires_approval else "approved"
        status = "pending_approval" if data.requires_approval else ("scheduled" if data.scheduled_at else "queued")

        run = PublishAgentRun(
            project_id=data.project_id,
            platforms=platforms,
            scheduled_at=data.scheduled_at,
            requires_approval=data.requires_approval,
            approval_status=approval_status,
            status=status,
            output_meta={"jobs": []},
            created_by_id=user.id,
        )
        db.add(run)
        db.flush()

        job_rows: list[dict] = []
        for plat in platforms:
            try:
                pub_plat = PublishPlatform(plat)
            except ValueError:
                continue
            job_status = status
            if data.requires_approval:
                job_status = "pending_approval"
            elif data.scheduled_at:
                job_status = "scheduled"
            else:
                job_status = "queued"

            job = PublishJob(
                project_id=data.project_id,
                platform=pub_plat,
                agent_run_id=run.id,
                scheduled_at=data.scheduled_at,
                requires_approval=data.requires_approval,
                approval_status=approval_status,
                status=job_status,
                seo_title=data.seo_title or project.seo_title,
                seo_description=data.seo_description or project.seo_description,
                seo_keywords=data.seo_keywords or project.seo_keywords,
                thumbnail_url=data.thumbnail_url or project.thumbnail_url,
                meta={"agent_run_id": run.id},
                created_by_id=user.id,
            )
            db.add(job)
            db.flush()
            job_rows.append({
                "id": job.id,
                "platform": plat,
                "status": job.status,
                "approval_status": job.approval_status,
            })
            PublishingAgentService._track_event(
                db,
                project_id=data.project_id,
                platform=plat,
                event_type="publish.queued",
                agent_run_id=run.id,
                publish_job_id=job.id,
            )

        if data.requires_approval:
            db.add(
                StudioApproval(
                    project_id=data.project_id,
                    entity_type="publish_agent_run",
                    entity_id=run.id,
                    requested_by_id=user.id,
                    status=ApprovalStatus.PENDING,
                    notes=f"Publish to {', '.join(platforms)}",
                )
            )

        meta = dict(run.output_meta or {})
        meta["jobs"] = job_rows
        run.output_meta = meta

        deliveries = deliver_webhooks(
            db,
            "publish.queued",
            {"run_id": run.id, "project_id": run.project_id, "platforms": platforms, "jobs": job_rows},
            project_id=run.project_id,
        )
        meta["webhook_deliveries"] = deliveries
        run.output_meta = meta

        StudioPlatformService.log_activity(
            db, user.id, "publish.agent_queued", data.project_id, "publish_agent_run", run.id,
        )

        if not data.requires_approval and not data.scheduled_at:
            from app.workers.publish_tasks import process_publish_agent_run

            task = process_publish_agent_run.delay(run.id)
            run.celery_task_id = task.id
            run.status = "running"
        elif data.scheduled_at:
            deliver_webhooks(
                db,
                "publish.scheduled",
                {"run_id": run.id, "scheduled_at": data.scheduled_at.isoformat()},
                project_id=run.project_id,
            )

        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def execute_run(db: Session, run_id: int) -> dict:
        run = db.query(PublishAgentRun).filter(PublishAgentRun.id == run_id).first()
        if not run or run.status in ("completed", "cancelled"):
            return {"run_id": run_id, "status": run.status if run else "not_found"}

        if run.requires_approval and run.approval_status != "approved":
            return {"run_id": run_id, "status": "pending_approval"}

        if run.scheduled_at and run.scheduled_at > datetime.now(timezone.utc):
            return {"run_id": run_id, "status": "scheduled"}

        project = db.query(Production).filter(Production.id == run.project_id).first()
        if not project:
            raise NotFoundError("Project")

        user = db.query(User).filter(User.id == run.created_by_id).first() if run.created_by_id else None
        if not user:
            user = db.query(User).filter(User.is_admin.is_(True)).first()

        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        run.progress = 5
        db.commit()

        jobs = (
            db.query(PublishJob)
            .filter(PublishJob.agent_run_id == run_id)
            .order_by(PublishJob.id.asc())
            .all()
        )
        total = len(jobs) or 1
        job_results: list[dict] = []
        success_count = 0
        fail_count = 0

        for i, job in enumerate(jobs):
            if job.status == "published":
                success_count += 1
                job_results.append({"id": job.id, "platform": job.platform.value, "status": "published"})
                continue
            if job.approval_status == "rejected" or job.status == "cancelled":
                job_results.append({"id": job.id, "platform": job.platform.value, "status": job.status})
                continue

            plat = job.platform.value if hasattr(job.platform, "value") else str(job.platform)
            job.status = "processing"
            db.commit()
            time.sleep(0.2)

            if plat == "originals" and user:
                try:
                    StudioPlatformService.publish_to_originals(db, user, project.id)
                    result_ok = True
                    err = None
                    external_id = None
                except Exception as exc:
                    result_ok = False
                    err = str(exc)
                    external_id = None
            else:
                pub_result = _PUBLISHER.publish(
                    plat,
                    project_title=project.title,
                    seo_title=job.seo_title,
                    retry_count=job.retry_count,
                )
                result_ok = pub_result.success
                err = pub_result.error
                external_id = pub_result.external_id

            if result_ok:
                job.status = "published"
                job.published_at = datetime.now(timezone.utc)
                job.error_message = None
                success_count += 1
                PublishingAgentService._track_event(
                    db,
                    project_id=run.project_id,
                    platform=plat,
                    event_type="publish.success",
                    agent_run_id=run.id,
                    publish_job_id=job.id,
                    payload={"external_id": external_id},
                )
                deliver_webhooks(
                    db,
                    "publish.success",
                    {"run_id": run.id, "job_id": job.id, "platform": plat, "project_id": run.project_id},
                    project_id=run.project_id,
                )
            else:
                job.status = "failed"
                job.error_message = err
                fail_count += 1
                PublishingAgentService._track_event(
                    db,
                    project_id=run.project_id,
                    platform=plat,
                    event_type="publish.failed",
                    agent_run_id=run.id,
                    publish_job_id=job.id,
                    payload={"error": err},
                )
                deliver_webhooks(
                    db,
                    "publish.failed",
                    {"run_id": run.id, "job_id": job.id, "platform": plat, "error": err},
                    project_id=run.project_id,
                )

            job_results.append({
                "id": job.id,
                "platform": plat,
                "status": job.status,
                "error": job.error_message,
            })
            run.progress = int(((i + 1) / total) * 100)
            meta = dict(run.output_meta or {})
            meta["jobs"] = job_results
            run.output_meta = meta
            db.commit()

        if fail_count == 0:
            run.status = "completed"
        elif success_count == 0:
            run.status = "failed"
            run.error_message = "All platform publishes failed"
        else:
            run.status = "partial"
            run.error_message = f"{fail_count} of {total} platforms failed"

        run.progress = 100
        run.completed_at = datetime.now(timezone.utc)
        meta = dict(run.output_meta or {})
        meta["jobs"] = job_results
        meta["summary"] = {"success": success_count, "failed": fail_count}
        run.output_meta = meta

        PublishingAgentService._notify(
            db,
            run.created_by_id,
            f"Publishing {run.status} — {success_count}/{total} platforms",
            project.title,
            {"run_id": run.id, "status": run.status},
        )
        db.commit()
        return {"run_id": run.id, "status": run.status, "jobs": job_results}

    @staticmethod
    def get_queue(db: Session, user: User, limit: int = 50) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.schedule")
        runs = (
            db.query(PublishAgentRun, Production)
            .join(Production, PublishAgentRun.project_id == Production.id)
            .filter(PublishAgentRun.status.in_(["queued", "running", "scheduled", "pending_approval"]))
            .order_by(PublishAgentRun.created_at.desc())
            .limit(limit)
            .all()
        )
        jobs = PublishingCmsService.list_queue(db, user, limit=limit)
        return {
            "runs": [PublishingAgentService._run_dict(r, p) for r, p in runs],
            "jobs": jobs,
        }

    @staticmethod
    def get_history(db: Session, user: User, limit: int = 50, offset: int = 0) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.schedule")
        q = (
            db.query(PublishAgentRun, Production)
            .join(Production, PublishAgentRun.project_id == Production.id)
            .order_by(PublishAgentRun.created_at.desc())
        )
        total = q.count()
        rows = q.offset(offset).limit(limit).all()
        return {
            "items": [PublishingAgentService._run_dict(r, p) for r, p in rows],
            "total": total,
        }

    @staticmethod
    def approve_run(db: Session, user: User, run_id: int, notes: str | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.approve")
        run = db.query(PublishAgentRun).filter(PublishAgentRun.id == run_id).first()
        if not run:
            raise NotFoundError("Publish agent run")

        run.approval_status = "approved"
        run.status = "scheduled" if run.scheduled_at else "queued"

        approval = (
            db.query(StudioApproval)
            .filter(
                StudioApproval.entity_type == "publish_agent_run",
                StudioApproval.entity_id == run_id,
                StudioApproval.status == ApprovalStatus.PENDING,
            )
            .first()
        )
        if approval:
            approval.status = ApprovalStatus.APPROVED
            approval.approver_id = user.id
            approval.resolved_at = datetime.now(timezone.utc)
            if notes:
                approval.notes = notes

        jobs = db.query(PublishJob).filter(PublishJob.agent_run_id == run_id).all()
        for job in jobs:
            job.approval_status = "approved"
            job.approved_by_id = user.id
            job.approved_at = datetime.now(timezone.utc)
            job.status = "scheduled" if job.scheduled_at else "queued"

        deliver_webhooks(
            db,
            "publish.approved",
            {"run_id": run.id, "project_id": run.project_id},
            project_id=run.project_id,
        )

        if not run.scheduled_at or run.scheduled_at <= datetime.now(timezone.utc):
            from app.workers.publish_tasks import process_publish_agent_run

            task = process_publish_agent_run.delay(run.id)
            run.celery_task_id = task.id
            run.status = "running"
        db.commit()
        project = db.query(Production).filter(Production.id == run.project_id).first()
        return PublishingAgentService._run_dict(run, project)

    @staticmethod
    def reject_run(db: Session, user: User, run_id: int, notes: str | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.approve")
        run = db.query(PublishAgentRun).filter(PublishAgentRun.id == run_id).first()
        if not run:
            raise NotFoundError("Publish agent run")

        run.approval_status = "rejected"
        run.status = "cancelled"
        run.error_message = notes or "Rejected by approver"

        jobs = db.query(PublishJob).filter(PublishJob.agent_run_id == run_id).all()
        for job in jobs:
            job.approval_status = "rejected"
            job.status = "cancelled"
            job.error_message = notes

        deliver_webhooks(
            db,
            "publish.rejected",
            {"run_id": run.id, "notes": notes},
            project_id=run.project_id,
        )
        db.commit()
        project = db.query(Production).filter(Production.id == run.project_id).first()
        return PublishingAgentService._run_dict(run, project)

    @staticmethod
    def retry_run(db: Session, user: User, run_id: int, data: PublishingAgentRetryRequest | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.schedule")
        run = db.query(PublishAgentRun).filter(PublishAgentRun.id == run_id).first()
        if not run:
            raise NotFoundError("Publish agent run")

        job_ids = data.job_ids if data and data.job_ids else None
        q = db.query(PublishJob).filter(PublishJob.agent_run_id == run_id, PublishJob.status == "failed")
        if job_ids:
            q = q.filter(PublishJob.id.in_(job_ids))
        jobs = q.all()
        if not jobs:
            raise BadRequestError("No failed jobs to retry")

        for job in jobs:
            job.retry_count += 1
            job.status = "queued"
            job.error_message = None
            plat = job.platform.value if hasattr(job.platform, "value") else str(job.platform)
            PublishingAgentService._track_event(
                db,
                project_id=run.project_id,
                platform=plat,
                event_type="publish.retry",
                agent_run_id=run.id,
                publish_job_id=job.id,
            )
            deliver_webhooks(
                db,
                "publish.retry",
                {"run_id": run.id, "job_id": job.id, "platform": plat},
                project_id=run.project_id,
            )

        run.status = "running"
        run.error_message = None
        db.commit()

        from app.workers.publish_tasks import process_publish_agent_run

        task = process_publish_agent_run.delay(run.id)
        run.celery_task_id = task.id
        db.commit()

        project = db.query(Production).filter(Production.id == run.project_id).first()
        return PublishingAgentService._run_dict(run, project)

    @staticmethod
    def get_analytics(db: Session, user: User, days: int = 30) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = (
            db.query(PublishPlatformEvent.platform, PublishPlatformEvent.event_type, func.count(PublishPlatformEvent.id))
            .filter(PublishPlatformEvent.created_at >= since)
            .group_by(PublishPlatformEvent.platform, PublishPlatformEvent.event_type)
            .all()
        )
        by_platform: dict[str, dict[str, int]] = {}
        for plat, evt, count in rows:
            by_platform.setdefault(plat, {})[evt] = count

        recent = (
            db.query(PublishPlatformEvent)
            .order_by(PublishPlatformEvent.created_at.desc())
            .limit(20)
            .all()
        )
        return {
            "days": days,
            "by_platform": by_platform,
            "recent_events": [
                {
                    "id": e.id,
                    "platform": e.platform,
                    "event_type": e.event_type,
                    "project_id": e.project_id,
                    "created_at": e.created_at,
                }
                for e in recent
            ],
        }

    @staticmethod
    def list_webhooks(db: Session, user: User) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "publish.schedule")
        rows = db.query(PublishWebhook).order_by(PublishWebhook.created_at.desc()).all()
        return [
            {
                "id": w.id,
                "name": w.name,
                "url": w.url,
                "events": w.events or [],
                "is_active": w.is_active,
                "project_id": w.project_id,
                "last_triggered_at": w.last_triggered_at,
                "created_at": w.created_at,
            }
            for w in rows
        ]

    @staticmethod
    def create_webhook(db: Session, user: User, data: WebhookCreate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.schedule")
        events = [e for e in data.events if e in WEBHOOK_EVENTS or e == "*"]
        if not events:
            events = ["publish.success", "publish.failed"]
        row = PublishWebhook(
            name=data.name,
            url=data.url,
            events=events,
            secret=data.secret,
            is_active=data.is_active,
            project_id=data.project_id,
            created_by_id=user.id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return {
            "id": row.id,
            "name": row.name,
            "url": row.url,
            "events": row.events or [],
            "is_active": row.is_active,
            "project_id": row.project_id,
            "last_triggered_at": row.last_triggered_at,
            "created_at": row.created_at,
        }

    @staticmethod
    def update_webhook(db: Session, user: User, webhook_id: int, data: WebhookUpdate) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.schedule")
        row = db.query(PublishWebhook).filter(PublishWebhook.id == webhook_id).first()
        if not row:
            raise NotFoundError("Webhook")
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(row, key, value)
        db.commit()
        db.refresh(row)
        return {
            "id": row.id,
            "name": row.name,
            "url": row.url,
            "events": row.events or [],
            "is_active": row.is_active,
            "project_id": row.project_id,
            "last_triggered_at": row.last_triggered_at,
            "created_at": row.created_at,
        }

    @staticmethod
    def delete_webhook(db: Session, user: User, webhook_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.schedule")
        row = db.query(PublishWebhook).filter(PublishWebhook.id == webhook_id).first()
        if not row:
            raise NotFoundError("Webhook")
        db.delete(row)
        db.commit()
        return {"deleted": webhook_id}

    @staticmethod
    def process_due_scheduled(db: Session) -> dict:
        """Called by Celery beat — execute runs whose scheduled_at has passed."""
        now = datetime.now(timezone.utc)
        due_runs = (
            db.query(PublishAgentRun)
            .filter(
                PublishAgentRun.status == "scheduled",
                PublishAgentRun.scheduled_at <= now,
                PublishAgentRun.approval_status == "approved",
            )
            .limit(20)
            .all()
        )
        processed = []
        from app.workers.publish_tasks import process_publish_agent_run

        for run in due_runs:
            run.status = "running"
            db.commit()
            task = process_publish_agent_run.delay(run.id)
            run.celery_task_id = task.id
            processed.append(run.id)
        db.commit()
        return {"processed": processed, "count": len(processed)}
