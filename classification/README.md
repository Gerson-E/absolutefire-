# classification/

Owner: **Owner 3 — Classification**

Pure Python module. No FastAPI. No network calls. Fully testable in isolation.

## Public API

```python
from classifier.rules import classify
from classifier.models import InternalDetection, ClassificationResult

detections = [
    InternalDetection(label="HCC", confidence=0.87, bbox_xywh=[320, 240, 45, 38])
]

result: ClassificationResult = classify(detections, px_per_mm=3.5)
print(result.us_class)   # "US-3"
print(result.reasoning)
print(result.warnings)
```

## Folder structure

```
classifier/
  __init__.py       package entry
  constants.py      SUSPICIOUS_LABELS, thresholds, version
  models.py         InternalDetection, LargestObservation, ClassificationResult
  features.py       feature extraction (filter, suspicious check, size)
  rules.py          US-1/2/3 rules engine — main entry point
tests/
  test_features.py
  test_rules.py
  fixtures/
    sample_detections.json
```

## Run tests

```bash
cd classification
pytest tests/ -v
```

## Configuration

Adjust `classifier/constants.py` to:
- Add/remove suspicious label names to match your Roboflow model
- Change the confidence threshold (default 0.30)
- Change the size threshold (default 10.0 mm)

## Extension points

- `px_per_mm` is an optional parameter in `classify()`. Pass it when physical
  calibration is available (e.g., from DICOM spacing metadata).
- Add mask area calculation in `features.py` when segmentation masks are available.
- Add multi-feature logic in `rules.py` for future LI-RADS features.
