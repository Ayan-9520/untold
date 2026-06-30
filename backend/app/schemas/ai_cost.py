"""AI Cost Optimization API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CostBreakdownItem(BaseModel):
    key: str
    label: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0
    request_count: int = 0


class CostDashboardResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    total_requests: int
    cache_hits: int
    cache_savings_usd: float
    by_project: list[CostBreakdownItem]
    by_user: list[CostBreakdownItem]
    by_model: list[CostBreakdownItem]
    by_provider: list[CostBreakdownItem]
    active_budgets: int
    unacknowledged_alerts: int


class BudgetCreate(BaseModel):
    scope_type: str = Field(pattern="^(global|user|project)$")
    scope_id: int | None = None
    name: str = Field(min_length=1, max_length=200)
    monthly_limit_usd: float = Field(gt=0, le=1_000_000)
    alert_threshold_pct: int = Field(default=80, ge=1, le=100)
    hard_limit: bool = False
    enabled: bool = True


class BudgetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    monthly_limit_usd: float | None = Field(default=None, gt=0)
    alert_threshold_pct: int | None = Field(default=None, ge=1, le=100)
    hard_limit: bool | None = None
    enabled: bool | None = None


class BudgetResponse(BaseModel):
    id: int
    scope_type: str
    scope_id: int | None
    name: str
    monthly_limit_usd: float
    alert_threshold_pct: int
    hard_limit: bool
    enabled: bool
    current_spend_usd: float = 0
    utilization_pct: float = 0
    created_at: datetime | None

    model_config = {"from_attributes": True}


class ModelPolicyUpdate(BaseModel):
    selection_mode: str | None = Field(default=None, pattern="^(auto|fixed|cheapest|quality)$")
    primary_model: str | None = None
    primary_provider: str | None = None
    fallback_chain: list[dict[str, str]] | None = None
    max_cost_per_request_usd: float | None = Field(default=None, ge=0)
    cache_enabled: bool | None = None
    cache_ttl_hours: int | None = Field(default=None, ge=1, le=720)
    enabled: bool | None = None


class ModelPolicyResponse(BaseModel):
    id: int
    module: str
    selection_mode: str
    primary_model: str | None
    primary_provider: str | None
    fallback_chain: list[dict[str, str]]
    max_cost_per_request_usd: float | None
    cache_enabled: bool
    cache_ttl_hours: int
    enabled: bool

    model_config = {"from_attributes": True}


class CostAlertResponse(BaseModel):
    id: int
    budget_id: int
    budget_name: str | None = None
    alert_type: str
    threshold_pct: int
    spend_usd: float
    limit_usd: float
    message: str
    acknowledged: bool
    created_at: datetime | None

    model_config = {"from_attributes": True}


class MonthlyReportResponse(BaseModel):
    id: int
    year: int
    month: int
    scope_type: str
    scope_id: int | None
    report_data: dict[str, Any]
    generated_at: datetime | None

    model_config = {"from_attributes": True}
