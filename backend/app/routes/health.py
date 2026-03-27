"""
GET /api/health

Owner: Owner 2 — Backend
"""

from fastapi import APIRouter

from ..config import settings

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": settings.app_version}
