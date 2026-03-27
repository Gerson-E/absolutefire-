"""
Unit tests for classification/classifier/features.py

Owner: Owner 3 — Classification
"""

import pytest
from classifier.features import (
    extract_largest_observation,
    filter_by_confidence,
    is_suspicious,
    longest_dimension_px,
)
from classifier.models import InternalDetection


# ── helpers ──────────────────────────────────────────────────────────────────

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


# ── is_suspicious ─────────────────────────────────────────────────────────────

class TestIsSuspicious:
    def test_known_suspicious_labels(self):
        for label in ["HCC", "hcc"]:
            assert is_suspicious(make_detection(label, 0.9)), f"{label} should be suspicious"

    def test_non_suspicious_labels(self):
        for label in ["liver", "vessel", "artifact", "background", "lesion", "nodule", "K", "LVR", "PV"]:
            assert not is_suspicious(make_detection(label, 0.9)), f"{label} should not be suspicious"


# ── longest_dimension_px ──────────────────────────────────────────────────────

class TestLongestDimension:
    def test_width_larger(self):
        d = make_detection("HCC", 0.9, w=50.0, h=30.0)
        assert longest_dimension_px(d) == 50.0

    def test_height_larger(self):
        d = make_detection("HCC", 0.9, w=20.0, h=45.0)
        assert longest_dimension_px(d) == 45.0

    def test_equal_dimensions(self):
        d = make_detection("HCC", 0.9, w=25.0, h=25.0)
        assert longest_dimension_px(d) == 25.0


# ── filter_by_confidence ──────────────────────────────────────────────────────

class TestFilterByConfidence:
    def test_filters_below_threshold(self):
        detections = [
            make_detection("HCC", 0.9),
            make_detection("nodule", 0.2),
            make_detection("lesion", 0.3),
        ]
        result = filter_by_confidence(detections, threshold=0.3)
        assert len(result) == 2
        assert all(d.confidence >= 0.3 for d in result)

    def test_empty_input(self):
        assert filter_by_confidence([]) == []

    def test_all_filtered(self):
        detections = [make_detection("HCC", 0.1), make_detection("lesion", 0.05)]
        assert filter_by_confidence(detections, threshold=0.5) == []

    def test_none_filtered(self):
        detections = [make_detection("HCC", 0.8), make_detection("lesion", 0.95)]
        assert len(filter_by_confidence(detections, threshold=0.3)) == 2


# ── extract_largest_observation ───────────────────────────────────────────────

class TestExtractLargestObservation:
    def test_no_detections_returns_absent(self):
        obs = extract_largest_observation([])
        assert obs.present is False
        assert obs.label is None

    def test_no_suspicious_returns_absent(self):
        detections = [make_detection("liver", 0.9), make_detection("vessel", 0.8)]
        obs = extract_largest_observation(detections)
        assert obs.present is False

    def test_returns_largest_suspicious(self):
        detections = [
            make_detection("HCC", 0.87, w=45.0, h=38.0),
            make_detection("HCC", 0.55, w=12.0, h=11.0),
        ]
        obs = extract_largest_observation(detections)
        assert obs.present is True
        assert obs.label == "HCC"
        assert obs.size_px == 45.0

    def test_size_mm_computed_when_calibrated(self):
        detections = [make_detection("HCC", 0.87, w=35.0, h=20.0)]
        obs = extract_largest_observation(detections, px_per_mm=3.5)
        assert obs.size_mm == pytest.approx(10.0, rel=1e-2)

    def test_size_mm_none_without_calibration(self):
        detections = [make_detection("HCC", 0.87, w=35.0, h=20.0)]
        obs = extract_largest_observation(detections, px_per_mm=None)
        assert obs.size_mm is None

    def test_ignores_zero_px_per_mm(self):
        detections = [make_detection("HCC", 0.87, w=35.0, h=20.0)]
        obs = extract_largest_observation(detections, px_per_mm=0)
        assert obs.size_mm is None
