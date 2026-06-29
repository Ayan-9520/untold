from pydantic import BaseModel


class RevenueSummary(BaseModel):
    total_revenue: float
    mrr: float
    arr: float
    growth_rate: float
    active_subscriptions: int
    revenue_by_plan: dict[str, float]
    monthly_revenue: list[dict]
