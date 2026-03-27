"""
Classification constants.

Owner: Owner 3 — Classification
"""

# Labels that are treated as suspicious observations.
# Must match the class names your Roboflow model produces (case-insensitive).
SUSPICIOUS_LABELS: frozenset[str] = frozenset({
    "hcc",
})

# Detections below this confidence threshold are ignored.
CONFIDENCE_THRESHOLD: float = 0.30

# LI-RADS size threshold in mm (longest dimension).
# Observations >= this value → US-3; below → US-2.
SIZE_THRESHOLD_MM: float = 10.0

# App version surfaced in classification result metadata.
CLASSIFIER_VERSION: str = "0.1.0"
