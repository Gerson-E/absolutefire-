"""
Tests for the Roboflow normalization layer (internal.py).

Owner: Owner 2 — Backend

These tests do NOT make real HTTP calls to Roboflow.
They only test normalize_detections() with fixture data.
"""

import json
import os
import sys

import pytest

# Add classification to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "classification"))
# Add backend app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.schemas.internal import normalize_detections, _bbox_from_points


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name: str) -> dict:
    with open(os.path.join(FIXTURES_DIR, name)) as f:
        return json.load(f)


class TestNormalizeDetections:
    def test_standard_detection_response(self):
        raw = load_fixture("sample_roboflow_response.json")
        detections = normalize_detections(raw)
        assert len(detections) == 2

        hcc = next(d for d in detections if d.label == "HCC")
        assert hcc.confidence == pytest.approx(0.87)
        assert hcc.bbox_xywh == pytest.approx([320.5, 240.3, 45.2, 38.1])

    def test_empty_predictions(self):
        raw = {"predictions": []}
        assert normalize_detections(raw) == []

    def test_missing_predictions_key(self):
        assert normalize_detections({}) == []

    def test_non_dict_input_raises(self):
        with pytest.raises(ValueError):
            normalize_detections("not a dict")  # type: ignore

    def test_prediction_missing_confidence_is_skipped(self):
        raw = {
            "predictions": [
                {"x": 10, "y": 10, "width": 5, "height": 5, "class": "HCC"},
            ]
        }
        assert normalize_detections(raw) == []

    def test_prediction_missing_bbox_but_has_points(self):
        raw = {
            "predictions": [
                {
                    "class": "lesion",
                    "confidence": 0.7,
                    "points": [
                        {"x": 100, "y": 100},
                        {"x": 150, "y": 100},
                        {"x": 150, "y": 140},
                        {"x": 100, "y": 140},
                    ],
                }
            ]
        }
        detections = normalize_detections(raw)
        assert len(detections) == 1
        d = detections[0]
        assert d.label == "lesion"
        assert d.bbox_xywh[2] == pytest.approx(50.0)  # width
        assert d.bbox_xywh[3] == pytest.approx(40.0)  # height

    def test_prediction_missing_both_bbox_and_points_is_skipped(self):
        raw = {
            "predictions": [
                {"class": "HCC", "confidence": 0.9},
            ]
        }
        assert normalize_detections(raw) == []

    def test_label_from_class_field(self):
        raw = {
            "predictions": [
                {"x": 1, "y": 1, "width": 10, "height": 10, "confidence": 0.5, "class": "nodule"}
            ]
        }
        detections = normalize_detections(raw)
        assert detections[0].label == "nodule"


class TestBboxFromPoints:
    def test_basic_rectangle(self):
        points = [
            {"x": 10, "y": 20},
            {"x": 60, "y": 20},
            {"x": 60, "y": 70},
            {"x": 10, "y": 70},
        ]
        x, y, w, h = _bbox_from_points(points)
        assert x == pytest.approx(35.0)
        assert y == pytest.approx(45.0)
        assert w == pytest.approx(50.0)
        assert h == pytest.approx(50.0)

    def test_empty_points_returns_none(self):
        assert _bbox_from_points([]) is None

    def test_malformed_points_returns_none(self):
        assert _bbox_from_points([{"bad": 1}]) is None
