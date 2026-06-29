from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMBase


class AnalyticsEventCreate(BaseModel):
    event_type: str
    video_id: int | None = None
    metadata: dict | None = None


class AnalyticsEventResponse(ORMBase):
    id: int
    event_type: str
    user_id: int | None
    video_id: int | None
    metadata_json: str | None
    created_at: datetime


class AnalyticsSummary(BaseModel):
    total_users: int
    total_videos: int
    total_views: int
    total_watchlist_items: int
    active_subscriptions: int
    events_last_24h: int
    events_last_7d: int
    top_videos: list[dict]
    events_by_type: dict[str, int]


class DashboardStats(BaseModel):
    users: int
    videos: int
    categories: int
    watchlist_items: int
    subscriptions: int
    analytics_events: int
