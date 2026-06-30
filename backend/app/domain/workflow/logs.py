"""Workflow run event logs."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.studio_platform import ProductionPipelineRun

_MAX_LOGS = 500


def append_log(
    db: Session,
    run_id: int,
    message: str,
    *,
    level: str = "info",
    stage: str | None = None,
) -> None:
    run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run_id).first()
    if not run:
        return
    meta = dict(run.output_meta or {})
    logs = list(meta.get("logs") or [])
    logs.append(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "stage": stage,
        }
    )
    meta["logs"] = logs[-_MAX_LOGS:]
    run.output_meta = meta
    db.flush()


def get_logs(run: ProductionPipelineRun) -> list[dict]:
    return list((run.output_meta or {}).get("logs") or [])
