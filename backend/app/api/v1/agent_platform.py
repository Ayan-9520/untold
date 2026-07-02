"""Enterprise AI Agent Platform REST API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.agent_platform import (
    AgentMemoryUpsert,
    AgentMessageSend,
    AgentRegisterRequest,
    AgentRunRequest,
    AgentScheduleCreate,
)
from app.services.agent_analytics_service import AgentAnalyticsService
from app.services.agent_marketplace_service import AgentMarketplaceService
from app.services.agent_memory_service import AgentMemoryService
from app.services.agent_platform_service import AgentPlatformService
from app.services.agent_runtime_service import AgentRuntimeService
from app.services.agent_scheduler_service import AgentSchedulerService

router = APIRouter(prefix="/studio/platform/agent-platform", tags=["Agent Platform"])


@router.get("/registry")
def agent_registry(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AgentPlatformService.registry(db, user)


@router.get("/sdk")
def agent_sdk_docs():
    return AgentPlatformService.sdk_docs()


@router.post("/register", status_code=201)
def register_agent(data: AgentRegisterRequest, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AgentPlatformService.register_agent(
        db,
        user,
        slug=data.slug,
        name=data.name,
        description=data.description,
        category=data.category,
        config_schema=data.config_schema,
        available_permissions=data.available_permissions,
    )


@router.get("/monitoring")
def agent_monitoring(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AgentAnalyticsService.monitoring_overview(db, user)


@router.get("/logs")
def agent_execution_logs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    installation_id: int | None = Query(None),
    agent_slug: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return AgentAnalyticsService.execution_logs(
        db, user, installation_id=installation_id, agent_slug=agent_slug, status=status, limit=limit, offset=offset
    )


@router.get("/installations/{installation_id}/analytics")
def installation_analytics(
    installation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AgentAnalyticsService.installation_analytics(db, user, installation_id)


@router.post("/installations/{installation_id}/run")
def run_agent(
    installation_id: int,
    data: AgentRunRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    from app.services.agent_memory_service import AgentMemoryService

    slug = AgentMemoryService._slug_for_installation(db, installation_id, user.id)
    ctx = AgentRuntimeService.build_context(db, user.id, slug, project_id=data.project_id)
    timer = AgentRuntimeService.execution_timer()
    try:
        result = AgentRuntimeService.run_registered_agent(ctx, data.payload)
        log = AgentRuntimeService.log_execution(
            db,
            agent_slug=slug,
            installation_id=installation_id,
            user_id=user.id,
            organization_id=ctx.organization_id,
            project_id=data.project_id,
            status="success",
            duration_ms=timer.elapsed_ms(),
            message="Manual agent run",
            meta={"result": result},
        )
        db.commit()
        return {"status": "success", "result": result, "log_id": log.id}
    except Exception as exc:
        AgentRuntimeService.log_execution(
            db,
            agent_slug=slug,
            installation_id=installation_id,
            user_id=user.id,
            status="failed",
            duration_ms=timer.elapsed_ms(),
            message=str(exc)[:500],
        )
        db.commit()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/installations/{installation_id}/memory")
def list_agent_memory(
    installation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    project_id: int | None = Query(None),
    prefix: str | None = Query(None),
):
    return AgentMemoryService.list_memory(db, user, installation_id, project_id=project_id, prefix=prefix)


@router.put("/installations/{installation_id}/memory")
def upsert_agent_memory(
    installation_id: int,
    data: AgentMemoryUpsert,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AgentMemoryService.upsert_memory(
        db,
        user,
        installation_id,
        memory_key=data.memory_key,
        content=data.content,
        project_id=data.project_id,
        meta=data.meta,
        expires_at=data.expires_at,
    )


@router.delete("/installations/{installation_id}/memory/{memory_id}", status_code=204)
def delete_agent_memory(
    installation_id: int,
    memory_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    AgentMemoryService.delete_memory(db, user, installation_id, memory_id)


@router.get("/installations/{installation_id}/schedules")
def list_agent_schedules(
    installation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AgentSchedulerService.list_schedules(db, user, installation_id)


@router.post("/installations/{installation_id}/schedules", status_code=201)
def create_agent_schedule(
    installation_id: int,
    data: AgentScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AgentSchedulerService.create_schedule(
        db, user, installation_id, name=data.name, cron_expression=data.cron_expression, payload=data.payload
    )


@router.delete("/installations/{installation_id}/schedules/{schedule_id}", status_code=204)
def delete_agent_schedule(
    installation_id: int,
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    AgentSchedulerService.delete_schedule(db, user, installation_id, schedule_id)


@router.get("/installations/{installation_id}/messages")
def list_agent_messages(
    installation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    status: str | None = Query(None),
):
    AgentMarketplaceService._get_installation(db, installation_id, user.id)
    return AgentRuntimeService.list_messages(db, installation_id, status=status)


@router.post("/installations/{installation_id}/messages", status_code=201)
def send_agent_message(
    installation_id: int,
    data: AgentMessageSend,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    from app.services.agent_memory_service import AgentMemoryService

    slug = AgentMemoryService._slug_for_installation(db, installation_id, user.id)
    ctx = AgentRuntimeService.build_context(db, user.id, slug)
    msg = AgentRuntimeService.send_message(db, ctx, data.to_slug, data.payload, message_type=data.message_type)
    db.commit()
    return {"id": msg.id, "status": msg.status}


@router.post("/installations/{installation_id}/messages/{message_id}/read")
def mark_message_read(
    installation_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    AgentMarketplaceService._get_installation(db, installation_id, user.id)
    AgentRuntimeService.mark_message_read(db, message_id, installation_id)
    db.commit()
    return {"id": message_id, "status": "read"}
