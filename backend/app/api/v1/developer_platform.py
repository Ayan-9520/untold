"""Public developer platform REST API — self-service portal backend."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.domain.gateway.scopes import DEVELOPER_ACCOUNT_TIERS, GATEWAY_SCOPES, RATE_LIMIT_TIERS, WEBHOOK_EVENTS
from app.models import User
from app.schemas.api_gateway import GatewayWebhookCreate
from app.schemas.developer_platform import (
    DeveloperAccountResponse,
    DeveloperApiKeyCreate,
    DeveloperApiKeyCreateResponse,
    DeveloperApiKeyResponse,
    DeveloperRegister,
)
from app.services.developer_platform_service import DeveloperPlatformService

router = APIRouter(prefix="/developer", tags=["Developer Platform"])


@router.post("/register", response_model=DeveloperAccountResponse, status_code=201)
def register_developer(
    data: DeveloperRegister,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return DeveloperPlatformService.register(db, user, company_name=data.company_name, website=data.website)


@router.get("/me", response_model=DeveloperAccountResponse)
def developer_me(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    return DeveloperPlatformService.get_account(db, user)


@router.get("/docs")
def developer_docs():
    return DeveloperPlatformService.platform_docs()


@router.get("/scopes")
def developer_scopes():
    return {
        "scopes": GATEWAY_SCOPES,
        "rate_limit_tiers": RATE_LIMIT_TIERS,
        "account_tiers": {k: {**v, "allowed_rate_tiers": sorted(v["allowed_rate_tiers"])} for k, v in DEVELOPER_ACCOUNT_TIERS.items()},
        "webhook_events": list(WEBHOOK_EVENTS),
    }


@router.get("/sandbox")
def sandbox_info():
    return DeveloperPlatformService.sandbox_info()


@router.get("/keys", response_model=list[DeveloperApiKeyResponse])
def list_developer_keys(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    return DeveloperPlatformService.list_keys(db, user)


@router.post("/keys", response_model=DeveloperApiKeyCreateResponse, status_code=201)
def create_developer_key(
    data: DeveloperApiKeyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return DeveloperPlatformService.create_key(db, user, data)


@router.delete("/keys/{key_id}", status_code=204)
def revoke_developer_key(
    key_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)
):
    DeveloperPlatformService.revoke_key(db, user, key_id)


@router.get("/usage/overview")
def developer_usage_overview(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    return DeveloperPlatformService.usage_overview(db, user)


@router.get("/usage/timeseries")
def developer_usage_timeseries(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
    days: int = Query(7, ge=1, le=90),
):
    return DeveloperPlatformService.usage_timeseries(db, user, days=days)


@router.get("/usage/endpoints")
def developer_usage_endpoints(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
    limit: int = Query(20, ge=1, le=100),
):
    return DeveloperPlatformService.usage_endpoints(db, user, limit=limit)


@router.get("/webhooks")
def list_developer_webhooks(db: Session = Depends(get_db), user: User = Depends(get_current_active_user)):
    return DeveloperPlatformService.list_webhooks(db, user)


@router.post("/webhooks", status_code=201)
def create_developer_webhook(
    data: GatewayWebhookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return DeveloperPlatformService.create_webhook(db, user, data)


@router.delete("/webhooks/{webhook_id}", status_code=204)
def delete_developer_webhook(
    webhook_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)
):
    DeveloperPlatformService.delete_webhook(db, user, webhook_id)


@router.post("/webhooks/{webhook_id}/test")
def test_developer_webhook(
    webhook_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_active_user)
):
    return DeveloperPlatformService.test_webhook(db, user, webhook_id)


@router.get("/webhooks/{webhook_id}/deliveries")
def developer_webhook_deliveries(
    webhook_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
    limit: int = Query(50, ge=1, le=200),
):
    return DeveloperPlatformService.webhook_deliveries(db, user, webhook_id, limit=limit)
