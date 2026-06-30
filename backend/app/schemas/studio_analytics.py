"""Studio Analytics schemas."""

from datetime import datetime

from pydantic import BaseModel


class MetricPoint(BaseModel):
    date: str
    views: int
    watch_time_hours: float
    revenue: float
    subscribers: int


class BreakdownItem(BaseModel):
    label: str
    value: float
    pct: float


class TopVideoItem(BaseModel):
    id: int
    title: str
    views: int
    watch_time_hours: float
    ctr: float


class TopCreatorItem(BaseModel):
    name: str
    projects: int
    total_views: int


class RealtimeMetrics(BaseModel):
    active_viewers: int
    views_last_hour: int
    plays_last_hour: int
    revenue_today: float
    updated_at: datetime


class StudioAnalyticsOverview(BaseModel):
    views: int
    watch_time_hours: float
    ctr: float
    revenue: float
    subscribers: int
    subscriber_growth_pct: float
    views_growth_pct: float
    traffic_sources: list[BreakdownItem]
    countries: list[BreakdownItem]
    devices: list[BreakdownItem]
    top_videos: list[TopVideoItem]
    top_creators: list[TopCreatorItem]
    growth: list[MetricPoint]
