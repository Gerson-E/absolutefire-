# AbsoluteFire — US LI-RADS Surveillance Classifier (Prototype)

Accepts a liver ultrasound image, runs Roboflow inference, and returns a
US-1 / US-2 / US-3 LI-RADS surveillance classification.

> **This is a research prototype — not a clinical decision tool.**

---

## Quick start

### Prerequisites
- Node.js ≥ 18
- Python ≥ 3.11
- A Roboflow API key + model endpoint

### 1. Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in ROBOFLOW_API_KEY + ROBOFLOW_MODEL_URL
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev                    # http://localhost:3000
```

### 3. Classification (standalone tests)
```bash
cd classification
pip install pytest
pytest tests/
```

---

## Folder ownership

| Folder | Owner | Branch |
|---|---|---|
| `frontend/` | Owner 1 — Frontend | `feat/frontend-ui` |
| `backend/` | Owner 2 — Backend | `feat/backend-roboflow` |
| `classification/` | Owner 3 — Classification | `feat/classification-rules` |
| `shared/` | All (read-only after contract freeze) | any |
| `docs/` | All | any |

See `docs/branching-strategy.md` for team workflow.

---

## API

`POST /api/analyze-ultrasound` — see `shared/api-contract.md`

`GET /api/health`
(Architecture outline, main branch)
