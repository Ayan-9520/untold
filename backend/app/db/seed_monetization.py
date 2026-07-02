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
    {
        "slug": "issue-q1-2026",
        "title": "UNTOLD Q1 2026",
        "quarter": "Q1",
        "year": 2026,
        "tier": AccessTier.FREE,
        "prices": None,
        "cover": "https://images.unsplash.com/photo-1531415074968-076ba3e9f2e4?w=1200&q=80",
    },
    {
        "slug": "issue-q2-2026",
        "title": "UNTOLD Q2 2026",
        "quarter": "Q2",
        "year": 2026,
        "tier": AccessTier.PREMIUM,
        "prices": {"INR": 99, "USD": 2.99},
        "cover": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1200&q=80",
    },
    {
        "slug": "issue-exclusive-2026",
        "title": "UNTOLD Exclusive Edition",
        "quarter": "Special",
        "year": 2026,
        "tier": AccessTier.VIP,
        "prices": None,
        "cover": "https://images.unsplash.com/photo-1461896836934-ffe607ba7a38?w=1200&q=80",
    },
]

DEFAULT_SECTIONS = [
    {"id": "cover", "title": "Editor's Letter", "body": "Welcome to UNTOLD — the story behind the glory.", "excerpt": "Editor's letter"},
    {"id": "feature", "title": "Cover Story", "body": "In-depth storytelling on the season's defining moments.", "excerpt": "Cover feature"},
    {"id": "analytics", "title": "Analytics Desk", "body": "Performance data, trends, and fan intelligence.", "excerpt": "Analytics"},
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

    for m in MAGAZINES:
        db.add(
            MagazineEdition(
                issue_slug=m["slug"],
                title=m["title"],
                quarter=m["quarter"],
                year=m["year"],
                access_tier=m["tier"],
                prices_json=json.dumps(m["prices"]) if m["prices"] else None,
                pdf_storage_key=f"magazines/{m['slug']}.pdf",
                cover_image_url=m["cover"],
                content_json=json.dumps(DEFAULT_SECTIONS),
                page_count=48,
            )
        )

    db.commit()
