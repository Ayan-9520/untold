"""API Gateway router assembly."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

from app.gateway.openapi_spec import OPENAPI_SPEC
from app.gateway.rest import router as rest_router
from app.gateway.sandbox import router as sandbox_router
from app.services.api_gateway_service import ApiGatewayService

gateway_router = APIRouter(tags=["API Gateway"])
gateway_router.include_router(rest_router)
gateway_router.include_router(sandbox_router, prefix="/sandbox")


@gateway_router.get("/")
def gateway_index():
    return ApiGatewayService.gateway_docs()


@gateway_router.get("/openapi.json", include_in_schema=False)
def gateway_openapi():
    return JSONResponse(OPENAPI_SPEC)


@gateway_router.get("/docs", include_in_schema=False)
def gateway_swagger_ui():
    return get_swagger_ui_html(openapi_url="/gateway/openapi.json", title="UNTOLD API Gateway")
