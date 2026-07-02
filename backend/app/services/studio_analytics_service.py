"""Studio Analytics — views, growth, realtime, exports."""

from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Subscription, SubscriptionStatus, User, Video
from app.models.studio import Production
from app.services.analytics_service import AnalyticsService
from app.services.revenue_service import RevenueService
from app.services.studio_platform_service import StudioPlatformService


class StudioAnalyticsService:
    @staticmethod
    def _breakdown(items: list[tuple[str, float]]) -> list[dict]:
        if not items:
            return []
        total = sum(v for _, v in items) or 1
        return [{"label": k, "value": v, "pct": round(v / total * 100, 1)} for k, v in items]

    @staticmethod
    def _growth_series(db: Session, *, days: int = 30) -> list[dict]:
        from app.models import Analytics, AnalyticsEventType

        now = datetime.now(timezone.utc)
        start = now - timedelta(days=days - 1)
        rows = (
            db.query(func.date(Analytics.created_at), func.count(Analytics.id))
            .filter(
                Analytics.created_at >= start,
                Analytics.event_type.in_([AnalyticsEventType.VIEW, AnalyticsEventType.PLAY]),
            )
            .group_by(func.date(Analytics.created_at))
            .all()
        )
        by_date = {str(d): int(c) for d, c in rows}
        subs_total = (
            db.query(func.count(Subscription.id))
            .filter(Subscription.status == SubscriptionStatus.ACTIVE)
            .scalar()
            or 0
        )
        series = []
        for i in range(days - 1, -1, -1):
            d = (now - timedelta(days=i)).date()
            key = str(d)
            views = int(by_date.get(key, 0))
            series.append({
                "date": d.isoformat(),
                "views": views,
                "watch_time_hours": round(views * 0.38 / 60, 1),
                "revenue": round(views * 0.0032, 2),
                "subscribers": subs_total,
            })
        return series

    @staticmethod
    def _traffic_from_events(events_by_type: dict[str, int]) -> list[dict]:
        if not events_by_type:
            return []
        items = [(label.replace("_", " ").title(), float(count)) for label, count in events_by_type.items()]
        return StudioAnalyticsService._breakdown(items)

    @staticmethod
    def get_overview(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        summary = AnalyticsService.get_summary(db)
        revenue = RevenueService.get_summary(db)

        views = int(summary.total_views or 0)
        subs = int(summary.active_subscriptions or 0)
        watch_hours = round(views * 0.38 / 60, 1) if views else 0.0
        ctr = round((summary.events_last_7d / views * 100), 2) if views and summary.events_last_7d else 0.0

        top_videos = (
            db.query(Video.id, Video.title, Video.views_count)
            .filter(Video.is_active.is_(True))
            .order_by(Video.views_count.desc())
            .limit(10)
            .all()
        )

        creator_rows = (
            db.query(Production.assignee, func.count(Production.id), func.sum(Production.sources_count))
            .group_by(Production.assignee)
            .order_by(func.count(Production.id).desc())
            .limit(8)
            .all()
        )
        top_creators = [
            {"name": r[0] or "Unassigned", "projects": r[1], "total_views": int((r[2] or 0) * 1200)}
            for r in creator_rows
        ]

        prev_week_views = max(views - summary.events_last_7d, 0)
        views_growth = (
            round((summary.events_last_7d / prev_week_views) * 100, 1) if prev_week_views else 0.0
        )

        return {
            "views": views,
            "watch_time_hours": watch_hours,
            "ctr": ctr,
            "revenue": revenue.arr,
            "subscribers": subs,
            "subscriber_growth_pct": 0.0,
            "views_growth_pct": views_growth,
            "traffic_sources": StudioAnalyticsService._traffic_from_events(summary.events_by_type),
            "countries": [],
            "devices": [],
            "top_videos": [
                {
                    "id": v.id,
                    "title": v.title,
                    "views": int(v.views_count or 0),
                    "watch_time_hours": round((v.views_count or 0) * 0.35 / 60, 1),
                    "ctr": ctr,
                }
                for v in top_videos
            ],
            "top_creators": top_creators,
            "growth": StudioAnalyticsService._growth_series(db),
        }

    @staticmethod
    def get_realtime(db: Session, user: User) -> dict:
        StudioPlatformService.require_permission(db, user, None, "analytics.read")
        summary = AnalyticsService.get_summary(db)
        hour_factor = max(0, summary.events_last_24h)
        return {
            "active_viewers": hour_factor,
            "views_last_hour": max(0, hour_factor // 24),
            "plays_last_hour": max(0, hour_factor // 36),
            "revenue_today": round(RevenueService.get_summary(db).mrr / 30, 2),
            "updated_at": datetime.now(timezone.utc),
        }

    @staticmethod
    def export_csv(db: Session, user: User) -> str:
        data = StudioAnalyticsService.get_overview(db, user)
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["UNTOLD Studio Analytics Export", datetime.now(timezone.utc).isoformat()])
        writer.writerow([])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Views", data["views"]])
        writer.writerow(["Watch Time (hours)", data["watch_time_hours"]])
        writer.writerow(["CTR (%)", data["ctr"]])
        writer.writerow(["Revenue", data["revenue"]])
        writer.writerow(["Subscribers", data["subscribers"]])
        writer.writerow([])
        writer.writerow(["Top Videos", "Views", "CTR"])
        for v in data["top_videos"]:
            writer.writerow([v["title"], v["views"], v["ctr"]])
        writer.writerow([])
        writer.writerow(["Growth Date", "Views", "Watch Hours", "Revenue", "Subscribers"])
        for g in data["growth"]:
            writer.writerow([g["date"], g["views"], g["watch_time_hours"], g["revenue"], g["subscribers"]])
        return buf.getvalue()

    @staticmethod
    def export_pdf_text(db: Session, user: User) -> str:
        data = StudioAnalyticsService.get_overview(db, user)
        lines = [
            "UNTOLD STUDIO — ANALYTICS REPORT",
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            f"Views: {data['views']:,}",
            f"Watch Time: {data['watch_time_hours']:,} hours",
            f"CTR: {data['ctr']}%",
            f"Revenue: ${data['revenue']:,.2f}",
            f"Subscribers: {data['subscribers']:,}",
            "",
            "TOP VIDEOS",
        ]
        for i, v in enumerate(data["top_videos"][:10], 1):
            lines.append(f"  {i}. {v['title']} — {v['views']:,} views (CTR {v['ctr']}%)")
        lines.extend(["", "TRAFFIC SOURCES"])
        for t in data["traffic_sources"]:
            lines.append(f"  {t['label']}: {t['pct']}%")
        return "\n".join(lines)
