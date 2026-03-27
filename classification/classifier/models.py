"""
Data models for the classification module.

Owner: Owner 3 — Classification

NOTE: InternalDetection here mirrors backend/app/schemas/internal.py.
If the backend schema changes, this file must be updated to match.
Coordinate with Owner 2 before making breaking changes.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class InternalDetection:
    """
    Normalized representation of a single detection from Roboflow.
    Created by the backend normalization layer; consumed by classification.
    """
    label: str
    confidence: float
    # [x_center, y_center, width, height] in pixels
    bbox_xywh: list[float]


@dataclass
class LargestObservation:
    """Details of the largest suspicious observation found, or absence thereof."""
    present: bool
    label: Optional[str] = None
    confidence: Optional[float] = None
    size_px: Optional[float] = None   # longest bbox dimension in pixels
    size_mm: Optional[float] = None   # None unless px_per_mm calibration provided


@dataclass
class ClassificationResult:
    """Output of the classification rules engine."""
    us_class: str                        # "US-1" | "US-2" | "US-3"
    reasoning: list[str] = field(default_factory=list)
    largest_observation: Optional[LargestObservation] = None
    warnings: list[str] = field(default_factory=list)
