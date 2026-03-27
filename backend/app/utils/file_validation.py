"""
Upload file validation.

Owner: Owner 2 — Backend
"""

from fastapi import HTTPException
from PIL import Image
import io

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


def validate_image_upload(
    filename: str,
    content_type: str,
    image_bytes: bytes,
) -> None:
    """
    Validate an uploaded image file.

    Checks:
    - File size <= 20 MB
    - MIME type is in the allowed set
    - File extension is in the allowed set
    - Bytes are decodable as an image by Pillow

    Raises:
        HTTPException 400 on any validation failure.
    """
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024*1024)} MB.",
        )

    if content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{content_type}'. "
                   f"Allowed: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}",
        )

    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{ext}'. "
                   f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Attempt to decode with Pillow to catch corrupted images
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"File could not be decoded as an image: {exc}",
        )
