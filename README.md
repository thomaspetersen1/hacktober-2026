# Hacktober 2026

Teamates: Thomas Petersen,

## Quick start

Requires Python 3.12 and Node 20+.

### 1. Setup (once)

```bash
cp .env.example .env
```

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
```

```bash
cd frontend
npm install
```

On macOS/Linux, use `.venv/bin/python` instead of `.venv/Scripts/python`.

### 2. Start the backend (terminal 1)

```bash
cd backend
.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
```

API: http://localhost:8000 · Docs: http://localhost:8000/docs

### 3. Start the frontend (terminal 2)

```bash
cd frontend
npm run dev
```

App: http://localhost:5173

### Tests

```bash
cd backend
.venv/Scripts/python -m pytest
```
