"""API Gateway admin REST API — Studio management console."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.db.session import get_db
from app.models import User
from app.schemas.api_gateway import (
    GatewayApiKeyCreate,
    GatewayApiKeyCreateResponse,
    GatewayApiKeyResponse,
    GatewayOverviewResponse,
    GatewayWebhookCreate,
    GatewayWebhookResponse,
)
from app.services.api_gateway_service import ApiGatewayService

router = APIRouter(prefix="/studio/platform/api-gateway", tags=["API Gateway Admin"])


@router.get("/overview", response_model=GatewayOverviewResponse)
def gateway_overview(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return ApiGatewayService.overview(db, user)


@router.get("/usage/timeseries")
def gateway_usage_timeseries(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
    days: int = Query(7, ge=1, le=90),
):
    return ApiGatewayService.usage_timeseries(db, user, days=days)


@router.get("/usage/endpoints")
def gateway_usage_endpoints(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
    limit: int = Query(20, ge=1, le=100),
):
    return ApiGatewayService.usage_by_endpoint(db, user, limit=limit)


@router.get("/docs")
def gateway_admin_docs():
    return ApiGatewayService.gateway_docs()


@router.get("/keys", response_model=list[GatewayApiKeyResponse])
def list_gateway_keys(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return ApiGatewayService.list_keys(db, user)


@router.post("/keys", response_model=GatewayApiKeyCreateResponse, status_code=201)
def create_gateway_key(
    data: GatewayApiKeyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return ApiGatewayService.create_key(db, user, data)


@router.delete("/keys/{key_id}", status_code=204)
def revoke_gateway_key(key_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    ApiGatewayService.revoke_key(db, user, key_id)


@router.get("/webhooks", response_model=list[GatewayWebhookResponse])
def list_gateway_webhooks(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return ApiGatewayService.list_webhooks(db, user)


@router.post("/webhooks", status_code=201)
def create_gateway_webhook(
    data: GatewayWebhookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
):
    return ApiGatewayService.create_webhook(db, user, data)


@router.delete("/webhooks/{webhook_id}", status_code=204)
def delete_gateway_webhook(
    webhook_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_admin)
):
    ApiGatewayService.delete_webhook(db, user, webhook_id)


@router.get("/webhooks/{webhook_id}/deliveries")
def webhook_deliveries(
    webhook_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_admin),
    limit: int = Query(50, ge=1, le=200),
):
    return ApiGatewayService.webhook_deliveries(db, user, webhook_id, limit=limit)


@router.post("/webhooks/{webhook_id}/test")
def test_gateway_webhook(
    webhook_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_admin)
):
    return ApiGatewayService.test_webhook(db, user, webhook_id)
