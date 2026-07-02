from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Subscription, SubscriptionPlan, SubscriptionStatus
from app.schemas.revenue import RevenueSummary

PLAN_PRICES = {
    SubscriptionPlan.FREE: 0.0,
    SubscriptionPlan.PREMIUM: 9.99,
    SubscriptionPlan.VIP: 12.99,
}


class RevenueService:
    @staticmethod
    def get_summary(db: Session) -> RevenueSummary:
        active_subs = (
            db.query(Subscription)
            .filter(Subscription.status == SubscriptionStatus.ACTIVE)
            .all()
        )

        revenue_by_plan: dict[str, float] = {}
        mrr = 0.0
        for sub in active_subs:
            price = PLAN_PRICES.get(sub.plan, 0.0)
            plan_key = sub.plan.value
            revenue_by_plan[plan_key] = revenue_by_plan.get(plan_key, 0.0) + price
            mrr += price

        arr = mrr * 12
        total_revenue = arr

        monthly_rows = (
            db.query(
                func.date_trunc("month", Subscription.started_at),
                func.count(Subscription.id),
            )
            .filter(Subscription.status == SubscriptionStatus.ACTIVE)
            .group_by(func.date_trunc("month", Subscription.started_at))
            .order_by(func.date_trunc("month", Subscription.started_at).desc())
            .limit(6)
            .all()
        )
        monthly_revenue = []
        for month_start, count in reversed(monthly_rows):
            label = month_start.strftime("%b") if month_start else "—"
            monthly_revenue.append({"month": label, "revenue": round(mrr * (count / max(len(active_subs), 1)), 2)})

        if not monthly_revenue and mrr > 0:
            monthly_revenue = [{"month": "Current", "revenue": round(mrr, 2)}]

        growth_rate = 0.0
        if len(monthly_rows) >= 2:
            prev = monthly_rows[1][1] or 1
            curr = monthly_rows[0][1] or 0
            growth_rate = round(((curr - prev) / prev) * 100, 1)

        return RevenueSummary(
            total_revenue=round(total_revenue, 2),
            mrr=round(mrr, 2),
            arr=round(arr, 2),
            growth_rate=growth_rate,
            active_subscriptions=len(active_subs),
            revenue_by_plan={k: round(v, 2) for k, v in revenue_by_plan.items()},
            monthly_revenue=monthly_revenue,
        )
