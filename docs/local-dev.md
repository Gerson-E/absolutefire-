# Local Development Guide

## Prerequisites

| Tool | Version |
|---|---|
| Python | ≥ 3.11 |
| Node.js | ≥ 18 |
| npm | ≥ 9 |

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and fill in:
#   ROBOFLOW_API_KEY=your_key_here
#   ROBOFLOW_MODEL_URL=https://detect.roboflow.com/your-model/1

uvicorn app.main:app --reload --port 8000
```

Backend is live at http://localhost:8000
Swagger UI: http://localhost:8000/docs

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend is live at http://localhost:3000

The frontend expects the backend at `http://localhost:8000`.
This is set via `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local`.

```bash
# frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Classification — standalone test run

```bash
cd classification
pip install pytest          # if not already installed
pytest tests/ -v
```

No server needed. Classification is pure Python.

## Full stack CORS note

The backend has CORS configured for `http://localhost:3000` in development.
See `backend/app/main.py`. Adjust if you run the frontend on a different port.

## Useful curl test

```bash
curl -X POST http://localhost:8000/api/analyze-ultrasound \
  -F "image=@/path/to/liver_us.jpg"
```

With calibration:
```bash
curl -X POST http://localhost:8000/api/analyze-ultrasound \
  -F "image=@/path/to/liver_us.jpg" \
  -F "px_per_mm=3.5"
```

Health check:
```bash
curl http://localhost:8000/api/health
```
