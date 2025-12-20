"""Aggregated API v1 router."""

from fastapi import APIRouter

from app.api.v1 import ai, comments, health, images, music, threads, videos

api_router = APIRouter()

# Include all v1 routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(threads.router, prefix="/threads", tags=["Threads"])
api_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(images.router, prefix="/ai/images", tags=["AI Images"])
api_router.include_router(videos.router, prefix="/ai/videos", tags=["AI Videos"])
api_router.include_router(music.router, prefix="/ai/music", tags=["AI Music"])

