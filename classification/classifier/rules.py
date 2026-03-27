"""
US LI-RADS surveillance classification rules engine.

Owner: Owner 3 — Classification

Rules (v1):
  US-1 — No suspicious observation detected
  US-2 — Suspicious observation detected, size_mm < 10
  US-3 — Suspicious observation detected, size_mm >= 10
         OR suspicious detected but mm calibration unavailable (conservative)

This is the single public entry point for classification:
  classify(detections, px_per_mm) → ClassificationResult
"""

from typing import Optional

from .constants import CLASSIFIER_VERSION, CONFIDENCE_THRESHOLD, SIZE_THRESHOLD_MM
from .features import extract_largest_observation, filter_by_confidence
from .models import ClassificationResult, InternalDetection, LargestObservation

_PROTO_WARNING = "Prototype only — not validated for clinical use"
_NO_CALIBRATION_WARNING = (
    "No physical mm calibration provided; size_mm is unavailable"
)
_CONSERVATIVE_WARNING = (
    "Conservative US-3 assigned: suspicious observation present "
    "but size cannot be confirmed without mm calibration"
)


def classify(
    detections: list[InternalDetection],
    px_per_mm: Optional[float] = None,
) -> ClassificationResult:
    """
    Apply the US LI-RADS v1 rules engine.

    Args:
        detections: Raw (unfiltered) list of InternalDetection from the backend.
        px_per_mm:  Optional physical calibration factor (pixels per mm).

    Returns:
        ClassificationResult with us_class, reasoning, largest_observation,
        and any warnings.
    """
    warnings: list[str] = [_PROTO_WARNING]
    reasoning: list[str] = []

    # Step 1: filter low-confidence detections
    filtered = filter_by_confidence(detections, CONFIDENCE_THRESHOLD)
    dropped = len(detections) - len(filtered)
    if dropped > 0:
        reasoning.append(
            f"{dropped} detection(s) dropped below confidence threshold "
            f"({CONFIDENCE_THRESHOLD})"
        )

    # Step 2: extract largest suspicious observation
    obs: LargestObservation = extract_largest_observation(filtered, px_per_mm)

    # Step 3: apply classification rules
    if not obs.present:
        us_class = "US-1"
        reasoning.append("No suspicious observations detected above confidence threshold")
    elif obs.size_mm is not None:
        if obs.size_mm < SIZE_THRESHOLD_MM:
            us_class = "US-2"
            reasoning.append(
                f"Suspicious observation detected (label: {obs.label}, "
                f"confidence: {obs.confidence:.2f})"
            )
            reasoning.append(
                f"Largest suspicious observation is {obs.size_mm} mm "
                f"— below {SIZE_THRESHOLD_MM} mm threshold"
            )
        else:
            us_class = "US-3"
            reasoning.append(
                f"Suspicious observation detected (label: {obs.label}, "
                f"confidence: {obs.confidence:.2f})"
            )
            reasoning.append(
                f"Largest suspicious observation is {obs.size_mm} mm "
                f"— at or above {SIZE_THRESHOLD_MM} mm threshold"
            )
    else:
        # Suspicious detected but no mm calibration — conservative fallback
        us_class = "US-3"
        reasoning.append(
            f"Suspicious observation detected (label: {obs.label}, "
            f"confidence: {obs.confidence:.2f})"
        )
        reasoning.append(
            f"Largest suspicious observation is {obs.size_px} px "
            f"(mm size unavailable)"
        )
        warnings.append(_NO_CALIBRATION_WARNING)
        warnings.append(_CONSERVATIVE_WARNING)

    return ClassificationResult(
        us_class=us_class,
        reasoning=reasoning,
        largest_observation=obs,
        warnings=warnings,
    )
