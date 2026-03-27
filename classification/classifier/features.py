"""
Feature extraction from a list of InternalDetections.

Owner: Owner 3 — Classification

Responsibilities:
- Filter detections by confidence threshold
- Identify which detections are "suspicious"
- Extract the largest suspicious observation (by longest bbox dimension)
- Compute size in mm if calibration is provided
"""

from typing import Optional

from .constants import CONFIDENCE_THRESHOLD, SUSPICIOUS_LABELS
from .models import InternalDetection, LargestObservation


def is_suspicious(detection: InternalDetection) -> bool:
    """Return True if the detection label is in the suspicious label set."""
    return detection.label.lower() in SUSPICIOUS_LABELS


def longest_dimension_px(detection: InternalDetection) -> float:
    """
    Return the longest dimension of the bounding box in pixels.
    bbox_xywh = [x_center, y_center, width, height]
    """
    _, _, w, h = detection.bbox_xywh
    return max(w, h)


def filter_by_confidence(
    detections: list[InternalDetection],
    threshold: float = CONFIDENCE_THRESHOLD,
) -> list[InternalDetection]:
    """Drop detections below the confidence threshold."""
    return [d for d in detections if d.confidence >= threshold]


def extract_largest_observation(
    detections: list[InternalDetection],
    px_per_mm: Optional[float] = None,
) -> LargestObservation:
    """
    From a list of already-filtered detections, find the largest suspicious
    observation and return its details.

    Args:
        detections: Confidence-filtered InternalDetection list.
        px_per_mm:  Physical calibration factor. If None, size_mm will be None.

    Returns:
        LargestObservation — present=False if no suspicious detection found.
    """
    suspicious = [d for d in detections if is_suspicious(d)]

    if not suspicious:
        return LargestObservation(present=False)

    largest = max(suspicious, key=longest_dimension_px)
    size_px = longest_dimension_px(largest)
    size_mm = (size_px / px_per_mm) if px_per_mm and px_per_mm > 0 else None

    return LargestObservation(
        present=True,
        label=largest.label,
        confidence=largest.confidence,
        size_px=round(size_px, 2),
        size_mm=round(size_mm, 2) if size_mm is not None else None,
    )
