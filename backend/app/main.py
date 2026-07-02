import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import api_router
from app.gateway.graphql_schema import create_graphql_router
from app.gateway.middleware import GatewayUsageMiddleware
from app.middleware.compliance_access_log import ComplianceAccessLogMiddleware
from app.gateway.router import gateway_router
from app.core.config import get_settings
from app.core.telemetry import configure_logging, setup_telemetry
from app.core.exceptions import AppException
from app.core.redis import ping_redis
from app.db.init_db import seed_database
from app.db.migrate import run_migrations
from app.db.session import engine
from app.middleware.rate_limit import limiter, setup_rate_limiting
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.websocket.live import redis_live_listener, router as ws_router
from app.websocket.studio import router as studio_ws_router

settings = get_settings()
configure_logging(settings)
logger = logging.getLogger("untold")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s [%s]", settings.app_name, settings.app_version, settings.environment)
    # Docker entrypoint runs migrations + seed when RUN_MIGRATIONS=true
    if os.getenv("RUN_MIGRATIONS") != "true":
        run_migrations()
        seed_database()
    ws_task = None
    if settings.enable_websocket:
        ws_task = asyncio.create_task(redis_live_listener())
    yield
    if ws_task:
        ws_task.cancel()
        try:
            await ws_task
        except asyncio.CancelledError:
            pass
    engine.dispose()
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready REST API for UNTOLD — The Story Behind The Glory",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "X-API-Key",
        "X-Request-ID",
        "X-API-Version",
        "Accept-Version",
        "X-Organization-ID",
        "X-Workspace-ID",
    ],
)

if settings.is_production and settings.trusted_host_list != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ComplianceAccessLogMiddleware)

setup_rate_limiting(app, settings)
app.add_middleware(GatewayUsageMiddleware)
setup_telemetry(app, settings)


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "code": "VALIDATION_ERROR"},
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(_: Request, exc: SQLAlchemyError):
    logger.exception("Database error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred", "code": "DATABASE_ERROR"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    detail = "Internal server error" if settings.is_production else str(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail, "code": "INTERNAL_ERROR"},
    )


@app.get("/live", tags=["Health"])
@limiter.exempt
def liveness_check():
    """Kubernetes liveness — process is running."""
    return {"status": "alive"}


@app.get("/ready", tags=["Health"])
@limiter.exempt
def readiness_check():
    """Kubernetes readiness — dependencies available."""
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        logger.warning("Readiness — database unreachable: %s", exc)

    redis_ok = ping_redis()
    ready = db_ok and redis_ok
    return JSONResponse(
        status_code=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "ready" if ready else "not_ready",
            "checks": {"database": "up" if db_ok else "down", "redis": "up" if redis_ok else "down"},
        },
    )


@app.get("/health", tags=["Health"])
@limiter.exempt
def health_check(request: Request):
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        logger.warning("Health check — database unreachable: %s", exc)

    redis_ok = ping_redis()

    overall = "healthy" if db_ok else "unhealthy"
    status_code = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall,
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "checks": {
                "database": "up" if db_ok else "down",
                "redis": "up" if redis_ok else "down",
            },
        },
    )


app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(gateway_router, prefix="/gateway")
app.include_router(create_graphql_router(), prefix="/gateway/graphql")
app.include_router(create_graphql_router(), prefix="/gateway/sandbox/graphql")
if settings.enable_websocket:
    app.include_router(ws_router, tags=["WebSocket"])
    app.include_router(studio_ws_router, tags=["WebSocket"])
