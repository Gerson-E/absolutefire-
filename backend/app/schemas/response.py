"""
API response schemas (Pydantic v2).

Owner: Owner 2 — Backend

These schemas define exactly what the frontend receives.
Match shared/api-contract.md — do not change field names without
updating the contract and notifying Owner 1.
"""

from typing import Optional
from pydantic import BaseModel


class LargestObservationOut(BaseModel):
    present: bool
    label: Optional[str] = None
    confidence: Optional[float] = None
    size_px: Optional[float] = None
    size_mm: Optional[float] = None


class DetectionOut(BaseModel):
    label: str
    confidence: float
    bbox_xywh: list[float]


class AnalyzeResponse(BaseModel):
    result_id: str
    classification: str
    reasoning: list[str]
    largest_observation: LargestObservationOut
    detections: list[DetectionOut]
    annotated_image_url: Optional[str] = None
    warnings: list[str]
