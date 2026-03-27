# Roboflow API Reference

## Credentials

| Field | Value |
|-------|-------|
| API URL | `https://serverless.roboflow.com` |
| API Key | `6UIDNVJSQVDLFnH069EW` |
| Model ID | `liver_ultrasound/10` |

## SDK Usage

```python
from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="6UIDNVJSQVDLFnH069EW"
)

result = CLIENT.infer("your_image.jpg", model_id="liver_ultrasound/10")
```

## Sample Output

```json
{
  "predictions": [
    {
      "x": 65,
      "y": 95,
      "width": 72,
      "height": 48,
      "confidence": 0.555,
      "class": "HCC",
      "class_id": 0,
      "detection_id": "8cd896d6-ef61-40b3-8b0e-8c07b915ec0f"
    }
  ]
}
```

- `x`, `y` — **center** of bounding box (pixels)
- `width`, `height` — bounding box dimensions (pixels)
- `size_mm = max(width, height) / px_per_mm`

## All Model Labels

| Label | Meaning | Used? |
|-------|---------|-------|
| `HCC` | Hepatocellular carcinoma lesion | **YES — only suspicious label** |
| `0` | Unknown/background | No |
| `HV` | Hepatic vein | No |
| `IVC` | Inferior vena cava | No |
| `K` | Kidney | No |
| `K-C` | Kidney (coronal) | No |
| `K-M` | Kidney (mid) | No |
| `LT SAG` | Left sagittal view | No |
| `LVR` | Liver | No |
| `PV` | Portal vein | No |
| `RT TRANS` | Right transverse view | No |
| `SAG` | Sagittal view | No |
| `SAG K` | Sagittal kidney | No |
| `TRANS` | Transverse view | No |

## Classification Logic (constants.py)

```python
SUSPICIOUS_LABELS = frozenset({"HCC"})
CONFIDENCE_THRESHOLD = 0.30
SIZE_THRESHOLD_MM = 10.0
```

- **US-1:** No HCC detection above confidence threshold
- **US-2:** HCC detected AND `size_mm < 10`
- **US-3:** HCC detected AND `size_mm >= 10`, or `px_per_mm` unavailable
