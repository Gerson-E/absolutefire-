# API Contract — US LI-RADS Classifier

> **FROZEN after Day 1 review.**
> Changes require team sign-off. This is the single source of truth for
> Frontend ↔ Backend communication.

---

## Endpoints

### POST /api/analyze-ultrasound

Analyzes a liver ultrasound image and returns a US LI-RADS classification.

**Request**

```
Content-Type: multipart/form-data

Fields:
  image          (required) JPEG / PNG / WEBP ultrasound image, max 20 MB
  px_per_mm      (optional) float — physical calibration factor.
                             If omitted, size_mm will be null and a warning
                             is included in the response.
```

**Response 200**

```json
{
  "result_id": "string (uuid4)",
  "classification": "US-1 | US-2 | US-3",
  "reasoning": ["string", "..."],
  "largest_observation": {
    "present": false,
    "label": null,
    "confidence": null,
    "size_px": null,
    "size_mm": null
  },
  "detections": [
    {
      "label": "string",
      "confidence": 0.0,
      "bbox_xywh": [0.0, 0.0, 0.0, 0.0]
    }
  ],
  "annotated_image_url": "string | null",
  "warnings": ["string", "..."]
}
```

`largest_observation` when a suspicious finding is present:

```json
{
  "present": true,
  "label": "HCC",
  "confidence": 0.87,
  "size_px": 42.1,
  "size_mm": null
}
```

`size_mm` is `null` unless `px_per_mm` was provided in the request.

**Response 400** — invalid file type or missing image

```json
{ "detail": "string" }
```

**Response 422** — validation error

```json
{ "detail": [{ "loc": ["..."], "msg": "string", "type": "string" }] }
```

**Response 502** — Roboflow inference failure

```json
{ "detail": "Roboflow inference failed: <reason>" }
```

---

### GET /api/health

**Response 200**

```json
{ "status": "ok", "version": "0.1.0" }
```

---

## Classification rules (v1)

| Condition | Class |
|---|---|
| No suspicious observation detected | US-1 |
| Suspicious detected, size_mm < 10 | US-2 |
| Suspicious detected, size_mm ≥ 10 | US-3 |
| Suspicious detected, size_mm unavailable | US-3 + warning |

Conservative fallback: when mm calibration is absent, the system defaults to
US-3 to avoid under-staging. This is explicitly called out in `warnings[]`.

---

## Field definitions

See `shared/glossary.md`.
