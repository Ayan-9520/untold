from fastapi import APIRouter

from app.api.v1 import admin, ai_pipeline, analytics, auth, categories, community, live, magazine, membership, news, payments, streaming, users, videos, watchlist
from app.schemas.auth import TokenResponse, UserResponse

api_router = APIRouter()

# Module routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(videos.router)
api_router.include_router(live.router)
api_router.include_router(magazine.router)
api_router.include_router(categories.router)
api_router.include_router(watchlist.router)
api_router.include_router(community.router)
api_router.include_router(news.router)
api_router.include_router(news.admin_router)
api_router.include_router(analytics.router)
api_router.include_router(admin.router)
api_router.include_router(ai_pipeline.router)
api_router.include_router(membership.router)
api_router.include_router(payments.router)
api_router.include_router(payments.webhook_router)
api_router.include_router(streaming.router)

# Spec aliases: POST /register, POST /login (at /api/v1 root)
api_router.add_api_route(
    "/register",
    auth.register,
    methods=["POST"],
    response_model=UserResponse,
    status_code=201,
    tags=["Auth"],
)
api_router.add_api_route(
    "/login",
    auth.login,
    methods=["POST"],
    response_model=TokenResponse,
    tags=["Auth"],
)
