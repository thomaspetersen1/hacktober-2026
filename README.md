# Hacktober 2026

Teamates: Thomas Petersen, Phillip Lee

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

## Form API

The planner form submits its budget and room count to `POST /api/plan`.
The backend validates the values, splits the budget deterministically, and
returns the generated plan.

Request:

```json
{
  "budget": 500,
  "rooms": 1
}
```

Successful response (`200 OK`):

```json
{
  "theme": "Untitled Haunt",
  "budget": 500,
  "total_allocated": 500,
  "rooms": [
    {
      "order": 1,
      "name": "Room 1",
      "concept": "Concept coming soon from the ideas stage.",
      "budget": 500
    }
  ]
}
```

`budget` must be greater than zero, and `rooms` must be between 1 and 12.
Invalid input returns `422 Unprocessable Entity`. The response contains one
room entry per requested room.

### Tests

```bash
cd backend
.venv/Scripts/python -m pytest
```

## Credits

Pumpkin, bat, ghost, spider, web and other icons are from [Twemoji](https://github.com/jdecked/twemoji), licensed CC-BY 4.0. Fonts are Creepster, Pirata One and Grenze from Google Fonts (SIL Open Font License).
