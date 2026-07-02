"""Celery tasks — compliance retention and privacy SLA checks."""

from app.db.session import SessionLocal
from app.domain.compliance.retention import run_retention_purge
from app.services.compliance_service import ComplianceService
from app.workers.celery_app import celery_app


@celery_app.task(name="untold.compliance_retention_purge")
def compliance_retention_purge() -> dict:
    db = SessionLocal()
    try:
        ComplianceService.ensure_default_policies(db)
        return run_retention_purge(db)
    finally:
        db.close()
