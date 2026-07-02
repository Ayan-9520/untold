"""UNTOLD E-Magazine — Magazine Editor AI Agent."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.monetization import AccessTier, MagazineEdition, MagazineJob

logger = logging.getLogger("untold")

WORKFLOW_STEPS = [
    {"id": "collecting", "label": "Collecting Data", "agent": "Data Collection Agent"},
    {"id": "writing", "label": "Writing", "agent": "Editorial AI Agent"},
    {"id": "designing", "label": "Designing", "agent": "Design AI Agent"},
    {"id": "publishing", "label": "Publishing", "agent": "Publishing Agent"},
    {"id": "ready", "label": "Ready", "agent": "Editor-in-Chief Approval"},
]

PROGRESS_MAP = {"collecting": 25, "writing": 50, "designing": 75, "publishing": 90, "ready": 100}
STATUS_ORDER = ["collecting", "writing", "designing", "publishing", "ready"]


DEFAULT_COVER = "https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=1200&q=80"

MAGAZINE_SECTIONS_TEMPLATE = [
    {"id": "cover", "title": "Editor's Letter", "body": "Welcome to this edition of UNTOLD — stories behind the glory.", "excerpt": "Editor's letter"},
    {"id": "feature", "title": "Cover Story", "body": "Deep-dive feature on the athletes and moments defining the season.", "excerpt": "Cover feature"},
    {"id": "analytics", "title": "Analytics Desk", "body": "Data-driven insights across performance, form, and fan sentiment.", "excerpt": "Analytics"},
]


class MagazineAgentService:
    @staticmethod
    def _issue_dict(edition: MagazineEdition) -> dict:
        access = edition.access_tier.value if hasattr(edition.access_tier, "value") else str(edition.access_tier)
        prices = json.loads(edition.prices_json) if edition.prices_json else {}
        sections = json.loads(edition.content_json) if edition.content_json else MAGAZINE_SECTIONS_TEMPLATE
        theme = edition.title.split(" — ")[0] if " — " in edition.title else edition.title
        cover = edition.cover_image_url or DEFAULT_COVER
        page_count = edition.page_count or 48
        return {
            "id": edition.issue_slug,
            "title": edition.title,
            "quarter": edition.quarter,
            "year": edition.year,
            "theme": theme,
            "access": access,
            "sample": access == "free",
            "pageCount": page_count,
            "page_count": page_count,
            "coverImage": cover,
            "cover_image_url": cover,
            "priceINR": prices.get("INR"),
            "sections": sections,
            "featured": access == "free",
        }

    @staticmethod
    def _default_steps() -> list[dict]:
        return [{**s, "status": "pending"} for s in WORKFLOW_STEPS]

    @staticmethod
    def _job_dict(job: MagazineJob) -> dict:
        steps = json.loads(job.steps_json) if job.steps_json else MagazineAgentService._default_steps()
        return {
            "id": job.external_id,
            "theme": job.theme,
            "quarter": job.quarter,
            "year": job.year,
            "status": job.status,
            "progress": job.progress,
            "steps": steps,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }

    @staticmethod
    def list_issues(db: Session) -> list[dict]:
        rows = (
            db.query(MagazineEdition)
            .filter(MagazineEdition.is_published.is_(True))
            .order_by(MagazineEdition.created_at.desc())
            .all()
        )
        return [MagazineAgentService._issue_dict(r) for r in rows]

    @staticmethod
    def get_issue(db: Session, issue_id: str) -> dict | None:
        edition = db.query(MagazineEdition).filter(MagazineEdition.issue_slug == issue_id).first()
        return MagazineAgentService._issue_dict(edition) if edition else None

    @staticmethod
    def list_jobs(db: Session) -> list[dict]:
        rows = db.query(MagazineJob).order_by(MagazineJob.created_at.desc()).all()
        return [MagazineAgentService._job_dict(r) for r in rows]

    @staticmethod
    def generate_issue(db: Session, theme: str, quarter: str, year: int) -> dict:
        external_id = f"job-{int(datetime.now(timezone.utc).timestamp())}"
        steps = MagazineAgentService._default_steps()
        steps[0]["status"] = "processing"
        job = MagazineJob(
            external_id=external_id,
            theme=theme,
            quarter=quarter,
            year=year,
            status="collecting",
            progress=10,
            steps_json=json.dumps(steps),
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info("Magazine AI job started: %s %s %s — %s", quarter, year, theme, external_id)
        return MagazineAgentService._job_dict(job)

    @staticmethod
    def advance_job(db: Session, job_id: str) -> dict | None:
        job = db.query(MagazineJob).filter(MagazineJob.external_id == job_id).first()
        if not job:
            return None
        idx = STATUS_ORDER.index(job.status) if job.status in STATUS_ORDER else 0
        if idx < len(STATUS_ORDER) - 1:
            job.status = STATUS_ORDER[idx + 1]
        job.progress = PROGRESS_MAP.get(job.status, job.progress)
        steps = json.loads(job.steps_json) if job.steps_json else MagazineAgentService._default_steps()
        for i, step in enumerate(steps):
            if i < idx + 1:
                step["status"] = "completed"
            elif i == idx + 1:
                step["status"] = "processing"
            else:
                step["status"] = "pending"
        job.steps_json = json.dumps(steps)
        db.commit()
        db.refresh(job)
        return MagazineAgentService._job_dict(job)

    @staticmethod
    def approve_and_publish(db: Session, job_id: str) -> dict | None:
        job = db.query(MagazineJob).filter(MagazineJob.external_id == job_id).first()
        if not job:
            return None
        job.status = "ready"
        job.progress = 100
        steps = json.loads(job.steps_json) if job.steps_json else MagazineAgentService._default_steps()
        for step in steps:
            step["status"] = "completed"
        job.steps_json = json.dumps(steps)

        issue_slug = f"uq-{job.year}-{job.quarter.lower()}"
        title = f"{job.theme} — {job.quarter} {job.year}"
        edition = db.query(MagazineEdition).filter(MagazineEdition.issue_slug == issue_slug).first()
        if not edition:
            edition = MagazineEdition(
                issue_slug=issue_slug,
                title=title,
                quarter=job.quarter,
                year=job.year,
                access_tier=AccessTier.PREMIUM,
                is_published=True,
            )
            db.add(edition)
        else:
            edition.title = title
            edition.is_published = True

        job.published_issue_slug = issue_slug
        db.commit()
        db.refresh(job)
        db.refresh(edition)

        issue = MagazineAgentService._issue_dict(edition)
        logger.info("Magazine published: %s", issue_slug)
        return {"job": MagazineAgentService._job_dict(job), "issue": issue}
