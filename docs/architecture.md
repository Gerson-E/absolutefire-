# Architecture

## System overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Browser                                                             │
│  frontend/                                                           │
│    UploadForm → lib/api.ts → POST /api/analyze-ultrasound           │
│    ResultCard ← AnalyzeResponse JSON                                 │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ multipart/form-data
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FastAPI  backend/app/                                               │
│                                                                      │
│  routes/analyze.py                                                   │
│    └── validates file                                                │
│    └── calls roboflow_client.run_inference(image_bytes)              │
│    └── calls normalize_detections(raw) → InternalDetection[]        │
│    └── calls classify(detections) → ClassificationResult            │
│    └── builds AnalyzeResponse and returns JSON                       │
└──────────┬──────────────────────────────┬───────────────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐    ┌──────────────────────────────────────────┐
│  Roboflow            │    │  classification/classifier/              │
│  Inference API       │    │    features.py  — extract largest obs    │
│  (external)          │    │    rules.py     — US-1/2/3 engine        │
└──────────────────────┘    └──────────────────────────────────────────┘
```

## Key design decisions

### 1. Single normalization point
Raw Roboflow JSON is converted to `InternalDetection` in
`backend/app/schemas/internal.py` + `roboflow_client.py`.
No other layer ever sees the raw vendor payload.

### 2. Classification is a pure function
`classify(detections: list[InternalDetection]) → ClassificationResult`
lives entirely in `classification/`. It has no FastAPI dependency and
can be tested in isolation with `pytest`.

### 3. Stable cross-module contract
The classification module imports `InternalDetection` from its own
`classification/classifier/models.py` (a mirror of the backend schema).
Both models are kept in sync manually — a deliberate simplicity trade-off
that avoids a shared package.

### 4. Frontend is schema-driven
`frontend/lib/types.ts` defines the TypeScript interface for the API response.
It maps 1:1 to `shared/api-contract.md`. Frontend never imports from backend.

## Data flow — step by step

1. User selects image in `UploadForm`
2. `lib/api.ts::analyzeUltrasound()` sends `multipart/form-data` to `/api/analyze-ultrasound`
3. `routes/analyze.py` validates the file (type, size, decodability)
4. `services/roboflow_client.py` POSTs image bytes to Roboflow, returns raw predictions
5. `schemas/internal.py::normalize_detections()` maps raw predictions → `InternalDetection[]`
6. `classification/classifier/features.py::extract_features()` identifies suspicious detections
7. `classification/classifier/rules.py::classify()` applies the rules engine
8. `routes/analyze.py` assembles `AnalyzeResponse` and returns 200
9. Frontend renders `ResultCard` with classification badge + detection list
