# Branching Strategy

## Branches

| Branch | Owner | Primary folders |
|---|---|---|
| `feat/classification-rules` | Owner 3 | `classification/` |
| `feat/backend-roboflow` | Owner 2 | `backend/` |
| `feat/frontend-ui` | Owner 1 | `frontend/` |
| `main` | All | merge target |

## Recommended sequence

### Day 1 — Contract freeze
All three owners review `shared/api-contract.md` together.
No changes to that file after sign-off without a team discussion.

### Day 1–2 — Owner 3 goes first (classification)
Classification logic has zero dependencies on backend or frontend.
Land `feat/classification-rules` into `main` first so Owner 2 can import it.

```bash
# Owner 3
git checkout -b feat/classification-rules
# ... implement classification/
git push origin feat/classification-rules
# open PR → main
```

### Day 2–3 — Owner 2 integrates
Backend wires Roboflow + calls the classification module.
Owner 2 pulls `main` (which now includes classification) before starting.

```bash
# Owner 2
git checkout main && git pull
git checkout -b feat/backend-roboflow
# ... implement backend/
# import from classification.classifier.rules import classify
```

### Day 1–3 — Owner 1 works in parallel
Frontend has no dependency on the backend being live.
Use the sample payloads in `shared/sample-payloads/` to build the UI
against a mock or a local stub.

```bash
# Owner 1
git checkout -b feat/frontend-ui
# ... implement frontend/ using mocked API response
```

## Merge order

```
feat/classification-rules → main   (first)
feat/backend-roboflow     → main   (second, after classification lands)
feat/frontend-ui          → main   (anytime, parallel)
```

## Merge-conflict prevention rules

1. **Each owner stays in their folder.** If you find yourself editing a file
   in another owner's folder, stop and discuss.

2. **`shared/` is append-only after freeze.** Never edit existing entries;
   add new ones via PR review.

3. **`classification/classifier/models.py` and `backend/app/schemas/internal.py`
   must stay in sync.** Owner 2 and Owner 3 coordinate on any schema change.

4. **`README.md` and `docs/` are low-conflict** — merge prose conflicts manually.

5. Use feature flags (a constant in `constants.py`) rather than branching
   on half-implemented features.

## PR checklist

- [ ] Tests pass locally
- [ ] No files edited outside your ownership folder (except docs)
- [ ] `shared/api-contract.md` unchanged (or team-approved)
- [ ] Classification tests: `cd classification && pytest`
- [ ] Backend tests: `cd backend && pytest`
