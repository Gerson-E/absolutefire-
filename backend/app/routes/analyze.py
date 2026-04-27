"""
POST /api/analyze-ultrasound

Owner: Owner 2 — Backend

Orchestrates the full analysis pipeline:
  1. Validate uploaded image (type, size, decodability)
  2. Send image to Roboflow for object-detection inference
  3. Normalize raw vendor payload → InternalDetection[]
  4. Run the US LI-RADS classification rules engine
  5. Assemble and return the AnalyzeResponse
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..schemas.internal import normalize_detections
from ..schemas.response import AnalyzeResponse, DetectionOut, LargestObservationOut
from ..services.roboflow_client import RoboflowClient, RoboflowError
from ..utils.file_validation import validate_image_upload

from classifier.models import InternalDetection
from classifier.rules import classify

logger = logging.getLogger(__name__)

router = APIRouter()

# Shared client instance — lifecycle managed by the FastAPI lifespan in main.py
roboflow_client = RoboflowClient()


@router.post("/analyze-ultrasound", response_model=AnalyzeResponse)
async def analyze_ultrasound(
    image: UploadFile = File(
        ..., description="Liver ultrasound image (JPEG/PNG/WEBP, max 20 MB)"
    ),
    px_per_mm: Optional[float] = Form(
        default=None,
        description=(
            "Physical calibration factor (pixels per mm). "
            "If omitted, size_mm will be null and classification "
            "conservatively defaults to US-3 when a suspicious "
            "observation is present."
        ),
        gt=0,
    ),
    observation_size_px: Optional[float] = Form(
        default=None,
        description=(
            "Manually measured longest dimension of the confirmed tumor "
            "in pixels. When provided, Roboflow inference is skipped and "
            "this value is used directly for LI-RADS size classification."
        ),
        gt=0,
    ),
) -> AnalyzeResponse:
    # ── 1. Validate uploaded file ────────────────────────────────────────
    image_bytes = await image.read()
    validate_image_upload(
        filename=image.filename or "",
        content_type=image.content_type or "",
        image_bytes=image_bytes,
    )
    logger.info(
        "Image validated: %s (%d bytes, %s)",
        image.filename,
        len(image_bytes),
        image.content_type,
    )

    # ── 2. Build detections ──────────────────────────────────────────────
    if observation_size_px is not None:
        # Manual mode: confirmed tumor, skip Roboflow
        logger.info(
            "Manual observation_size_px=%.1f provided — skipping Roboflow",
            observation_size_px,
        )
        detections: list[InternalDetection] = [
            InternalDetection(
                label="hcc",
                confidence=1.0,
                bbox_xywh=[0.0, 0.0, observation_size_px, observation_size_px],
            )
        ]
    else:
        # Auto mode: run Roboflow inference
        try:
            raw_response = await roboflow_client.infer(
                image_bytes, filename=image.filename or "image.jpg"
            )
        except RoboflowError as exc:
            logger.error("Roboflow inference failed: %s", exc)
            raise HTTPException(
                status_code=502,
                detail=f"Roboflow inference failed: {exc}",
            )

        try:
            detections = normalize_detections(raw_response)
        except ValueError as exc:
            logger.error("Normalization failed: %s", exc)
            raise HTTPException(
                status_code=502,
                detail=f"Roboflow returned malformed data: {exc}",
            )

    logger.info("Normalized %d detection(s)", len(detections))

    # ── 4. Classify ──────────────────────────────────────────────────────
    result = classify(detections, px_per_mm=px_per_mm)
    logger.info(
        "Classification: %s (observations: %s)",
        result.us_class,
        result.largest_observation.present if result.largest_observation else False,
    )

    # ── 5. Assemble response ─────────────────────────────────────────────
    obs = result.largest_observation
    largest_out = LargestObservationOut(
        present=obs.present if obs else False,
        label=obs.label if obs else None,
        confidence=obs.confidence if obs else None,
        size_px=obs.size_px if obs else None,
        size_mm=obs.size_mm if obs else None,
    )

    detections_out = [
        DetectionOut(
            label=d.label,
            confidence=d.confidence,
            bbox_xywh=d.bbox_xywh,
        )
        for d in detections
    ]

    return AnalyzeResponse(
        result_id=str(uuid.uuid4()),
        classification=result.us_class,
        reasoning=result.reasoning,
        largest_observation=largest_out,
        detections=detections_out,
        annotated_image_url=None,
        warnings=result.warnings,
    )
