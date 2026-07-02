"""AI Cost Optimization & Intelligence REST API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_studio_user
from app.db.session import get_db
from app.models import User
from app.schemas.ai_cost import (
    BudgetCreate,
    BudgetResponse,
    BudgetUpdate,
    CostAlertResponse,
    CostDashboardResponse,
    IntelligenceDashboardResponse,
    ModelPolicyResponse,
    ModelPolicyUpdate,
    MonthlyReportResponse,
    RoutingRequest,
    RoutingResponse,
)
from app.services.ai_cost_intelligence_service import AICostIntelligenceService
from app.services.ai_cost_service import AICostService

router = APIRouter(prefix="/studio/platform/ai-cost", tags=["AI Cost Intelligence"])


@router.get("/dashboard", response_model=CostDashboardResponse)
def cost_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    year: int | None = Query(None),
    month: int | None = Query(None, ge=1, le=12),
):
    return AICostService.dashboard(db, user, year=year, month=month)


@router.get("/intelligence", response_model=IntelligenceDashboardResponse)
def cost_intelligence_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    year: int | None = Query(None),
    month: int | None = Query(None, ge=1, le=12),
):
    return AICostIntelligenceService.intelligence_dashboard(db, user, year=year, month=month)


@router.post("/routing/resolve", response_model=RoutingResponse)
def resolve_routing(
    data: RoutingRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AICostIntelligenceService.resolve_routing(
        db, user, module=data.module, prompt=data.prompt, max_cost_per_request=data.max_cost_per_request,
    )


@router.get("/pricing")
def pricing_catalog(user: User = Depends(get_current_studio_user)):
    from app.domain.ai.cost_intelligence import provider_pricing_catalog

    return provider_pricing_catalog()


@router.get("/cache-stats")
def cache_stats(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AICostService.cache_stats(db, user)


@router.get("/budgets", response_model=list[BudgetResponse])
def list_budgets(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AICostService.list_budgets(db, user)


@router.post("/budgets", response_model=BudgetResponse, status_code=201)
def create_budget(data: BudgetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AICostService.create_budget(db, user, data)


@router.patch("/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AICostService.update_budget(db, user, budget_id, data)


@router.delete("/budgets/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    AICostService.delete_budget(db, user, budget_id)


@router.get("/policies", response_model=list[ModelPolicyResponse])
def list_model_policies(db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AICostService.list_policies(db, user)


@router.patch("/policies/{module}", response_model=ModelPolicyResponse)
def update_model_policy(
    module: str,
    data: ModelPolicyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
):
    return AICostService.update_policy(db, user, module, data)


@router.get("/alerts", response_model=list[CostAlertResponse])
def list_cost_alerts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    acknowledged: bool | None = Query(None),
):
    return AICostService.list_alerts(db, user, acknowledged=acknowledged)


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_studio_user)):
    return AICostService.acknowledge_alert(db, user, alert_id)


@router.get("/reports", response_model=list[MonthlyReportResponse])
def list_monthly_reports(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    limit: int = Query(12, ge=1, le=36),
):
    return AICostService.list_monthly_reports(db, user, limit=limit)


@router.post("/reports/generate", response_model=MonthlyReportResponse)
def generate_monthly_report(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_studio_user),
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    scope_type: str = Query("global"),
    scope_id: int | None = Query(None),
):
    return AICostService.generate_monthly_report(db, user, year=year, month=month, scope_type=scope_type, scope_id=scope_id)
