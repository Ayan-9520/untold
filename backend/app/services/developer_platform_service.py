"""Public developer platform — self-service keys, usage, sandbox."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.domain.gateway.auth import hash_api_key
from app.domain.gateway.scopes import (
    DEFAULT_API_KEY_SCOPES,
    DEVELOPER_ACCOUNT_TIERS,
    GATEWAY_SCOPES,
    RATE_LIMIT_TIERS,
    SUPPORTED_VERSIONS,
    WEBHOOK_EVENTS,
)
from app.models import User
from app.models.studio.developer import DeveloperAccount
from app.models.studio_platform import ApiGatewayUsageLog, ApiGatewayWebhook, ApiGatewayWebhookDelivery, StudioApiKey
from app.services.api_gateway_service import ApiGatewayService


class DeveloperPlatformService:
    @staticmethod
    def register(db: Session, user: User, *, company_name: str | None = None, website: str | None = None) -> dict:
        existing = db.query(DeveloperAccount).filter(DeveloperAccount.user_id == user.id).first()
        if existing:
            if company_name:
                existing.company_name = company_name
            if website:
                existing.website = website
            db.commit()
            db.refresh(existing)
            return DeveloperPlatformService._account_dict(existing)

        row = DeveloperAccount(
            user_id=user.id,
            company_name=company_name or user.full_name,
            website=website,
            tier="free",
            sandbox_enabled=True,
            approved_at=datetime.now(timezone.utc),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return DeveloperPlatformService._account_dict(row)

    @staticmethod
    def get_account(db: Session, user: User) -> dict:
        row = db.query(DeveloperAccount).filter(DeveloperAccount.user_id == user.id).first()
        if not row:
            raise NotFoundError("Developer account not found — register first")
        return DeveloperPlatformService._account_dict(row)

    @staticmethod
    def require_account(db: Session, user: User) -> DeveloperAccount:
        row = db.query(DeveloperAccount).filter(DeveloperAccount.user_id == user.id).first()
        if not row:
            raise ForbiddenError("Register a developer account first")
        return row

    @staticmethod
    def platform_docs() -> dict:
        base = ApiGatewayService.gateway_docs()
        return {
            **base,
            "title": "UNTOLD Developer Platform",
            "environments": {
                "production": {
                    "base_url": "/gateway",
                    "rest": "/gateway/v1",
                    "graphql": "/gateway/graphql",
                    "key_prefix": "unt_live_",
                },
                "sandbox": {
                    "base_url": "/gateway/sandbox",
                    "rest": "/gateway/sandbox/v1",
                    "graphql": "/gateway/sandbox/graphql",
                    "key_prefix": "unt_sandbox_",
                    "note": "Sandbox returns sample data — no production side effects.",
                },
            },
            "sdk": {
                "npm": "@untold/developer-sdk",
                "import": "import { UntoldClient } from '@untold/developer-sdk'",
            },
            "portal_url": "/developers",
            "self_service": "/api/v1/developer",
        }

    @staticmethod
    def list_keys(db: Session, user: User) -> list[dict]:
        DeveloperPlatformService.require_account(db, user)
        rows = (
            db.query(StudioApiKey)
            .filter(StudioApiKey.created_by_id == user.id)
            .order_by(StudioApiKey.created_at.desc())
            .all()
        )
        return [DeveloperPlatformService._key_dict(r) for r in rows]

    @staticmethod
    def create_key(db: Session, user: User, data) -> dict:
        account = DeveloperPlatformService.require_account(db, user)
        env = data.environment or "production"
        if env == "sandbox" and not account.sandbox_enabled:
            raise ForbiddenError("Sandbox is disabled for this account")

        scopes = data.scopes or DEFAULT_API_KEY_SCOPES
        for s in scopes:
            if s not in GATEWAY_SCOPES:
                raise BadRequestError(f"Unknown scope: {s}")

        tier_limits = DEVELOPER_ACCOUNT_TIERS.get(account.tier, DEVELOPER_ACCOUNT_TIERS["free"])
        active_keys = (
            db.query(func.count(StudioApiKey.id))
            .filter(StudioApiKey.created_by_id == user.id, StudioApiKey.is_active.is_(True))
            .scalar()
            or 0
        )
        if active_keys >= tier_limits["max_active_keys"]:
            raise BadRequestError(
                f"Active key limit reached ({tier_limits['max_active_keys']} for {account.tier} tier)"
            )

        requested_tier = data.rate_limit_tier or "free"
        if requested_tier not in RATE_LIMIT_TIERS:
            raise BadRequestError(f"Unknown rate limit tier: {requested_tier}")
        if requested_tier not in tier_limits["allowed_rate_tiers"]:
            raise ForbiddenError(f"Rate limit tier '{requested_tier}' is not available on the {account.tier} plan")
        tier = requested_tier

        prefix_label = "unt_sandbox_" if env == "sandbox" else "unt_live_"
        secret = f"{prefix_label}{secrets.token_urlsafe(28)}"
        prefix = secret[:16]
        row = StudioApiKey(
            name=data.name,
            key_prefix=prefix,
            key_hash=hash_api_key(secret),
            permissions=scopes,
            scopes=scopes,
            rate_limit_tier=tier,
            api_version=data.api_version or "v1",
            environment=env,
            expires_at=data.expires_at,
            created_by_id=user.id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        result = DeveloperPlatformService._key_dict(row)
        result["secret_key"] = secret
        return result

    @staticmethod
    def revoke_key(db: Session, user: User, key_id: int) -> None:
        DeveloperPlatformService.require_account(db, user)
        row = (
            db.query(StudioApiKey)
            .filter(StudioApiKey.id == key_id, StudioApiKey.created_by_id == user.id)
            .first()
        )
        if not row:
            raise NotFoundError("API key not found")
        row.is_active = False
        db.commit()

    @staticmethod
    def usage_overview(db: Session, user: User) -> dict:
        DeveloperPlatformService.require_account(db, user)
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        key_ids = [k.id for k in db.query(StudioApiKey.id).filter(StudioApiKey.created_by_id == user.id).all()]
        if not key_ids:
            return {
                "requests_24h": 0,
                "requests_7d": 0,
                "avg_latency_ms": 0,
                "error_rate_24h_pct": 0,
                "active_keys": 0,
                "by_environment": {},
                "by_protocol": {},
            }

        base = db.query(ApiGatewayUsageLog).filter(ApiGatewayUsageLog.api_key_id.in_(key_ids))
        requests_24h = base.filter(ApiGatewayUsageLog.created_at >= day_ago).count()
        requests_7d = base.filter(ApiGatewayUsageLog.created_at >= week_ago).count()
        avg_latency = (
            db.query(func.avg(ApiGatewayUsageLog.latency_ms))
            .filter(ApiGatewayUsageLog.api_key_id.in_(key_ids), ApiGatewayUsageLog.created_at >= day_ago)
            .scalar()
        )
        errors_24h = base.filter(
            ApiGatewayUsageLog.created_at >= day_ago, ApiGatewayUsageLog.status_code >= 400
        ).count()
        active_keys = (
            db.query(func.count(StudioApiKey.id))
            .filter(StudioApiKey.created_by_id == user.id, StudioApiKey.is_active.is_(True))
            .scalar()
            or 0
        )

        by_env = (
            db.query(ApiGatewayUsageLog.environment, func.count(ApiGatewayUsageLog.id))
            .filter(ApiGatewayUsageLog.api_key_id.in_(key_ids), ApiGatewayUsageLog.created_at >= week_ago)
            .group_by(ApiGatewayUsageLog.environment)
            .all()
        )
        by_protocol = (
            db.query(ApiGatewayUsageLog.protocol, func.count(ApiGatewayUsageLog.id))
            .filter(ApiGatewayUsageLog.api_key_id.in_(key_ids), ApiGatewayUsageLog.created_at >= week_ago)
            .group_by(ApiGatewayUsageLog.protocol)
            .all()
        )

        return {
            "requests_24h": requests_24h,
            "requests_7d": requests_7d,
            "avg_latency_ms": round(float(avg_latency or 0), 1),
            "error_rate_24h_pct": round((errors_24h / requests_24h * 100) if requests_24h else 0, 2),
            "active_keys": int(active_keys),
            "by_environment": {e: c for e, c in by_env},
            "by_protocol": {p: c for p, c in by_protocol},
        }

    @staticmethod
    def usage_timeseries(db: Session, user: User, *, days: int = 7) -> list[dict]:
        DeveloperPlatformService.require_account(db, user)
        key_ids = [k.id for k in db.query(StudioApiKey.id).filter(StudioApiKey.created_by_id == user.id).all()]
        if not key_ids:
            return []
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = (
            db.query(
                func.date_trunc("day", ApiGatewayUsageLog.created_at).label("day"),
                func.count(ApiGatewayUsageLog.id).label("requests"),
                func.avg(ApiGatewayUsageLog.latency_ms).label("avg_latency"),
            )
            .filter(ApiGatewayUsageLog.api_key_id.in_(key_ids), ApiGatewayUsageLog.created_at >= since)
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
    def usage_endpoints(db: Session, user: User, *, limit: int = 20) -> list[dict]:
        DeveloperPlatformService.require_account(db, user)
        key_ids = [k.id for k in db.query(StudioApiKey.id).filter(StudioApiKey.created_by_id == user.id).all()]
        if not key_ids:
            return []
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        rows = (
            db.query(
                ApiGatewayUsageLog.path,
                ApiGatewayUsageLog.method,
                func.count(ApiGatewayUsageLog.id).label("count"),
            )
            .filter(ApiGatewayUsageLog.api_key_id.in_(key_ids), ApiGatewayUsageLog.created_at >= week_ago)
            .group_by(ApiGatewayUsageLog.path, ApiGatewayUsageLog.method)
            .order_by(func.count(ApiGatewayUsageLog.id).desc())
            .limit(limit)
            .all()
        )
        return [{"path": r.path, "method": r.method, "requests": r.count} for r in rows]

    @staticmethod
    def list_webhooks(db: Session, user: User) -> list[dict]:
        DeveloperPlatformService.require_account(db, user)
        rows = db.query(ApiGatewayWebhook).filter(ApiGatewayWebhook.user_id == user.id).all()
        return [ApiGatewayService._webhook_dict(w) for w in rows]

    @staticmethod
    def create_webhook(db: Session, user: User, data) -> dict:
        DeveloperPlatformService.require_account(db, user)
        return ApiGatewayService.create_webhook(db, user, data)

    @staticmethod
    def delete_webhook(db: Session, user: User, webhook_id: int) -> None:
        DeveloperPlatformService.require_account(db, user)
        ApiGatewayService.delete_webhook(db, user, webhook_id)

    @staticmethod
    def test_webhook(db: Session, user: User, webhook_id: int) -> list[dict]:
        DeveloperPlatformService.require_account(db, user)
        return ApiGatewayService.test_webhook(db, user, webhook_id)

    @staticmethod
    def webhook_deliveries(db: Session, user: User, webhook_id: int, *, limit: int = 50) -> list[dict]:
        DeveloperPlatformService.require_account(db, user)
        row = (
            db.query(ApiGatewayWebhook)
            .filter(ApiGatewayWebhook.id == webhook_id, ApiGatewayWebhook.user_id == user.id)
            .first()
        )
        if not row:
            raise NotFoundError("Webhook not found")
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
    def sandbox_info() -> dict:
        return {
            "environment": "sandbox",
            "sample_videos": 3,
            "sample_projects": 2,
            "webhooks_delivered": False,
            "rate_limits_relaxed": True,
            "supported_versions": list(SUPPORTED_VERSIONS),
        }

    @staticmethod
    def _account_dict(row: DeveloperAccount) -> dict:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "company_name": row.company_name,
            "website": row.website,
            "tier": row.tier,
            "sandbox_enabled": row.sandbox_enabled,
            "approved_at": row.approved_at,
            "created_at": row.created_at,
        }

    @staticmethod
    def _key_dict(row: StudioApiKey) -> dict:
        return {
            "id": row.id,
            "name": row.name,
            "key_prefix": row.key_prefix,
            "environment": getattr(row, "environment", None) or "production",
            "scopes": row.scopes or row.permissions or [],
            "rate_limit_tier": row.rate_limit_tier,
            "api_version": row.api_version,
            "is_active": row.is_active,
            "total_requests": row.total_requests or 0,
            "last_used_at": row.last_used_at,
            "expires_at": row.expires_at,
            "created_at": row.created_at,
        }
