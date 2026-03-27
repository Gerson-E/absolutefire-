# Risks & Known Limitations

## Clinical / product

| Risk | Mitigation |
|---|---|
| Prototype misused as clinical tool | Prominent warnings in UI and all API responses |
| Missing mm calibration → under/over-staging | Default to conservative US-3; explicit warning in response |
| Roboflow model label set may differ from expected SUSPICIOUS_LABELS | `constants.py` is configurable; document expected labels |
| Low-confidence detections inflate classification | Confidence threshold in `constants.py` (default 0.3) |

## Technical

| Risk | Mitigation |
|---|---|
| Roboflow timeout | httpx timeout + 502 error with clear message |
| Roboflow rate limit (free tier) | Retry-after header respected; 429 propagated to client |
| Malformed Roboflow response | `normalize_detections()` validates structure; raises 502 on failure |
| Corrupted or non-image file upload | PIL decode check in `file_validation.py` |
| Unsupported MIME type | Allowlist in `file_validation.py` |
| Overlapping / duplicate detections | Largest unique detection used; duplicates logged as warnings |
| Segmentation model output (no bbox) | `normalize_detections()` computes bbox from mask bounding rect if present |

## Merge / team

| Risk | Mitigation |
|---|---|
| Schema drift between `internal.py` and `classifier/models.py` | Explicit note in both files; sync is manual but documented |
| `shared/api-contract.md` modified without review | Noted in PR checklist; treat as protected file |
| Backend merging before classification is ready | Owner 3 lands first per branching strategy |

## Out of scope for v1

- DICOM ingestion (physical spacing from metadata)
- Segmentation mask area calculation
- Authentication / user accounts
- Result persistence / audit log
- Multi-frame / video ultrasound
- Doppler / contrast enhancement features
