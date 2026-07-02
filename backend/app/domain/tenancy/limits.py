"""Plan limits and usage enforcement."""

from __future__ import annotations

from app.domain.tenancy.enums import OrganizationPlan

# seats, projects, workspaces, storage_gb, ai_generations_month, api_requests_day
PLAN_LIMITS: dict[str, dict[str, int]] = {
    OrganizationPlan.FREE.value: {
        "seats": 3,
        "projects": 5,
        "workspaces": 1,
        "storage_gb": 5,
        "ai_generations_month": 100,
        "api_requests_day": 1_000,
    },
    OrganizationPlan.STARTER.value: {
        "seats": 10,
        "projects": 25,
        "workspaces": 3,
        "storage_gb": 50,
        "ai_generations_month": 1_000,
        "api_requests_day": 10_000,
    },
    OrganizationPlan.PRO.value: {
        "seats": 50,
        "projects": 200,
        "workspaces": 20,
        "storage_gb": 500,
        "ai_generations_month": 10_000,
        "api_requests_day": 100_000,
    },
    OrganizationPlan.ENTERPRISE.value: {
        "seats": 10_000,
        "projects": 100_000,
        "workspaces": 1_000,
        "storage_gb": 10_000,
        "ai_generations_month": 1_000_000,
        "api_requests_day": 10_000_000,
    },
}


def get_plan_limits(plan: str) -> dict[str, int]:
    return dict(PLAN_LIMITS.get(plan, PLAN_LIMITS[OrganizationPlan.FREE.value]))


def merge_usage_limits(plan: str, overrides: dict | None) -> dict[str, int]:
    base = get_plan_limits(plan)
    if overrides:
        base.update({k: int(v) for k, v in overrides.items() if k in base})
    return base
