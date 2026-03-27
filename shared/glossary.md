# Glossary

**US LI-RADS** — Ultrasound Liver Imaging Reporting and Data System.
A standardized framework for reporting liver observations on surveillance ultrasound.

**US-1** — Negative. No suspicious observation detected.

**US-2** — Subthreshold. Suspicious observation present but < 10 mm in longest dimension.

**US-3** — Positive. Suspicious observation ≥ 10 mm, or suspicious detected without mm calibration (conservative fallback).

**Suspicious observation** — Any detection whose label is in the configured
SUSPICIOUS_LABELS set (see `classification/classifier/constants.py`).

**bbox_xywh** — Bounding box in [x_center, y_center, width, height] pixel coordinates
as returned by Roboflow. Origin is top-left.

**size_px** — Longest dimension (max of bbox width, bbox height) in pixels.

**size_mm** — Physical size in millimeters. Computed as `size_px / px_per_mm`.
Null unless calibration is provided.

**px_per_mm** — Calibration factor: how many image pixels correspond to 1 mm
in physical space. Typically derived from ultrasound DICOM metadata or a ruler overlay.

**InternalDetection** — Backend-normalized detection schema.
Defined in `backend/app/schemas/internal.py`.
Neither the raw Roboflow payload nor the frontend response shape.
