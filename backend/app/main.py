"""
FastAPI application entry point.

Owner: Owner 2 — Backend

Sets up:
- sys.path so the sibling ``classification/`` package is importable
- FastAPI app with CORS middleware
- Lifespan handler to manage the Roboflow client lifecycle
- Route registration
"""

from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Make the classification package importable ───────────────────────────
# In production you would install it as a proper package instead.
_CLASSIFICATION_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "classification"
)
if _CLASSIFICATION_DIR not in sys.path:
    sys.path.insert(0, _CLASSIFICATION_DIR)

from .config import settings
from .routes.analyze import roboflow_client, router as analyze_router
from .routes.health import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hook — manages long-lived resources."""
    logger.info("Starting US LI-RADS Classifier v%s", settings.app_version)
    yield
    await roboflow_client.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title="US LI-RADS Classifier",
    description="Prototype ultrasound LI-RADS surveillance classification API",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
