"""
Roboflow inference client.

Owner: Owner 2 — Backend

Async client that submits ultrasound images to Roboflow's hosted inference
API and returns the raw parsed JSON response.  All knowledge of Roboflow's
REST interface lives in this file.

Design notes
------------
- A single ``httpx.AsyncClient`` is created at startup and reused across
  requests (connection pooling, keep-alive).  Call ``close()`` during
  application shutdown.
- Every public method raises ``RoboflowError`` on failure so the caller
  never has to handle raw HTTP exceptions.
"""

from __future__ import annotations

import base64
import logging
from typing import Any

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


class RoboflowError(Exception):
    """Raised when the Roboflow API returns an error or is unreachable."""


class RoboflowClient:
    """
    Async wrapper around the Roboflow inference REST API.

    Lifecycle
    ---------
    Instantiate once at app startup.  The underlying ``httpx.AsyncClient``
    is lazily created on the first call and **must** be closed via
    ``await client.close()`` at shutdown (handled by the FastAPI lifespan).
    """

    def __init__(self) -> None:
        self._model_url: str = settings.roboflow_model_url
        self._api_key: str = settings.roboflow_api_key
        self._timeout: int = settings.roboflow_timeout
        self._http: httpx.AsyncClient | None = None

    # -- lifecycle -----------------------------------------------------------

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout, connect=10.0),
            )
        return self._http

    async def close(self) -> None:
        """Shut down the underlying HTTP connection pool."""
        if self._http is not None and not self._http.is_closed:
            await self._http.aclose()
            logger.info("Roboflow HTTP client closed")

    # -- public API ----------------------------------------------------------

    async def infer(
        self,
        image_bytes: bytes,
        filename: str = "image.jpg",
    ) -> dict[str, Any]:
        """
        Submit image bytes to Roboflow for object-detection inference.

        Parameters
        ----------
        image_bytes : bytes
            Raw image file contents (JPEG / PNG / WEBP).
        filename : str
            Original filename — used for Content-Disposition and to guess
            the MIME type.

        Returns
        -------
        dict
            Parsed Roboflow JSON response containing ``predictions``.

        Raises
        ------
        RoboflowError
            On missing config, HTTP errors, timeouts, rate-limits, or
            unparseable responses.
        """
        self._validate_config()

        url = f"{self._model_url.rstrip('/')}?api_key={self._api_key}"
        content_type = _guess_content_type(filename)
        files = {"file": (filename, image_bytes, content_type)}

        logger.info(
            "Sending inference request to Roboflow (%d bytes, type=%s)",
            len(image_bytes),
            content_type,
        )

        client = self._ensure_client()

        try:
            response = await client.post(url, files=files)
        except httpx.TimeoutException as exc:
            logger.error("Roboflow request timed out after %ds", self._timeout)
            raise RoboflowError(
                f"Request timed out after {self._timeout}s"
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Roboflow network error: %s", exc)
            raise RoboflowError(f"Network error: {exc}") from exc

        return self._handle_response(response)

    # -- internals -----------------------------------------------------------

    def _validate_config(self) -> None:
        if not self._model_url:
            raise RoboflowError(
                "ROBOFLOW_MODEL_URL is not set — check your .env file"
            )
        if not self._api_key:
            raise RoboflowError(
                "ROBOFLOW_API_KEY is not set — check your .env file"
            )

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Interpret the Roboflow HTTP response and return parsed JSON."""
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "unknown")
            logger.warning("Roboflow rate-limited; retry after %s s", retry_after)
            raise RoboflowError(
                f"Roboflow rate limit exceeded. Retry after {retry_after}s."
            )

        if response.status_code != 200:
            body_preview = response.text[:300]
            logger.error(
                "Roboflow HTTP %d: %s", response.status_code, body_preview
            )
            raise RoboflowError(
                f"Roboflow returned HTTP {response.status_code}: {body_preview}"
            )

        try:
            data = response.json()
        except Exception as exc:
            logger.error("Failed to parse Roboflow JSON: %s", exc)
            raise RoboflowError(
                f"Could not parse Roboflow response as JSON: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise RoboflowError(
                f"Expected JSON object from Roboflow, got {type(data).__name__}"
            )

        pred_count = len(data.get("predictions", []))
        logger.info("Roboflow returned %d prediction(s)", pred_count)
        return data


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _guess_content_type(filename: str) -> str:
    """Map common image extensions to MIME types."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }.get(ext, "application/octet-stream")
