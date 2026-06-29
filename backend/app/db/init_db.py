"""Database initialization and seed data."""

import logging
import random

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.seed_data import MOCK_USERS, CATEGORIES, build_videos
from app.db.session import SessionLocal
from app.models import (
    AdminUser,
    Analytics,
    AnalyticsEventType,
    Category,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    User,
    UserRole,
    Video,
    VideoType,
    Watchlist,
)

logger = logging.getLogger("untold")
settings = get_settings()


def seed_database() -> None:
    """Insert seed data when SEED_DATABASE=true and the database is empty."""
    if not settings.seed_database:
        logger.info("Database seeding disabled (SEED_DATABASE=false)")
        return

    if not settings.admin_password:
        raise RuntimeError("ADMIN_PASSWORD is required when SEED_DATABASE=true")

    db = SessionLocal()
    try:
        _seed_data(db)
        from app.db.seed_news import seed_news_data

        seed_news_data(db)
        from app.db.seed_live import seed_live_data

        seed_live_data(db)
        from app.db.seed_monetization import seed_monetization_data

        seed_monetization_data(db)
        logger.info("News, live & monetization seed data applied")
    finally:
        db.close()


def _seed_data(db: Session) -> None:
    if db.query(Category).first():
        logger.info("Database already seeded, skipping")
        return

    logger.info("Seeding UNTOLD database (users, videos, categories)...")

    category_map: dict[str, Category] = {}
    for name, slug, desc in CATEGORIES:
        cat = Category(name=name, slug=slug, description=desc)
        db.add(cat)
        category_map[slug] = cat
    db.flush()

    videos_data = build_videos()
    video_objects: list[Video] = []
    for v in videos_data:
        cat = category_map.get(v["category"])
        video = Video(
            title=v["title"],
            slug=v["slug"],
            description=v["description"],
            category_id=cat.id if cat else None,
            duration=v["duration"],
            duration_seconds=v["duration_seconds"],
            year=v["year"],
            rating=v["rating"],
            image_url=v["image_url"],
            hero_image_url=v.get("hero_image_url"),
            is_featured=v.get("is_featured", False),
            is_trending=v.get("is_trending", False),
            video_type=VideoType(v["video_type"]),
            views_count=v.get("views_count", 0),
        )
        db.add(video)
        video_objects.append(video)
    db.flush()

    admin = User(
        email=settings.admin_email.lower(),
        hashed_password=get_password_hash(settings.admin_password),
        full_name="UNTOLD Admin",
        is_admin=True,
        role=UserRole.ADMIN,
    )
    db.add(admin)
    db.flush()

    db.add(AdminUser(user_id=admin.id, department="Platform", permissions="all"))
    db.add(
        Subscription(
            user_id=admin.id,
            plan=SubscriptionPlan.VIP,
            status=SubscriptionStatus.ACTIVE,
        )
    )

    created_users = [admin]
    for name, email in MOCK_USERS:
        user = User(
            email=email.lower(),
            hashed_password=get_password_hash("Untold123!"),
            full_name=name,
            role=UserRole.USER,
        )
        db.add(user)
        created_users.append(user)
    db.flush()

    plans = [SubscriptionPlan.FREE, SubscriptionPlan.PREMIUM, SubscriptionPlan.VIP]
    for user in created_users[1:]:
        db.add(
            Subscription(
                user_id=user.id,
                plan=random.choice(plans),
                status=SubscriptionStatus.ACTIVE,
            )
        )
        for vid in random.sample(video_objects, k=min(3, len(video_objects))):
            db.add(Watchlist(user_id=user.id, video_id=vid.id))
        db.add(
            Analytics(
                event_type=random.choice(list(AnalyticsEventType)),
                user_id=user.id,
                video_id=random.choice(video_objects).id,
            )
        )

    db.commit()
    logger.info(
        "Seeded: %d categories, %d videos, %d users",
        len(category_map),
        len(video_objects),
        len(created_users),
    )
