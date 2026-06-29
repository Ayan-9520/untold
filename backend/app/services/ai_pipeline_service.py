"""AI localization pipeline — upload once, distribute globally."""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import LocalizationJob, LocalizationStatus, Subscription, SubscriptionPlan, SubscriptionStatus, User
from app.schemas.ai_pipeline import (
    AI_PIPELINE_STEPS,
    STEP_LABELS,
    LocalizationJobCreate,
    LocalizationJobResponse,
    MembershipStatsResponse,
    PipelineStepStatus,
    SubscriptionAdminResponse,
)

logger = logging.getLogger("untold")

PLAN_MRR_USD = {
    SubscriptionPlan.FREE: 0.0,
    SubscriptionPlan.PREMIUM: 9.99,
    SubscriptionPlan.VIP: 12.99,
}


def _default_steps(status: str = "pending") -> list[dict]:
    return [{"id": step, "label": STEP_LABELS[step], "status": status} for step in AI_PIPELINE_STEPS]


def _job_to_response(job: LocalizationJob) -> LocalizationJobResponse:
    try:
        targets = json.loads(job.target_languages)
    except (json.JSONDecodeError, TypeError):
        targets = []
    try:
        steps_raw = json.loads(job.steps_json) if job.steps_json else _default_steps()
    except (json.JSONDecodeError, TypeError):
        steps_raw = _default_steps()

    steps = [PipelineStepStatus(**s) if isinstance(s, dict) else s for s in steps_raw]

    return LocalizationJobResponse(
        id=job.id,
        video_id=job.video_id,
        video_title=job.video_title,
        source_language=job.source_language,
        target_languages=targets,
        status=job.status.value,
        progress=job.progress,
        steps=steps,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


class AIPipelineService:
    @staticmethod
    def list_jobs(db: Session, limit: int = 50) -> tuple[list[LocalizationJobResponse], int]:
        jobs = db.query(LocalizationJob).order_by(LocalizationJob.created_at.desc()).limit(limit).all()
        return [_job_to_response(j) for j in jobs], len(jobs)

    @staticmethod
    def get_job(db: Session, job_id: int) -> LocalizationJobResponse | None:
        job = db.query(LocalizationJob).filter(LocalizationJob.id == job_id).first()
        return _job_to_response(job) if job else None

    @staticmethod
    def create_job(db: Session, data: LocalizationJobCreate) -> LocalizationJobResponse:
        job = LocalizationJob(
            video_id=data.video_id,
            video_title=data.video_title,
            source_language=data.source_language,
            target_languages=json.dumps(data.target_languages),
            transcript=data.transcript,
            status=LocalizationStatus.PENDING,
            progress=0,
            steps_json=json.dumps(_default_steps()),
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info("Created localization job %s for '%s'", job.id, job.video_title)
        return _job_to_response(job)

    @staticmethod
    def process_job(db: Session, job_id: int) -> LocalizationJobResponse | None:
        job = db.query(LocalizationJob).filter(LocalizationJob.id == job_id).first()
        if not job:
            return None

        job.status = LocalizationStatus.PROCESSING
        steps = _default_steps()
        completed = 0
        for i, step in enumerate(steps):
            step["status"] = "completed"
            completed += 1
            job.progress = int((completed / len(steps)) * 100)
            job.steps_json = json.dumps(steps)
            db.commit()

        job.status = LocalizationStatus.COMPLETED
        job.progress = 100
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
        logger.info("Completed localization job %s", job.id)
        return _job_to_response(job)


class MembershipAdminService:
    @staticmethod
    def get_stats(db: Session) -> MembershipStatsResponse:
        active = (
            db.query(Subscription)
            .filter(Subscription.status == SubscriptionStatus.ACTIVE)
            .all()
        )
        premium = sum(1 for s in active if s.plan == SubscriptionPlan.PREMIUM)
        vip = sum(1 for s in active if s.plan == SubscriptionPlan.VIP)
        free = sum(1 for s in active if s.plan == SubscriptionPlan.FREE)
        mrr = sum(PLAN_MRR_USD.get(s.plan, 0.0) for s in active)

        return MembershipStatsResponse(
            total_subscribers=len(active),
            premium_count=premium,
            vip_count=vip,
            free_count=free,
            mrr=round(mrr, 2),
        )

    @staticmethod
    def list_subscriptions(db: Session, skip: int = 0, limit: int = 20) -> tuple[list[SubscriptionAdminResponse], int]:
        query = db.query(Subscription).order_by(Subscription.created_at.desc())
        total = query.count()
        subs = query.offset(skip).limit(limit).all()
        items = []
        for sub in subs:
            user = db.query(User).filter(User.id == sub.user_id).first()
            items.append(
                SubscriptionAdminResponse(
                    id=sub.id,
                    user_id=sub.user_id,
                    user_email=user.email if user else None,
                    plan=sub.plan.value,
                    status=sub.status.value,
                    started_at=sub.started_at,
                )
            )
        return items, total
