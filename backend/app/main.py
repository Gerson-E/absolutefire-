"""
FastAPI application entry point.

Owner: Owner 2 — Backend
"""

import sys
import os

# Allow importing classification module from the sibling folder.
# In production you would install it as a package instead.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "classification"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes.analyze import router as analyze_router
from .routes.health import router as health_router

app = FastAPI(
    title="US LI-RADS Classifier",
    description="Prototype ultrasound LI-RADS surveillance classification API",
    version=settings.app_version,
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
