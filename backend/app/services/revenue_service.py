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

        total_revenue = mrr * 12 * 1.5  # simulated lifetime multiplier
        arr = mrr * 12

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        monthly_revenue = []
        for i, month in enumerate(months[-6:]):
            factor = 0.7 + (i * 0.06)
            monthly_revenue.append({"month": month, "revenue": round(mrr * factor, 2)})

        return RevenueSummary(
            total_revenue=round(total_revenue, 2),
            mrr=round(mrr, 2),
            arr=round(arr, 2),
            growth_rate=12.4,
            active_subscriptions=len(active_subs),
            revenue_by_plan={k: round(v, 2) for k, v in revenue_by_plan.items()},
            monthly_revenue=monthly_revenue,
        )
