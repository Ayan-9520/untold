"""Business Intelligence REST API — executive dashboards, reports, export."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.core.tenant_deps import get_tenant_context
from app.db.session import get_db
from app.domain.tenancy.context import TenantContext
from app.models import User
from app.schemas.bi import BIReportCreate, BIScheduleCreate
from app.services.bi_report_service import BIReportService
from app.services.bi_service import BusinessIntelligenceService

router = APIRouter(prefix="/studio/platform/bi", tags=["Business Intelligence"])


@router.get("/catalog")
def bi_catalog():
    return BusinessIntelligenceService.metric_catalog()


@router.get("/executive")
def executive_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
    days: int = Query(30, ge=7, le=365),
):
    return BusinessIntelligenceService.executive_dashboard(db, user, ctx, days=days)


@router.get("/revenue")
def revenue_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
    days: int = Query(30, ge=7, le=365),
):
    return BusinessIntelligenceService.revenue_dashboard(db, user, ctx, days=days)


@router.get("/ai-costs")
def ai_costs_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
    days: int = Query(30, ge=7, le=365),
):
    return BusinessIntelligenceService.ai_costs_dashboard(db, user, ctx, days=days)


@router.get("/usage")
def usage_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
):
    return BusinessIntelligenceService.usage_dashboard(db, user, ctx)


@router.get("/performance")
def performance_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
    days: int = Query(30, ge=7, le=365),
):
    return BusinessIntelligenceService.performance_dashboard(db, user, ctx, days=days)


@router.get("/projects")
def projects_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
):
    return BusinessIntelligenceService.projects_dashboard(db, user, ctx)


@router.get("/teams")
def teams_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
):
    return BusinessIntelligenceService.teams_dashboard(db, user, ctx)


@router.get("/organizations")
def organizations_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
):
    return BusinessIntelligenceService.organizations_dashboard(db, user, ctx)


@router.get("/retention")
def retention_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
    days: int = Query(90, ge=30, le=365),
):
    return BusinessIntelligenceService.retention_dashboard(db, user, ctx, days=days)


@router.get("/growth")
def growth_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
    days: int = Query(180, ge=30, le=365),
):
    return BusinessIntelligenceService.growth_dashboard(db, user, ctx, days=days)


@router.get("/reports")
def list_reports(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
):
    return BIReportService.list_reports(db, user, ctx)


@router.post("/reports", status_code=201)
def create_report(
    data: BIReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
):
    return BIReportService.create_report(db, user, ctx, data=data.model_dump())


@router.get("/reports/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
):
    return BIReportService.get_report(db, user, report_id, ctx)


@router.delete("/reports/{report_id}", status_code=204)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
):
    BIReportService.delete_report(db, user, report_id, ctx)


@router.post("/reports/{report_id}/run")
def run_report(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
    days: int = Query(30, ge=7, le=365),
):
    return BIReportService.run_report(db, user, ctx, report_id, days=days)


@router.get("/reports/{report_id}/export")
def export_report(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
    format: str = Query("csv", pattern="^(csv|json)$"),
    days: int = Query(30, ge=7, le=365),
):
    content, mime, filename = BIReportService.export_report(db, user, ctx, report_id, fmt=format, days=days)
    return Response(content=content, media_type=mime, headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/scheduled-reports")
def list_scheduled_reports(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
):
    return BIReportService.list_schedules(db, user, ctx)


@router.post("/scheduled-reports", status_code=201)
def create_scheduled_report(
    data: BIScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
):
    return BIReportService.create_schedule(db, user, ctx, data=data.model_dump())


@router.delete("/scheduled-reports/{schedule_id}", status_code=204)
def delete_scheduled_report(
    schedule_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    ctx: TenantContext = Depends(get_tenant_context),
):
    BIReportService.delete_schedule(db, user, schedule_id, ctx)
