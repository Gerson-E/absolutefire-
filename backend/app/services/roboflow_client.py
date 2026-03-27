"""
Roboflow inference client.

Owner: Owner 2 — Backend

Wraps the Roboflow hosted inference API. Returns raw parsed JSON.
All knowledge of Roboflow's API format lives here and in internal.py.
"""

import httpx

from ..config import settings


class RoboflowError(Exception):
    """Raised when the Roboflow API returns an error or is unreachable."""


class RoboflowClient:
    """
    Thin async wrapper around the Roboflow inference REST API.

    Usage:
        client = RoboflowClient()
        raw = await client.infer(image_bytes, filename="scan.jpg")
    """

    def __init__(self) -> None:
        self._model_url = settings.roboflow_model_url
        self._api_key = settings.roboflow_api_key
        self._timeout = settings.roboflow_timeout

    async def infer(self, image_bytes: bytes, filename: str = "image.jpg") -> dict:
        """
        Submit image bytes to Roboflow for inference.

        Args:
            image_bytes: Raw image file contents.
            filename:    Original filename (used to set Content-Disposition).

        Returns:
            Parsed Roboflow JSON response dict.

        Raises:
            RoboflowError: On HTTP error, timeout, or unparseable response.
        """
        if not self._model_url or not self._api_key:
            raise RoboflowError(
                "ROBOFLOW_MODEL_URL and ROBOFLOW_API_KEY must be set in .env"
            )

        url = f"{self._model_url.rstrip('/')}?api_key={self._api_key}"

        # Roboflow accepts multipart/form-data with the image as 'file'
        files = {"file": (filename, image_bytes, _guess_content_type(filename))}

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, files=files)
        except httpx.TimeoutException as exc:
            raise RoboflowError(f"Request timed out after {self._timeout}s") from exc
        except httpx.RequestError as exc:
            raise RoboflowError(f"Network error: {exc}") from exc

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "unknown")
            raise RoboflowError(
                f"Roboflow rate limit exceeded. Retry after {retry_after}s."
            )

        if response.status_code != 200:
            raise RoboflowError(
                f"Roboflow returned HTTP {response.status_code}: {response.text[:200]}"
            )

        try:
            return response.json()
        except Exception as exc:
            raise RoboflowError(f"Could not parse Roboflow response as JSON: {exc}") from exc


def _guess_content_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }.get(ext, "application/octet-stream")
