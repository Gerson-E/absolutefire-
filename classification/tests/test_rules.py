"""
Unit tests for classification/classifier/rules.py

Owner: Owner 3 — Classification
"""

import pytest
from classifier.models import InternalDetection
from classifier.rules import classify


# ── helpers ───────────────────────────────────────────────────────────────────

def make_detection(
    label: str,
    confidence: float,
    w: float = 20.0,
    h: float = 15.0,
) -> InternalDetection:
    return InternalDetection(
        label=label,
        confidence=confidence,
        bbox_xywh=[100.0, 100.0, w, h],
    )


# ── US-1 ──────────────────────────────────────────────────────────────────────

class TestUS1:
    def test_empty_detections(self):
        result = classify([])
        assert result.us_class == "US-1"
        assert result.largest_observation.present is False

    def test_only_non_suspicious_detections(self):
        detections = [make_detection("liver", 0.9), make_detection("vessel", 0.85)]
        result = classify(detections)
        assert result.us_class == "US-1"

    def test_all_detections_below_confidence(self):
        detections = [make_detection("HCC", 0.1), make_detection("lesion", 0.05)]
        result = classify(detections)
        assert result.us_class == "US-1"


# ── US-2 ──────────────────────────────────────────────────────────────────────

class TestUS2:
    def test_suspicious_below_threshold_mm(self):
        # 3.5 px/mm × 9 px = 2.57 mm → US-2
        detections = [make_detection("HCC", 0.87, w=9.0, h=8.0)]
        result = classify(detections, px_per_mm=3.5)
        assert result.us_class == "US-2"
        assert result.largest_observation.present is True
        assert result.largest_observation.size_mm < 10.0

    def test_suspicious_exactly_below_threshold(self):
        # 10 px / (1.02 px/mm) ≈ 9.8 mm → US-2
        detections = [make_detection("HCC", 0.9, w=10.0, h=5.0)]
        result = classify(detections, px_per_mm=1.02)
        assert result.us_class == "US-2"

    def test_reasoning_mentions_label(self):
        detections = [make_detection("HCC", 0.6, w=9.0, h=9.0)]
        result = classify(detections, px_per_mm=3.5)
        assert result.us_class == "US-2"
        assert any("hcc" in r.lower() for r in result.reasoning)


# ── US-3 ──────────────────────────────────────────────────────────────────────

class TestUS3:
    def test_suspicious_at_threshold_mm(self):
        # 35 px / 3.5 px/mm = 10.0 mm → US-3
        detections = [make_detection("HCC", 0.87, w=35.0, h=20.0)]
        result = classify(detections, px_per_mm=3.5)
        assert result.us_class == "US-3"

    def test_suspicious_above_threshold_mm(self):
        detections = [make_detection("HCC", 0.87, w=80.0, h=60.0)]
        result = classify(detections, px_per_mm=3.5)
        assert result.us_class == "US-3"
        assert result.largest_observation.size_mm >= 10.0

    def test_suspicious_without_calibration_defaults_to_us3(self):
        """Conservative fallback: no mm data → US-3 with warnings."""
        detections = [make_detection("HCC", 0.87, w=45.0, h=38.0)]
        result = classify(detections, px_per_mm=None)
        assert result.us_class == "US-3"
        assert result.largest_observation.size_mm is None
        assert any("calibration" in w.lower() for w in result.warnings)

    def test_reasoning_mentions_size_mm(self):
        detections = [make_detection("HCC", 0.9, w=50.0, h=40.0)]
        result = classify(detections, px_per_mm=2.0)
        assert result.us_class == "US-3"
        assert any("mm" in r for r in result.reasoning)


# ── general ───────────────────────────────────────────────────────────────────

class TestGeneral:
    def test_prototype_warning_always_present(self):
        result = classify([])
        assert any("prototype" in w.lower() for w in result.warnings)

    def test_multiple_detections_uses_largest(self):
        detections = [
            make_detection("HCC", 0.9, w=80.0, h=70.0),  # larger
            make_detection("HCC", 0.6, w=12.0, h=10.0),  # smaller
        ]
        result = classify(detections, px_per_mm=3.5)
        assert result.largest_observation.size_px == 80.0

    def test_low_confidence_detections_noted_in_reasoning(self):
        detections = [
            make_detection("HCC", 0.9),
            make_detection("HCC", 0.05),  # below threshold
        ]
        result = classify(detections)
        assert any("dropped" in r.lower() for r in result.reasoning)

    def test_classification_result_has_all_fields(self):
        result = classify([])
        assert result.us_class
        assert isinstance(result.reasoning, list)
        assert result.largest_observation is not None
        assert isinstance(result.warnings, list)
