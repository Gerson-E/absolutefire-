"""
Internal normalization layer.

Owner: Owner 2 — Backend

Converts raw Roboflow JSON into InternalDetection objects.
This is the ONLY place in the codebase that knows about Roboflow's
payload structure.

NOTE: InternalDetection is defined in classification/classifier/models.py
and mirrored here by import. If the model changes, coordinate with Owner 3.
"""

import sys
import os

# Allow importing classification module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "classification"))

from classifier.models import InternalDetection


def normalize_detections(raw: dict) -> list[InternalDetection]:
    """
    Normalize a raw Roboflow inference response into InternalDetection objects.

    Handles:
    - Standard object-detection response (predictions[].x/y/width/height)
    - Missing predictions key → empty list
    - Predictions missing required fields → skipped with no crash
    - Segmentation models with points[] → bbox computed from point extents

    Args:
        raw: The parsed JSON dict from Roboflow's inference API.

    Returns:
        List of InternalDetection. May be empty.

    Raises:
        ValueError: If raw is not a dict (malformed response).
    """
    if not isinstance(raw, dict):
        raise ValueError(f"Expected dict from Roboflow, got {type(raw).__name__}")

    predictions = raw.get("predictions", [])
    if not isinstance(predictions, list):
        return []

    detections: list[InternalDetection] = []

    for pred in predictions:
        if not isinstance(pred, dict):
            continue

        label = pred.get("class") or pred.get("label") or ""
        confidence = pred.get("confidence")
        if confidence is None:
            continue

        # Standard detection bbox (center-based x/y + w/h)
        x = pred.get("x")
        y = pred.get("y")
        w = pred.get("width")
        h = pred.get("height")

        if None in (x, y, w, h):
            # Try to derive bbox from segmentation points if available
            points = pred.get("points")
            if points:
                bbox = _bbox_from_points(points)
                if bbox is None:
                    continue
                x, y, w, h = bbox
            else:
                continue

        detections.append(
            InternalDetection(
                label=str(label),
                confidence=float(confidence),
                bbox_xywh=[float(x), float(y), float(w), float(h)],
            )
        )

    return detections


def _bbox_from_points(points: list[dict]) -> tuple[float, float, float, float] | None:
    """
    Compute a bounding box from a list of segmentation point dicts.
    Each point has 'x' and 'y' keys.
    Returns (x_center, y_center, width, height) or None if invalid.
    """
    try:
        xs = [float(p["x"]) for p in points]
        ys = [float(p["y"]) for p in points]
    except (KeyError, TypeError, ValueError):
        return None

    if not xs or not ys:
        return None

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    w = max_x - min_x
    h = max_y - min_y
    x_center = min_x + w / 2
    y_center = min_y + h / 2
    return x_center, y_center, w, h
