import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    Analytics,
    AnalyticsEventType,
    Category,
    Subscription,
    SubscriptionStatus,
    User,
    Video,
    Watchlist,
)
from app.schemas.analytics import AnalyticsEventCreate, AnalyticsSummary, DashboardStats


class AnalyticsService:
    @staticmethod
    def track_event(
        db: Session,
        data: AnalyticsEventCreate,
        user_id: int | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Analytics:
        try:
            event_type = AnalyticsEventType(data.event_type)
        except ValueError:
            event_type = AnalyticsEventType.VIEW

        event = Analytics(
            event_type=event_type,
            user_id=user_id,
            video_id=data.video_id,
            metadata_json=json.dumps(data.metadata) if data.metadata else None,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(event)

        if data.video_id and event_type in (AnalyticsEventType.VIEW, AnalyticsEventType.PLAY):
            video = db.query(Video).filter(Video.id == data.video_id).first()
            if video:
                video.views_count += 1

        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def get_summary(db: Session) -> AnalyticsSummary:
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(hours=24)
        week_ago = now - timedelta(days=7)

        total_users = db.query(func.count(User.id)).scalar() or 0
        total_videos = db.query(func.count(Video.id)).filter(Video.is_active.is_(True)).scalar() or 0
        total_views = db.query(func.coalesce(func.sum(Video.views_count), 0)).scalar() or 0
        total_watchlist = db.query(func.count(Watchlist.id)).scalar() or 0
        active_subs = (
            db.query(func.count(Subscription.id))
            .filter(Subscription.status == SubscriptionStatus.ACTIVE)
            .scalar()
            or 0
        )
        events_24h = (
            db.query(func.count(Analytics.id)).filter(Analytics.created_at >= day_ago).scalar() or 0
        )
        events_7d = (
            db.query(func.count(Analytics.id)).filter(Analytics.created_at >= week_ago).scalar() or 0
        )

        top_videos = (
            db.query(Video.id, Video.title, Video.views_count)
            .filter(Video.is_active.is_(True))
            .order_by(Video.views_count.desc())
            .limit(5)
            .all()
        )

        events_by_type_rows = (
            db.query(Analytics.event_type, func.count(Analytics.id))
            .group_by(Analytics.event_type)
            .all()
        )
        events_by_type = {row[0].value: row[1] for row in events_by_type_rows}

        return AnalyticsSummary(
            total_users=total_users,
            total_videos=total_videos,
            total_views=total_views,
            total_watchlist_items=total_watchlist,
            active_subscriptions=active_subs,
            events_last_24h=events_24h,
            events_last_7d=events_7d,
            top_videos=[
                {"id": v.id, "title": v.title, "views": v.views_count} for v in top_videos
            ],
            events_by_type=events_by_type,
        )

    @staticmethod
    def get_dashboard_stats(db: Session) -> DashboardStats:
        return DashboardStats(
            users=db.query(func.count(User.id)).scalar() or 0,
            videos=db.query(func.count(Video.id)).scalar() or 0,
            categories=db.query(func.count(Category.id)).scalar() or 0,
            watchlist_items=db.query(func.count(Watchlist.id)).scalar() or 0,
            subscriptions=db.query(func.count(Subscription.id)).scalar() or 0,
            analytics_events=db.query(func.count(Analytics.id)).scalar() or 0,
        )

    @staticmethod
    def list_recent_events(db: Session, limit: int = 50) -> list[Analytics]:
        return db.query(Analytics).order_by(Analytics.created_at.desc()).limit(limit).all()
