"""
POST /api/analyze-ultrasound

Owner: Owner 2 — Backend

Orchestrates: file validation → Roboflow inference → normalization →
classification → response assembly.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..schemas.internal import normalize_detections
from ..schemas.response import AnalyzeResponse, DetectionOut, LargestObservationOut
from ..services.roboflow_client import RoboflowClient, RoboflowError
from ..utils.file_validation import validate_image_upload

# Import classification module (path added in main.py)
from classifier.models import InternalDetection
from classifier.rules import classify

router = APIRouter()
_roboflow = RoboflowClient()


@router.post("/analyze-ultrasound", response_model=AnalyzeResponse)
async def analyze_ultrasound(
    image: UploadFile = File(..., description="Liver ultrasound image (JPEG/PNG/WEBP)"),
    px_per_mm: Optional[float] = Form(
        default=None,
        description="Physical calibration factor (pixels per mm). "
                    "If omitted, size_mm will be null.",
        gt=0,
    ),
) -> AnalyzeResponse:
    # 1. Validate uploaded file
    image_bytes = await image.read()
    validate_image_upload(image.filename or "", image.content_type or "", image_bytes)

    # 2. Run Roboflow inference
    try:
        raw_response = await _roboflow.infer(image_bytes, filename=image.filename or "image.jpg")
    except RoboflowError as exc:
        raise HTTPException(status_code=502, detail=f"Roboflow inference failed: {exc}")

    # 3. Normalize raw vendor payload → InternalDetection[]
    detections: list[InternalDetection] = normalize_detections(raw_response)

    # 4. Classify
    result = classify(detections, px_per_mm=px_per_mm)

    # 5. Assemble response
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
        annotated_image_url=None,   # placeholder for future artifact storage
        warnings=result.warnings,
    )
