"""Publishing CMS — multi-platform queue, approvals, SEO, retries."""

from __future__ import annotations

import random
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.domain.studio.enums import ApprovalStatus, PublishPlatform, PublishingStatus
from app.models import User
from app.models.studio import Production
from app.models.studio_platform import PublishJob, StudioApproval
from app.schemas.publishing_cms import PublishingPackageUpdate, PublishingScheduleRequest
from app.services.studio_platform_service import StudioPlatformService

PLATFORM_LABELS = {
    "originals": "UNTOLD Originals",
    "youtube": "YouTube",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "x": "X",
    "threads": "Threads",
}


class PublishingCmsService:
    @staticmethod
    def _job_dict(job: PublishJob, project: Production | None = None) -> dict:
        plat = job.platform.value if hasattr(job.platform, "value") else str(job.platform)
        return {
            "id": job.id,
            "project_id": job.project_id,
            "project_title": project.title if project else None,
            "platform": plat,
            "scheduled_at": job.scheduled_at,
            "status": job.status,
            "approval_status": job.approval_status,
            "published_at": job.published_at,
            "requires_approval": job.requires_approval,
            "retry_count": job.retry_count,
            "error_message": job.error_message,
            "thumbnail_url": job.thumbnail_url,
            "seo_title": job.seo_title,
            "seo_description": job.seo_description,
            "seo_keywords": job.seo_keywords or [],
            "created_at": job.created_at,
        }

    @staticmethod
    def seed_demo_jobs(db: Session) -> None:
        if db.query(PublishJob).count() > 0:
            return
        projects = db.query(Production).limit(3).all()
        if not projects:
            return
        now = datetime.now(timezone.utc)
        demos = [
            ("originals", "pending_approval", "pending", True, None),
            ("youtube", "scheduled", "approved", True, now),
            ("instagram", "failed", "approved", False, None),
            ("facebook", "published", "approved", False, now),
            ("x", "queued", "approved", True, None),
        ]
        for i, (plat, status, approval, req_approval, sched) in enumerate(demos):
            proj = projects[i % len(projects)]
            job = PublishJob(
                project_id=proj.id,
                platform=PublishPlatform(plat),
                scheduled_at=sched,
                status=status,
                approval_status=approval,
                requires_approval=req_approval,
                created_by_id=1,
                seo_title=proj.seo_title or proj.title,
                seo_description=proj.seo_description or proj.description,
                seo_keywords=proj.seo_keywords or ["documentary", "untold"],
                thumbnail_url=proj.thumbnail_url or "https://images.unsplash.com/photo-1461896836934-ffe607cd7bc0?w=640",
                error_message="API rate limit exceeded" if status == "failed" else None,
                retry_count=2 if status == "failed" else 0,
                published_at=now if status == "published" else None,
            )
            db.add(job)
        db.commit()

    @staticmethod
    def get_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.schedule")
        PublishingCmsService.seed_demo_jobs(db)
        total = db.query(func.count(PublishJob.id)).scalar() or 0
        pending_approval = (
            db.query(func.count(PublishJob.id)).filter(PublishJob.approval_status == "pending").scalar() or 0
        )
        scheduled = db.query(func.count(PublishJob.id)).filter(PublishJob.status == "scheduled").scalar() or 0
        failed = db.query(func.count(PublishJob.id)).filter(PublishJob.status == "failed").scalar() or 0
        published = db.query(func.count(PublishJob.id)).filter(PublishJob.status == "published").scalar() or 0

        platform_rows = db.query(PublishJob.platform, func.count(PublishJob.id)).group_by(PublishJob.platform).all()
        platform_counts = {
            (p.value if hasattr(p, "value") else str(p)): c for p, c in platform_rows
        }
        vis_rows = db.query(Production.visibility, func.count(Production.id)).group_by(Production.visibility).all()
        visibility_counts = {v or "draft": c for v, c in vis_rows}

        return {
            "total_jobs": total,
            "pending_approval": pending_approval,
            "scheduled": scheduled,
            "failed": failed,
            "published": published,
            "platform_counts": platform_counts,
            "visibility_counts": visibility_counts,
        }

    @staticmethod
    def list_queue(
        db: Session,
        user: User,
        *,
        status: str | None = None,
        platform: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "publish.schedule")
        PublishingCmsService.seed_demo_jobs(db)
        q = db.query(PublishJob, Production).join(Production, PublishJob.project_id == Production.id)
        if status:
            q = q.filter(PublishJob.status == status)
        if platform:
            q = q.filter(PublishJob.platform == platform)
        rows = q.order_by(PublishJob.created_at.desc()).limit(limit).all()
        return [PublishingCmsService._job_dict(job, proj) for job, proj in rows]

    @staticmethod
    def get_workspace(db: Session, user: User, project_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "publish.schedule")
        project = db.query(Production).filter(Production.id == project_id).first()
        if not project:
            raise NotFoundError("Project")
        jobs = (
            db.query(PublishJob)
            .filter(PublishJob.project_id == project_id)
            .order_by(PublishJob.created_at.desc())
            .all()
        )
        pending = sum(1 for j in jobs if j.approval_status == "pending")
        return {
            "project_id": project_id,
            "project_title": project.title,
            "visibility": getattr(project, "visibility", None) or "draft",
            "publishing_status": project.publishing_status,
            "seo_title": project.seo_title,
            "seo_description": project.seo_description,
            "seo_keywords": project.seo_keywords or [],
            "thumbnail_url": project.thumbnail_url,
            "jobs": [PublishingCmsService._job_dict(j, project) for j in jobs],
            "pending_approvals": pending,
        }

    @staticmethod
    def update_package(db: Session, user: User, project_id: int, data: PublishingPackageUpdate) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "publish.schedule")
        project = db.query(Production).filter(Production.id == project_id).first()
        if not project:
            raise NotFoundError("Project")
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(project, key, value)
        if data.visibility == "published":
            project.publishing_status = PublishingStatus.PUBLISHED
        elif data.visibility == "archived":
            project.publishing_status = PublishingStatus.UNPUBLISHED
        db.commit()
        return PublishingCmsService.get_workspace(db, user, project_id)

    @staticmethod
    def schedule(db: Session, user: User, project_id: int, data: PublishingScheduleRequest) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "publish.schedule")
        project = db.query(Production).filter(Production.id == project_id).first()
        if not project:
            raise NotFoundError("Project")

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

        job = PublishJob(
            project_id=project_id,
            platform=data.platform,
            scheduled_at=data.scheduled_at,
            requires_approval=data.requires_approval,
            approval_status=approval_status,
            status=status,
            meta=data.meta,
            seo_title=data.seo_title or project.seo_title,
            seo_description=data.seo_description or project.seo_description,
            seo_keywords=data.seo_keywords or project.seo_keywords,
            thumbnail_url=data.thumbnail_url or project.thumbnail_url,
            created_by_id=user.id,
        )
        db.add(job)

        if data.requires_approval:
            db.add(
                StudioApproval(
                    project_id=project_id,
                    entity_type="publish_job",
                    entity_id=0,
                    requested_by_id=user.id,
                    status=ApprovalStatus.PENDING,
                    notes=f"Publish to {PLATFORM_LABELS.get(data.platform.value, data.platform)}",
                )
            )
            db.flush()
            approval = (
                db.query(StudioApproval)
                .filter(
                    StudioApproval.project_id == project_id,
                    StudioApproval.entity_type == "publish_job",
                    StudioApproval.status == ApprovalStatus.PENDING,
                )
                .order_by(StudioApproval.id.desc())
                .first()
            )
            if approval:
                approval.entity_id = job.id

        if not data.requires_approval and not data.scheduled_at:
            PublishingCmsService._execute_job(db, user, job, project)

        db.commit()
        db.refresh(job)
        return PublishingCmsService._job_dict(job, project)

    @staticmethod
    def _execute_job(db: Session, user: User, job: PublishJob, project: Production) -> None:
        plat = job.platform.value if hasattr(job.platform, "value") else str(job.platform)
        job.status = "processing"
        db.flush()
        # Demo: simulate platform publish
        fail_roll = random.random() < 0.08 and job.retry_count == 0
        if fail_roll and plat != "originals":
            job.status = "failed"
            job.error_message = f"{PLATFORM_LABELS.get(plat, plat)} API temporarily unavailable"
            return
        if plat == "originals":
            StudioPlatformService.publish_to_originals(db, user, project.id)
        job.status = "published"
        job.published_at = datetime.now(timezone.utc)
        job.error_message = None
        if project.visibility == "draft":
            project.visibility = "published"

    @staticmethod
    def approve_job(db: Session, user: User, job_id: int, notes: str | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.approve")
        job = db.query(PublishJob).filter(PublishJob.id == job_id).first()
        if not job:
            raise NotFoundError("Publish job")
        project = db.query(Production).filter(Production.id == job.project_id).first()
        job.approval_status = "approved"
        job.approved_by_id = user.id
        job.approved_at = datetime.now(timezone.utc)
        job.status = "scheduled" if job.scheduled_at else "queued"

        approval = (
            db.query(StudioApproval)
            .filter(
                StudioApproval.entity_type == "publish_job",
                StudioApproval.entity_id == job_id,
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

        if not job.scheduled_at or job.scheduled_at <= datetime.now(timezone.utc):
            PublishingCmsService._execute_job(db, user, job, project)

        db.commit()
        db.refresh(job)
        return PublishingCmsService._job_dict(job, project)

    @staticmethod
    def reject_job(db: Session, user: User, job_id: int, notes: str | None = None) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.approve")
        job = db.query(PublishJob).filter(PublishJob.id == job_id).first()
        if not job:
            raise NotFoundError("Publish job")
        job.approval_status = "rejected"
        job.status = "cancelled"
        job.error_message = notes or "Rejected by approver"
        project = db.query(Production).filter(Production.id == job.project_id).first()

        approval = (
            db.query(StudioApproval)
            .filter(
                StudioApproval.entity_type == "publish_job",
                StudioApproval.entity_id == job_id,
                StudioApproval.status == ApprovalStatus.PENDING,
            )
            .first()
        )
        if approval:
            approval.status = ApprovalStatus.REJECTED
            approval.approver_id = user.id
            approval.resolved_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(job)
        return PublishingCmsService._job_dict(job, project)

    @staticmethod
    def retry_job(db: Session, user: User, job_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, None, "publish.schedule")
        job = db.query(PublishJob).filter(PublishJob.id == job_id).first()
        if not job:
            raise NotFoundError("Publish job")
        if job.status != "failed":
            raise BadRequestError("Only failed jobs can be retried")
        project = db.query(Production).filter(Production.id == job.project_id).first()
        job.retry_count += 1
        job.error_message = None
        job.status = "queued"
        PublishingCmsService._execute_job(db, user, job, project)
        db.commit()
        db.refresh(job)
        return PublishingCmsService._job_dict(job, project)
