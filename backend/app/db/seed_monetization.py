"""Seed subscription plans and magazine editions."""

import json

from sqlalchemy.orm import Session

from app.models.monetization import AccessTier, MagazineEdition, PlanCatalog
from app.models import SubscriptionPlan

PLANS = [
    {
        "slug": "free",
        "name": "Free",
        "tier": SubscriptionPlan.FREE,
        "description": "Get started with UNTOLD",
        "prices": {"INR": 0, "USD": 0, "EUR": 0, "GBP": 0, "RUB": 0, "AED": 0},
        "features": ["Limited catalog", "Ad-supported shorts", "Free magazine sample"],
        "sort_order": 0,
    },
    {
        "slug": "premium",
        "name": "Premium",
        "tier": SubscriptionPlan.PREMIUM,
        "description": "Full UNTOLD experience",
        "prices": {"INR": 149, "USD": 4.99, "EUR": 4.99, "GBP": 4.99, "RUB": 499, "AED": 19},
        "features": ["Full UNTOLD Originals", "HD streaming", "Continue watching", "E-Magazine access"],
        "sort_order": 1,
    },
    {
        "slug": "vip",
        "name": "VIP",
        "tier": SubscriptionPlan.VIP,
        "description": "The ultimate fan experience",
        "prices": {"INR": 499, "USD": 12.99, "EUR": 12.99, "GBP": 11.99, "RUB": 1499, "AED": 49},
        "features": ["Everything in Premium", "4K streaming", "Early access", "VIP magazine downloads"],
        "sort_order": 2,
    },
]

MAGAZINES = [
    ("issue-q1-2026", "UNTOLD Q1 2026", "Q1", 2026, AccessTier.FREE, None),
    ("issue-q2-2026", "UNTOLD Q2 2026", "Q2", 2026, AccessTier.PREMIUM, '{"INR": 99, "USD": 2.99}'),
    ("issue-exclusive-2026", "UNTOLD Exclusive Edition", "Special", 2026, AccessTier.VIP, None),
]


def seed_monetization_data(db: Session) -> None:
    if db.query(PlanCatalog).first():
        return

    for p in PLANS:
        db.add(
            PlanCatalog(
                slug=p["slug"],
                name=p["name"],
                tier=p["tier"],
                description=p["description"],
                prices_json=json.dumps(p["prices"]),
                features_json=json.dumps(p["features"]),
                sort_order=p["sort_order"],
            )
        )

    for slug, title, quarter, year, tier, prices in MAGAZINES:
        db.add(
            MagazineEdition(
                issue_slug=slug,
                title=title,
                quarter=quarter,
                year=year,
                access_tier=tier,
                prices_json=prices,
                pdf_storage_key=f"magazines/{slug}.pdf",
            )
        )

    db.commit()
