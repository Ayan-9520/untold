"""Programmatic Workflow Engine controls."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import User
from app.schemas.production_pipeline import ProductionPipelineCreate
from app.services.production_pipeline_service import ProductionPipelineService


class WorkflowEngineClient:
    """SDK-style facade: run(), cancel(), retry(), approve(), reject(), history(), status(), logs()."""

    def __init__(self, db: Session, user: User) -> None:
        self._db = db
        self._user = user

    def run(self, run_id: int) -> dict:
        ProductionPipelineService.run(self._db, self._user, run_id)
        return ProductionPipelineService.get_run(self._db, self._user, run_id)

    def create_and_run(self, data: ProductionPipelineCreate) -> dict:
        run = ProductionPipelineService.create_run(self._db, self._user, data)
        return ProductionPipelineService.get_run(self._db, self._user, run.id)

    def cancel(self, run_id: int) -> dict:
        ProductionPipelineService.cancel_run(self._db, self._user, run_id)
        return ProductionPipelineService.get_run(self._db, self._user, run_id)

    def retry(self, run_id: int) -> dict:
        ProductionPipelineService.retry_run(self._db, self._user, run_id)
        return ProductionPipelineService.get_run(self._db, self._user, run_id)

    def approve(self, run_id: int, notes: str | None = None) -> dict:
        ProductionPipelineService.approve_run(self._db, self._user, run_id, notes)
        return ProductionPipelineService.get_run(self._db, self._user, run_id)

    def reject(self, run_id: int, notes: str | None = None) -> dict:
        ProductionPipelineService.reject_run(self._db, self._user, run_id, notes)
        return ProductionPipelineService.get_run(self._db, self._user, run_id)

    def history(self, *, limit: int = 50, offset: int = 0) -> dict:
        return ProductionPipelineService.history(self._db, self._user, limit=limit, offset=offset)

    def status(self, run_id: int) -> dict:
        return ProductionPipelineService.status(self._db, self._user, run_id)

    def logs(self, run_id: int) -> dict:
        return ProductionPipelineService.logs(self._db, self._user, run_id)
