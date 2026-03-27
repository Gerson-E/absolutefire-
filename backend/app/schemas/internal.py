"""
Internal normalization layer.

Owner: Owner 2 — Backend

Converts raw Roboflow inference JSON into ``InternalDetection`` objects
consumed by the classification module.  This is the **only** place in
the backend that understands Roboflow's payload structure.

NOTE: ``InternalDetection`` is defined in
``classification/classifier/models.py``.  If the model changes,
coordinate with Owner 3.
"""

from __future__ import annotations

import logging
from typing import Any

from classifier.models import InternalDetection

logger = logging.getLogger(__name__)


def normalize_detections(raw: Any) -> list[InternalDetection]:
    """
    Parse a raw Roboflow inference response into ``InternalDetection`` objects.

    Handles
    -------
    - Standard object-detection payloads (``predictions[].x/y/width/height``)
    - Segmentation models where ``points[]`` is present but bbox fields are
      missing — a bounding box is computed from point extents.
    - Missing ``predictions`` key → empty list.
    - Individual predictions missing required fields → skipped with a warning.

    Parameters
    ----------
    raw : Any
        The parsed JSON value returned by Roboflow.

    Returns
    -------
    list[InternalDetection]
        May be empty if no valid predictions were found.

    Raises
    ------
    ValueError
        If *raw* is not a ``dict`` (completely malformed response).
    """
    if not isinstance(raw, dict):
        raise ValueError(
            f"Expected dict from Roboflow, got {type(raw).__name__}"
        )

    predictions = raw.get("predictions", [])
    if not isinstance(predictions, list):
        logger.warning(
            "Roboflow 'predictions' field is not a list — treating as empty"
        )
        return []

    detections: list[InternalDetection] = []

    for idx, pred in enumerate(predictions):
        if not isinstance(pred, dict):
            logger.warning("Prediction #%d is not a dict — skipping", idx)
            continue

        # Label — Roboflow uses "class"; some models use "label"
        label = pred.get("class") or pred.get("label") or ""
        if not label:
            logger.warning("Prediction #%d has no label — skipping", idx)
            continue

        # Confidence — required
        confidence = pred.get("confidence")
        if confidence is None:
            logger.warning(
                "Prediction #%d (%s) has no confidence — skipping", idx, label
            )
            continue

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            logger.warning(
                "Prediction #%d (%s) has non-numeric confidence — skipping",
                idx,
                label,
            )
            continue

        # Bounding box — try standard fields first, fall back to points
        bbox = _extract_bbox(pred)
        if bbox is None:
            points = pred.get("points")
            if points:
                bbox = _bbox_from_points(points)

        if bbox is None:
            logger.warning(
                "Prediction #%d (%s) has no usable bbox — skipping", idx, label
            )
            continue

        x, y, w, h = bbox

        detections.append(
            InternalDetection(
                label=str(label),
                confidence=confidence,
                bbox_xywh=[x, y, w, h],
            )
        )

    logger.info(
        "Normalized %d / %d predictions into InternalDetections",
        len(detections),
        len(predictions),
    )
    return detections


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_bbox(
    pred: dict[str, Any],
) -> tuple[float, float, float, float] | None:
    """
    Extract (x_center, y_center, width, height) from standard Roboflow
    detection fields.  Returns ``None`` if any field is missing.
    """
    try:
        x = float(pred["x"])
        y = float(pred["y"])
        w = float(pred["width"])
        h = float(pred["height"])
    except (KeyError, TypeError, ValueError):
        return None
    return x, y, w, h


def _bbox_from_points(
    points: list[dict[str, Any]],
) -> tuple[float, float, float, float] | None:
    """
    Compute a bounding box from a list of segmentation point dicts.

    Each point is expected to have ``x`` and ``y`` keys.

    Returns (x_center, y_center, width, height), or ``None`` if the
    points are empty or malformed.
    """
    if not points:
        return None

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
