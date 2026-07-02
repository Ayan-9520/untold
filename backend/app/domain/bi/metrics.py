"""BI metric catalog and report templates."""

from __future__ import annotations

BI_NAMESPACES = (
    "revenue",
    "ai_cost",
    "usage",
    "performance",
    "projects",
    "teams",
    "organizations",
    "retention",
    "growth",
)

BI_METRIC_CATALOG: dict[str, dict[str, str]] = {
    "revenue": {
        "mrr_cents": "Monthly recurring revenue (cents)",
        "arr_cents": "Annual recurring revenue (cents)",
        "invoice_total_cents": "Paid invoice total (cents)",
        "active_subscriptions": "Active org subscriptions",
    },
    "ai_cost": {
        "total_cost_usd": "Total AI spend (USD)",
        "generation_count": "AI generation count",
        "input_tokens": "Input tokens consumed",
        "output_tokens": "Output tokens consumed",
    },
    "usage": {
        "seats": "Seat usage",
        "ai_credits": "AI credits consumed",
        "storage_gb": "Storage used (GB)",
        "video_minutes": "Video minutes processed",
    },
    "performance": {
        "avg_latency_ms": "Average generation latency (ms)",
        "success_rate": "Generation success rate (%)",
        "cache_hit_rate": "AI cache hit rate (%)",
    },
    "projects": {
        "active_projects": "Active productions",
        "completed_projects": "Completed productions",
        "pipeline_runs": "Pipeline runs",
    },
    "teams": {
        "team_count": "Teams",
        "member_count": "Team members",
    },
    "organizations": {
        "org_count": "Organizations",
        "member_count": "Organization members",
    },
    "retention": {
        "active_orgs_30d": "Orgs active in last 30 days",
        "churned_subscriptions": "Cancelled subscriptions",
        "renewal_rate": "Subscription renewal rate (%)",
    },
    "growth": {
        "new_orgs": "New organizations",
        "new_members": "New members",
        "new_projects": "New projects",
        "mrr_growth_pct": "MRR growth (%)",
    },
}

SYSTEM_REPORT_TEMPLATES: list[dict] = [
    {
        "name": "Executive Summary",
        "report_type": "executive",
        "metrics": ["revenue.mrr_cents", "ai_cost.total_cost_usd", "projects.active_projects", "growth.mrr_growth_pct"],
        "chart_type": "kpi",
    },
    {
        "name": "Revenue & Billing",
        "report_type": "revenue",
        "metrics": ["revenue.mrr_cents", "revenue.invoice_total_cents", "revenue.active_subscriptions"],
        "chart_type": "line",
    },
    {
        "name": "AI Cost Breakdown",
        "report_type": "ai_cost",
        "metrics": ["ai_cost.total_cost_usd", "ai_cost.generation_count", "ai_cost.input_tokens"],
        "chart_type": "bar",
    },
    {
        "name": "Usage Meters",
        "report_type": "usage",
        "metrics": ["usage.seats", "usage.ai_credits", "usage.storage_gb", "usage.video_minutes"],
        "chart_type": "bar",
    },
]
