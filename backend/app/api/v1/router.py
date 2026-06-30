from fastapi import APIRouter

from app.api.v1 import admin, agent_marketplace, ai_cost, ai_pipeline, ai_studio, analytics, api_gateway, asset_library, auth, categories, collaboration, community, enterprise_security, enterprise_security_auth, image_studio, live, magazine, membership, music_studio, news, payments, plugin_sdk, production_pipeline, publishing_agent, publishing_cms, research_studio, script_studio, seo_studio, shorts_studio, storyboard_studio, streaming, studio, studio_admin, studio_analytics, studio_platform, timeline_editor, translation_studio, users, video_studio, videos, voice_studio, watchlist, workflow_engine
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
api_router.include_router(studio.router)
api_router.include_router(studio_platform.router)
api_router.include_router(research_studio.router)
api_router.include_router(script_studio.router)
api_router.include_router(storyboard_studio.router)
api_router.include_router(ai_studio.router)
api_router.include_router(image_studio.router)
api_router.include_router(video_studio.router)
api_router.include_router(voice_studio.router)
api_router.include_router(music_studio.router)
api_router.include_router(shorts_studio.router)
api_router.include_router(seo_studio.router)
api_router.include_router(translation_studio.router)
api_router.include_router(asset_library.router)
api_router.include_router(timeline_editor.router)
api_router.include_router(publishing_cms.router)
api_router.include_router(publishing_agent.router)
api_router.include_router(production_pipeline.router)
api_router.include_router(workflow_engine.router)
api_router.include_router(agent_marketplace.router)
api_router.include_router(ai_cost.router)
api_router.include_router(collaboration.router)
api_router.include_router(plugin_sdk.router)
api_router.include_router(api_gateway.router)
api_router.include_router(enterprise_security.router)
api_router.include_router(enterprise_security_auth.router)
api_router.include_router(studio_analytics.router)
api_router.include_router(studio_admin.router)
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
