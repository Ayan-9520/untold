"""Workflow run event logs — JSONB buffer + durable table."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.studio_platform import ProductionPipelineRun, WorkflowRunLog

_MAX_LOGS = 500


def append_log(
    db: Session,
    run_id: int,
    message: str,
    *,
    level: str = "info",
    stage: str | None = None,
    node_id: str | None = None,
    meta: dict | None = None,
) -> None:
    run = db.query(ProductionPipelineRun).filter(ProductionPipelineRun.id == run_id).first()
    if not run:
        return
    ts = datetime.now(timezone.utc)
    entry = {
        "ts": ts.isoformat(),
        "level": level,
        "message": message,
        "stage": stage,
        "node_id": node_id,
    }
    buffer = dict(run.output_meta or {})
    logs = list(buffer.get("logs") or [])
    logs.append(entry)
    buffer["logs"] = logs[-_MAX_LOGS:]
    run.output_meta = buffer

    db.add(
        WorkflowRunLog(
            run_id=run_id,
            node_id=node_id,
            level=level,
            stage=stage,
            message=message,
            meta=meta or {},
            created_at=ts,
        )
    )
    db.flush()


def get_logs(run: ProductionPipelineRun) -> list[dict]:
    return list((run.output_meta or {}).get("logs") or [])


def query_execution_logs(
    db: Session,
    run_id: int,
    *,
    level: str | None = None,
    node_id: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> tuple[list[dict], int]:
    q = db.query(WorkflowRunLog).filter(WorkflowRunLog.run_id == run_id)
    if level:
        q = q.filter(WorkflowRunLog.level == level)
    if node_id:
        q = q.filter(WorkflowRunLog.node_id == node_id)
    total = q.count()
    rows = q.order_by(WorkflowRunLog.created_at.asc()).offset(offset).limit(limit).all()
    items = [
        {
            "id": r.id,
            "run_id": r.run_id,
            "node_id": r.node_id,
            "level": r.level,
            "stage": r.stage,
            "message": r.message,
            "meta": r.meta or {},
            "created_at": r.created_at,
        }
        for r in rows
    ]
    return items, total
