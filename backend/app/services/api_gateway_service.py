"""API Gateway service — usage analytics, webhooks, key management."""

from __future__ import annotations

import math
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.domain.gateway.scopes import DEFAULT_API_KEY_SCOPES, GATEWAY_SCOPES, RATE_LIMIT_TIERS, WEBHOOK_EVENTS
from app.domain.gateway.webhook_validation import validate_webhook_url
from app.domain.gateway.webhooks import deliver_gateway_webhooks
from app.models import User
from app.models.studio_platform import ApiGatewayUsageLog, ApiGatewayWebhook, ApiGatewayWebhookDelivery, StudioApiKey
from app.services.studio_admin_service import StudioAdminService


class ApiGatewayService:
    @staticmethod
    def log_usage(
        db: Session,
        *,
        auth,
        method: str,
        path: str,
        status_code: int,
        latency_ms: int | None,
        protocol: str = "rest",
        ip_address: str | None = None,
        user_agent: str | None = None,
        error_code: str | None = None,
        environment: str = "production",
        commit: bool = True,
    ) -> None:
        request_id = auth.request_id or str(uuid.uuid4())
        env = environment
        if auth.api_key and getattr(auth.api_key, "environment", None):
            env = auth.api_key.environment
        row = ApiGatewayUsageLog(
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id,
            method=method,
            path=path,
            api_version=auth.api_version,
            protocol=protocol,
            status_code=status_code,
            latency_ms=latency_ms,
            ip_address=ip_address,
            user_agent=(user_agent or "")[:500] or None,
            request_id=request_id,
            error_code=error_code,
            environment=env,
        )
        db.add(row)
        if auth.api_key:
            auth.api_key.last_used_at = datetime.now(timezone.utc)
            auth.api_key.total_requests = (auth.api_key.total_requests or 0) + 1
        if commit:
            db.commit()

    @staticmethod
    def overview(db: Session, user: User) -> dict:
        StudioAdminService._require_admin(db, user)
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        total_keys = db.query(func.count(StudioApiKey.id)).filter(StudioApiKey.is_active.is_(True)).scalar() or 0
        requests_24h = (
            db.query(func.count(ApiGatewayUsageLog.id)).filter(ApiGatewayUsageLog.created_at >= day_ago).scalar() or 0
        )
        requests_7d = (
            db.query(func.count(ApiGatewayUsageLog.id)).filter(ApiGatewayUsageLog.created_at >= week_ago).scalar() or 0
        )
        avg_latency = (
            db.query(func.avg(ApiGatewayUsageLog.latency_ms))
            .filter(ApiGatewayUsageLog.created_at >= day_ago, ApiGatewayUsageLog.latency_ms.isnot(None))
            .scalar()
        )
        error_rate = (
            db.query(func.count(ApiGatewayUsageLog.id))
            .filter(ApiGatewayUsageLog.created_at >= day_ago, ApiGatewayUsageLog.status_code >= 400)
            .scalar()
            or 0
        )
        webhooks = db.query(func.count(ApiGatewayWebhook.id)).filter(ApiGatewayWebhook.is_active.is_(True)).scalar() or 0

        by_version = (
            db.query(ApiGatewayUsageLog.api_version, func.count(ApiGatewayUsageLog.id))
            .filter(ApiGatewayUsageLog.created_at >= week_ago)
            .group_by(ApiGatewayUsageLog.api_version)
            .all()
        )
        by_protocol = (
            db.query(ApiGatewayUsageLog.protocol, func.count(ApiGatewayUsageLog.id))
            .filter(ApiGatewayUsageLog.created_at >= week_ago)
            .group_by(ApiGatewayUsageLog.protocol)
            .all()
        )

        return {
            "active_api_keys": total_keys,
            "requests_24h": requests_24h,
            "requests_7d": requests_7d,
            "avg_latency_ms": round(float(avg_latency or 0), 1),
            "error_rate_24h_pct": round((error_rate / requests_24h * 100) if requests_24h else 0, 2),
            "active_webhooks": webhooks,
            "supported_versions": ["v1", "v2"],
            "rate_limit_tiers": RATE_LIMIT_TIERS,
            "by_version": {v: c for v, c in by_version},
            "by_protocol": {p: c for p, c in by_protocol},
        }

    @staticmethod
    def usage_timeseries(db: Session, user: User, *, days: int = 7) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = (
            db.query(
                func.date_trunc("day", ApiGatewayUsageLog.created_at).label("day"),
                func.count(ApiGatewayUsageLog.id).label("requests"),
                func.avg(ApiGatewayUsageLog.latency_ms).label("avg_latency"),
            )
            .filter(ApiGatewayUsageLog.created_at >= since)
            .group_by("day")
            .order_by("day")
            .all()
        )
        return [
            {
                "date": r.day.date().isoformat() if r.day else None,
                "requests": r.requests,
                "avg_latency_ms": round(float(r.avg_latency or 0), 1),
            }
            for r in rows
        ]

    @staticmethod
    def usage_by_endpoint(db: Session, user: User, *, limit: int = 20) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        rows = (
            db.query(
                ApiGatewayUsageLog.path,
                ApiGatewayUsageLog.method,
                func.count(ApiGatewayUsageLog.id).label("count"),
                func.avg(ApiGatewayUsageLog.latency_ms).label("avg_latency"),
            )
            .filter(ApiGatewayUsageLog.created_at >= week_ago)
            .group_by(ApiGatewayUsageLog.path, ApiGatewayUsageLog.method)
            .order_by(func.count(ApiGatewayUsageLog.id).desc())
            .limit(limit)
            .all()
        )
        return [
            {"path": r.path, "method": r.method, "requests": r.count, "avg_latency_ms": round(float(r.avg_latency or 0), 1)}
            for r in rows
        ]

    @staticmethod
    def list_keys(db: Session, user: User) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        rows = db.query(StudioApiKey).order_by(StudioApiKey.created_at.desc()).all()
        return [ApiGatewayService._key_dict(r) for r in rows]

    @staticmethod
    def _key_dict(row: StudioApiKey) -> dict:
        return {
            "id": row.id,
            "name": row.name,
            "key_prefix": row.key_prefix,
            "environment": getattr(row, "environment", None) or "production",
            "permissions": row.permissions or [],
            "scopes": row.scopes or row.permissions or [],
            "rate_limit_tier": row.rate_limit_tier,
            "api_version": row.api_version,
            "is_active": row.is_active,
            "total_requests": row.total_requests or 0,
            "last_used_at": row.last_used_at,
            "expires_at": row.expires_at,
            "created_at": row.created_at,
        }

    @staticmethod
    def create_key(db: Session, user: User, data) -> dict:
        from app.domain.gateway.auth import hash_api_key

        StudioAdminService._require_admin(db, user, "admin.manage")
        secret = f"unt_live_{secrets.token_urlsafe(32)}"
        prefix = secret[:12]
        key_hash = hash_api_key(secret)
        scopes = data.scopes or data.permissions or DEFAULT_API_KEY_SCOPES
        row = StudioApiKey(
            name=data.name,
            key_prefix=prefix,
            key_hash=key_hash,
            permissions=scopes,
            scopes=scopes,
            rate_limit_tier=data.rate_limit_tier or "standard",
            api_version=data.api_version or "v1",
            environment="production",
            expires_at=data.expires_at,
            created_by_id=user.id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        result = ApiGatewayService._key_dict(row)
        result["secret_key"] = secret
        return result

    @staticmethod
    def revoke_key(db: Session, user: User, key_id: int) -> None:
        StudioAdminService.revoke_api_key(db, user, key_id)

    @staticmethod
    def list_webhooks(db: Session, user: User) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        rows = db.query(ApiGatewayWebhook).order_by(ApiGatewayWebhook.created_at.desc()).all()
        return [ApiGatewayService._webhook_dict(w) for w in rows]

    @staticmethod
    def _webhook_dict(w: ApiGatewayWebhook) -> dict:
        return {
            "id": w.id,
            "name": w.name,
            "url": w.url,
            "events": w.events or [],
            "is_active": w.is_active,
            "failure_count": w.failure_count,
            "last_triggered_at": w.last_triggered_at,
            "created_at": w.created_at,
        }

    @staticmethod
    def create_webhook(db: Session, user: User, data, *, api_key_id: int | None = None) -> dict:
        for ev in data.events:
            if ev not in WEBHOOK_EVENTS:
                raise BadRequestError(f"Unknown webhook event: {ev}")
        validate_webhook_url(data.url)
        secret = secrets.token_hex(32)
        row = ApiGatewayWebhook(
            user_id=user.id,
            api_key_id=api_key_id,
            name=data.name,
            url=data.url,
            secret=secret,
            events=data.events,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        result = ApiGatewayService._webhook_dict(row)
        result["signing_secret"] = secret
        return result

    @staticmethod
    def delete_webhook(db: Session, user: User, webhook_id: int) -> None:
        row = db.query(ApiGatewayWebhook).filter(ApiGatewayWebhook.id == webhook_id).first()
        if not row:
            raise NotFoundError("Webhook not found")
        if not user.is_admin and row.user_id != user.id:
            raise NotFoundError("Webhook not found")
        db.delete(row)
        db.commit()

    @staticmethod
    def webhook_deliveries(db: Session, user: User, webhook_id: int, *, limit: int = 50) -> list[dict]:
        StudioAdminService._require_admin(db, user)
        rows = (
            db.query(ApiGatewayWebhookDelivery)
            .filter(ApiGatewayWebhookDelivery.webhook_id == webhook_id)
            .order_by(ApiGatewayWebhookDelivery.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "event_type": r.event_type,
                "status": r.status,
                "http_status": r.http_status,
                "attempts": r.attempts,
                "created_at": r.created_at,
            }
            for r in rows
        ]

    @staticmethod
    def test_webhook(db: Session, user: User, webhook_id: int) -> list[dict]:
        row = db.query(ApiGatewayWebhook).filter(ApiGatewayWebhook.id == webhook_id).first()
        if not row:
            raise NotFoundError("Webhook not found")
        return deliver_gateway_webhooks(
            db,
            "api_key.used",
            {"test": True, "webhook_id": webhook_id, "triggered_by": user.id},
            user_id=row.user_id,
        )

    @staticmethod
    def gateway_docs() -> dict:
        return {
            "title": "UNTOLD API Gateway",
            "versions": {
                "v1": {"status": "stable", "base_path": "/gateway/v1"},
                "v2": {"status": "stable", "base_path": "/gateway/v2", "envelope": True},
            },
            "authentication": {
                "methods": ["Bearer JWT", "X-API-Key"],
                "headers": ["Authorization", "X-API-Key", "X-API-Version", "X-Request-ID"],
            },
            "protocols": ["REST", "GraphQL"],
            "scopes": GATEWAY_SCOPES,
            "rate_limit_tiers": RATE_LIMIT_TIERS,
            "webhook_events": list(WEBHOOK_EVENTS),
            "openapi_url": "/gateway/openapi.json",
            "graphql_url": "/gateway/graphql",
            "developer_portal": "/developers",
            "self_service_api": "/api/v1/developer",
        }

    @staticmethod
    def wrap_v2(data, auth, *, page: int | None = None, total: int | None = None) -> dict:
        meta = {"version": "v2", "request_id": auth.request_id}
        if page is not None:
            meta["page"] = page
        if total is not None:
            meta["total"] = total
        return {"data": data, "meta": meta}
