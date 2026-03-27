"""
Contract / integration tests for POST /api/analyze-ultrasound.

Owner: Owner 2 — Backend

Uses pytest + httpx TestClient. Roboflow calls are mocked — no real API key needed.
"""

import io
import json
import os
import sys
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "classification"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app

client = TestClient(app)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def make_jpeg_bytes(width: int = 64, height: int = 64) -> bytes:
    """Create minimal in-memory JPEG bytes."""
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), color=(128, 128, 128))
    img.save(buf, format="JPEG")
    return buf.getvalue()


def load_fixture(name: str) -> dict:
    with open(os.path.join(FIXTURES_DIR, name)) as f:
        return json.load(f)


MOCK_ROBOFLOW_RESPONSE = load_fixture("sample_roboflow_response.json")
MOCK_EMPTY_RESPONSE = {"predictions": []}


def post_image(image_bytes: bytes, extra_fields: dict | None = None) -> dict:
    files = {"image": ("test.jpg", io.BytesIO(image_bytes), "image/jpeg")}
    data = extra_fields or {}
    response = client.post("/api/analyze-ultrasound", files=files, data=data)
    return response


class TestAnalyzeEndpointContract:
    """Verify that response shape matches the API contract."""

    @patch(
        "app.routes.analyze._roboflow.infer",
        new_callable=AsyncMock,
        return_value=MOCK_ROBOFLOW_RESPONSE,
    )
    def test_response_has_all_required_fields(self, _mock):
        resp = post_image(make_jpeg_bytes())
        assert resp.status_code == 200
        body = resp.json()
        assert "result_id" in body
        assert "classification" in body
        assert "reasoning" in body
        assert "largest_observation" in body
        assert "detections" in body
        assert "annotated_image_url" in body
        assert "warnings" in body

    @patch(
        "app.routes.analyze._roboflow.infer",
        new_callable=AsyncMock,
        return_value=MOCK_ROBOFLOW_RESPONSE,
    )
    def test_classification_is_valid_us_class(self, _mock):
        body = post_image(make_jpeg_bytes()).json()
        assert body["classification"] in ("US-1", "US-2", "US-3")

    @patch(
        "app.routes.analyze._roboflow.infer",
        new_callable=AsyncMock,
        return_value=MOCK_EMPTY_RESPONSE,
    )
    def test_no_detections_returns_us1(self, _mock):
        body = post_image(make_jpeg_bytes()).json()
        assert body["classification"] == "US-1"
        assert body["largest_observation"]["present"] is False

    @patch(
        "app.routes.analyze._roboflow.infer",
        new_callable=AsyncMock,
        return_value=MOCK_ROBOFLOW_RESPONSE,
    )
    def test_warnings_always_present(self, _mock):
        body = post_image(make_jpeg_bytes()).json()
        assert isinstance(body["warnings"], list)
        assert len(body["warnings"]) > 0

    @patch(
        "app.routes.analyze._roboflow.infer",
        new_callable=AsyncMock,
        return_value=MOCK_ROBOFLOW_RESPONSE,
    )
    def test_result_id_is_string(self, _mock):
        body = post_image(make_jpeg_bytes()).json()
        assert isinstance(body["result_id"], str)
        assert len(body["result_id"]) > 0


class TestFileValidation:
    def test_missing_image_returns_422(self):
        resp = client.post("/api/analyze-ultrasound")
        assert resp.status_code == 422

    def test_empty_file_returns_400(self):
        files = {"image": ("empty.jpg", io.BytesIO(b""), "image/jpeg")}
        resp = client.post("/api/analyze-ultrasound", files=files)
        assert resp.status_code == 400

    def test_unsupported_content_type_returns_400(self):
        files = {"image": ("scan.bmp", io.BytesIO(b"fake"), "image/bmp")}
        resp = client.post("/api/analyze-ultrasound", files=files)
        assert resp.status_code == 400

    def test_corrupted_image_returns_400(self):
        files = {"image": ("bad.jpg", io.BytesIO(b"notanimage"), "image/jpeg")}
        resp = client.post("/api/analyze-ultrasound", files=files)
        assert resp.status_code == 400


class TestRoboflowFailure:
    @patch(
        "app.routes.analyze._roboflow.infer",
        new_callable=AsyncMock,
        side_effect=Exception("timeout"),
    )
    def test_roboflow_error_returns_502(self, _mock):
        from app.services.roboflow_client import RoboflowError
        _mock.side_effect = RoboflowError("timeout")
        resp = post_image(make_jpeg_bytes())
        assert resp.status_code == 502
        assert "Roboflow inference failed" in resp.json()["detail"]


class TestHealth:
    def test_health_returns_ok(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
