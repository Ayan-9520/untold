"""BI custom reports, export, and scheduled delivery."""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.domain.bi.metrics import SYSTEM_REPORT_TEMPLATES
from app.domain.tenancy.context import TenantContext
from app.models import User
from app.models.studio.bi import BIReportDefinition, BIReportRun, BIScheduledReport
from app.services.bi_service import BusinessIntelligenceService


def _compute_next_cron(cron_expression: str, *, base: datetime | None = None) -> datetime:
    from croniter import croniter

    base = base or datetime.now(timezone.utc)
    nxt = croniter(cron_expression, base).get_next(datetime)
    if nxt.tzinfo is None:
        return nxt.replace(tzinfo=timezone.utc)
    return nxt


class BIReportService:
    @staticmethod
    def ensure_system_templates(db: Session) -> None:
        for tpl in SYSTEM_REPORT_TEMPLATES:
            exists = (
                db.query(BIReportDefinition)
                .filter(BIReportDefinition.is_system.is_(True), BIReportDefinition.name == tpl["name"])
                .first()
            )
            if exists:
                continue
            db.add(
                BIReportDefinition(
                    name=tpl["name"],
                    description=f"System template: {tpl['name']}",
                    report_type=tpl["report_type"],
                    metrics=tpl["metrics"],
                    chart_type=tpl["chart_type"],
                    is_system=True,
                )
            )
        db.commit()

    @staticmethod
    def list_reports(db: Session, user: User, ctx: TenantContext) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        BIReportService.ensure_system_templates(db)
        q = db.query(BIReportDefinition)
        if ctx.organization_id:
            q = q.filter(
                (BIReportDefinition.organization_id == ctx.organization_id) | (BIReportDefinition.is_system.is_(True))
            )
        rows = q.order_by(BIReportDefinition.is_system.desc(), BIReportDefinition.name).all()
        return [BIReportService._report_dict(r) for r in rows]

    @staticmethod
    def create_report(db: Session, user: User, ctx: TenantContext, *, data: dict) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        row = BIReportDefinition(
            organization_id=ctx.organization_id,
            created_by_id=user.id,
            name=data["name"].strip(),
            description=data.get("description"),
            report_type=data.get("report_type", "custom"),
            metrics=data.get("metrics") or [],
            filters=data.get("filters") or {},
            dimensions=data.get("dimensions") or [],
            chart_type=data.get("chart_type", "bar"),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return BIReportService._report_dict(row)

    @staticmethod
    def get_report(db: Session, user: User, report_id: int, ctx: TenantContext) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        row = BIReportService._get_report(db, report_id, ctx)
        return BIReportService._report_dict(row)

    @staticmethod
    def delete_report(db: Session, user: User, report_id: int, ctx: TenantContext) -> None:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        row = BIReportService._get_report(db, report_id, ctx)
        if row.is_system:
            raise BadRequestError("Cannot delete system report templates")
        db.delete(row)
        db.commit()

    @staticmethod
    def run_report(db: Session, user: User, ctx: TenantContext, report_id: int, *, days: int = 30) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        report = BIReportService._get_report(db, report_id, ctx)
        run = BIReportRun(report_id=report.id, status="running", started_at=datetime.now(timezone.utc))
        db.add(run)
        db.flush()
        try:
            result = BIReportService._execute_report(db, user, ctx, report, days=days)
            run.status = "completed"
            run.result = result
            run.row_count = len(result.get("rows", []))
            run.completed_at = datetime.now(timezone.utc)
        except Exception as exc:
            run.status = "failed"
            run.error_message = str(exc)[:500]
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
            raise
        db.commit()
        db.refresh(run)
        return {"run_id": run.id, "status": run.status, "result": run.result, "row_count": run.row_count}

    @staticmethod
    def _execute_report(db: Session, user: User, ctx: TenantContext, report: BIReportDefinition, *, days: int) -> dict:
        dispatch = {
            "executive": BusinessIntelligenceService.executive_dashboard,
            "revenue": BusinessIntelligenceService.revenue_dashboard,
            "ai_cost": BusinessIntelligenceService.ai_costs_dashboard,
            "usage": lambda db, user, ctx, **kw: BusinessIntelligenceService.usage_dashboard(db, user, ctx),
            "performance": BusinessIntelligenceService.performance_dashboard,
            "projects": lambda db, user, ctx, **kw: BusinessIntelligenceService.projects_dashboard(db, user, ctx),
            "teams": lambda db, user, ctx, **kw: BusinessIntelligenceService.teams_dashboard(db, user, ctx),
            "organizations": lambda db, user, ctx, **kw: BusinessIntelligenceService.organizations_dashboard(db, user, ctx),
            "retention": BusinessIntelligenceService.retention_dashboard,
            "growth": BusinessIntelligenceService.growth_dashboard,
            "custom": BusinessIntelligenceService.executive_dashboard,
        }
        fn = dispatch.get(report.report_type, BusinessIntelligenceService.executive_dashboard)
        if report.report_type in ("usage", "projects", "teams", "organizations"):
            payload = fn(db, user, ctx)
        else:
            payload = fn(db, user, ctx, days=days)

        rows = []
        for metric in report.metrics or []:
            if "." in metric:
                ns, key = metric.split(".", 1)
                rows.append({"metric": metric, "namespace": ns, "key": key, "value": payload.get("kpis", {}).get(key.replace("_cents", "_usd").replace("total_cost_usd", "total_cost_usd"), None)})
        return {"report_type": report.report_type, "kpis": payload.get("kpis", {}), "rows": rows, "chart_type": report.chart_type}

    @staticmethod
    def export_report(db: Session, user: User, ctx: TenantContext, report_id: int, *, fmt: str = "json", days: int = 30) -> tuple[str, str, str]:
        result = BIReportService.run_report(db, user, ctx, report_id, days=days)["result"]
        if fmt == "csv":
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=["metric", "namespace", "key", "value"])
            writer.writeheader()
            for row in result.get("rows", []):
                writer.writerow(row)
            content = buf.getvalue()
            return content, "text/csv", f"report-{report_id}.csv"
        content = json.dumps(result, indent=2, default=str)
        return content, "application/json", f"report-{report_id}.json"

    @staticmethod
    def list_schedules(db: Session, user: User, ctx: TenantContext) -> list[dict]:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        q = db.query(BIScheduledReport)
        if ctx.organization_id:
            q = q.filter(BIScheduledReport.organization_id == ctx.organization_id)
        return [BIReportService._schedule_dict(s) for s in q.order_by(BIScheduledReport.created_at.desc()).all()]

    @staticmethod
    def create_schedule(db: Session, user: User, ctx: TenantContext, *, data: dict) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        BIReportService._get_report(db, data["report_id"], ctx)
        try:
            next_run = _compute_next_cron(data["cron_expression"])
        except Exception as exc:
            raise BadRequestError(f"Invalid cron: {exc}") from exc
        row = BIScheduledReport(
            report_id=data["report_id"],
            organization_id=ctx.organization_id,
            name=data["name"].strip(),
            cron_expression=data["cron_expression"],
            export_format=data.get("export_format", "csv"),
            recipients=data.get("recipients") or [],
            next_run_at=next_run,
            created_by_id=user.id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return BIReportService._schedule_dict(row)

    @staticmethod
    def delete_schedule(db: Session, user: User, schedule_id: int, ctx: TenantContext) -> None:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        row = db.query(BIScheduledReport).filter(BIScheduledReport.id == schedule_id).first()
        if not row:
            raise NotFoundError("Schedule")
        if ctx.organization_id and row.organization_id != ctx.organization_id:
            raise NotFoundError("Schedule")
        db.delete(row)
        db.commit()

    @staticmethod
    def process_due_schedules(db: Session) -> int:
        now = datetime.now(timezone.utc)
        schedules = (
            db.query(BIScheduledReport)
            .filter(
                BIScheduledReport.enabled.is_(True),
                BIScheduledReport.next_run_at.isnot(None),
                BIScheduledReport.next_run_at <= now,
            )
            .all()
        )
        fired = 0
        for sched in schedules:
            report = db.query(BIReportDefinition).filter(BIReportDefinition.id == sched.report_id).first()
            if not report:
                continue
            from app.models import User

            user = db.query(User).filter(User.id == sched.created_by_id).first() if sched.created_by_id else None
            if not user:
                user = db.query(User).filter(User.is_admin.is_(True)).first()
            if not user:
                continue
            from app.domain.tenancy.context import TenantContextService

            org_id = sched.organization_id or TenantContextService.resolve_primary_org_id(db, user.id)
            if not org_id:
                continue
            ctx = TenantContextService.build_context(db, user, organization_id=org_id)
            try:
                content, mime, filename = BIReportService.export_report(
                    db, user, ctx, sched.report_id, fmt=sched.export_format
                )
                sched.last_run_at = now
                sched.next_run_at = _compute_next_cron(sched.cron_expression, base=now)
                fired += 1
            except Exception:
                sched.last_run_at = now
                sched.next_run_at = _compute_next_cron(sched.cron_expression, base=now)
        db.commit()
        return fired

    @staticmethod
    def _get_report(db: Session, report_id: int, ctx: TenantContext) -> BIReportDefinition:
        row = db.query(BIReportDefinition).filter(BIReportDefinition.id == report_id).first()
        if not row:
            raise NotFoundError("Report")
        if row.organization_id and ctx.organization_id and row.organization_id != ctx.organization_id and not row.is_system:
            raise NotFoundError("Report")
        return row

    @staticmethod
    def _report_dict(r: BIReportDefinition) -> dict:
        return {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "report_type": r.report_type,
            "metrics": r.metrics or [],
            "filters": r.filters or {},
            "dimensions": r.dimensions or [],
            "chart_type": r.chart_type,
            "is_system": r.is_system,
            "organization_id": r.organization_id,
            "created_at": r.created_at,
        }

    @staticmethod
    def _schedule_dict(s: BIScheduledReport) -> dict:
        return {
            "id": s.id,
            "report_id": s.report_id,
            "name": s.name,
            "enabled": s.enabled,
            "cron_expression": s.cron_expression,
            "export_format": s.export_format,
            "recipients": s.recipients or [],
            "next_run_at": s.next_run_at,
            "last_run_at": s.last_run_at,
            "created_at": s.created_at,
        }
