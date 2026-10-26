# CLAUDE.md

## Project: Haunted House Planner (working name)

A Halloween hackathon project for **Hacktober 2026**. The user enters a **budget ($)** and a **number of rooms**, and the app returns a complete haunted house design:

- A **diagram / floor plan** of the rooms and the path guests walk through them
- A **theme and scare concept** for each room that fits one overall story
- A **budget breakdown**: suggested $ per room, plus specific props/items that fit within it

### Core pipeline (three AI stages)

1. **Idea creation**: pick an overall theme (e.g. "abandoned asylum", "witch's cottage") and create a concept per room: the scare, the mood, lighting and sound.
2. **Item research within budget**: for each room, find props, decorations and effects whose total cost fits that room's share of the budget. Prices come from data, not from the model's guesses.
3. **Room plan cohesiveness**: check the whole house. The story flows room to room, pacing builds (calm → tense → big scare → exit), there is no duplicated gimmick, and the totals add up to no more than the budget.

The output is rendered in the React frontend as an interactive floor plan with a per-room card and a budget table.

## Hackathon tracks we are targeting

1. **Best Open-Source AI Project**: open-source or open-weight AI must be central to how the app works.
2. **Best Open-Source AI Project with Snowflake**: also requires **(a)** using Snowflake CoCo, **(b)** a freely accessible Snowflake dataset (Marketplace or `SNOWFLAKE_SAMPLE_DATA`), and **(c)** open-source/open-weight AI.

Requirements for both tracks:
- Public GitHub repo under an open-source license (add `LICENSE`, e.g. MIT or Apache-2.0).
- In the demo, state **which dataset** we used and **how CoCo helped** (keep notes in `docs/coco-log.md` as we go).

## AI rules

- **Use only open-weight models** for generation (e.g. Llama, Mistral, Qwen, gpt-oss). Do not add proprietary LLM APIs to the app's runtime path, because that would undermine the main track.
- Preferred serving options:
  - **Snowflake Cortex `AI_COMPLETE` / `COMPLETE`** with an open-weight model (llama / mistral family). This keeps the model next to the data.
  - **Ollama** running locally as a fallback for development or offline demos.
- Embeddings for matching items to room themes: an open-source embedding model (e.g. `snowflake-arctic-embed`, Apache-2.0, available via Cortex `EMBED_TEXT`).
- The LLM proposes ideas and chooses items. **Budget math is deterministic code**, never LLM arithmetic. Validate the LLM's JSON output against a schema and retry if it fails.

## Snowflake usage

- Datasets are explored with **CoCo** (Snowflake's AI coding agent). Record useful prompts and queries in `docs/coco-log.md`.
- Candidate data (check availability with CoCo before relying on any of it):
  - **Item / price catalog**: `SNOWFLAKE_SAMPLE_DATA.TPCDS_*` `ITEM` tables (category, class, current price) can serve as a stand-in catalog. Alternatively, load a small curated Halloween prop CSV into our own Snowflake table.
  - **Price context**: CPI and price indexes from the free *Snowflake Public Data* Marketplace listing, used to adjust prices for inflation or flag unrealistic budgets.
  - **Location context**: points-of-interest and Census data from public Marketplace listings, used for "where to buy nearby" and estimates of expected visitors.
  - **Weather**: a free weather Marketplace listing, used to warn about outdoor rooms on Oct 31.
- SQL lives in `sql/`. Never commit credentials. Use `.env` (git-ignored) or Snowflake connection config.

## Stack

- **Frontend**: React 19 + Vite, **JavaScript only** (`.js` / `.jsx`, no TypeScript). Linting uses `oxlint`.
- **Backend**: **Python only**. FastAPI + Pydantic v2, with `pydantic-settings` for config and Snowpark (`snowflake-snowpark-python`) for Snowflake data and Cortex calls.
- **Python 3.12** (Snowpark requires ≤ 3.12 at time of writing).
- Floor plan rendering happens in the frontend (SVG / React components, or React Flow if needed).

## Repository layout

```
frontend/                  Vite + React (JS)
  vite.config.js           dev proxy: /api -> http://localhost:8000
  src/api/client.js        all fetch calls to the backend go through here
  src/App.jsx              home page: hero, planner form, results
  src/components/          NightSky (animated backdrop), PlanForm (tombstone form)
  public/images/           Twemoji SVGs (CC-BY 4.0) for pumpkins, bats, etc.
backend/                   FastAPI (Python)
  app/main.py              app, CORS, /api/health
  app/config.py            Settings from the root .env
  app/schemas.py           Pydantic request/response models (the API contract)
  app/routers/plan.py      POST /api/plan
  app/services/budget.py   deterministic budget allocation (no LLM math)
  app/services/planner.py  pipeline: ideas -> sourcing -> cohesion
  app/services/snowflake_client.py  cached Snowpark session
  tests/                   pytest
.claude/launch.json        dev server configs (backend :8000, frontend :5173)
```

## Environment

- A **single `.env` at the repo root** is shared by both apps. Copy it from `.env.example`.
- The backend loads it in `backend/app/config.py`. Vite loads it via `envDir: '..'`.
- Only `VITE_*` variables are exposed to the browser. **Never give a secret a `VITE_` prefix.**

## Commands

Setup (run once): see the Quick start in `README.md`.

Run (two terminals):
- Backend: `cd backend` then `.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000` (API docs at http://localhost:8000/docs)
- Frontend: `cd frontend` then `npm run dev` (http://localhost:5173, proxies `/api` to the backend)

Check:
- Backend tests: `cd backend` then `.venv/Scripts/python -m pytest`
- Frontend: `cd frontend` then `npm run lint` and `npm run build`

On macOS/Linux, use `.venv/bin/python` instead of `.venv/Scripts/python`.

## API contract

- `GET /api/health` returns `{status, snowflake_configured}`.
- `POST /api/plan` takes `{budget, rooms, square_feet?}` (budget > 0, rooms 1–12, square_feet optional and > 0) and returns `{theme, budget, total_allocated, square_feet, rooms: [{order, name, concept, budget}]}`.
- When you change `backend/app/schemas.py`, update `frontend/src/api/client.js` and the UI to match.

## Conventions

- Keep it hackathon-simple: working demo over abstraction.
- Each pipeline stage is its own module with a clear input/output schema so stages can be tested and swapped.
- Frontend stays JavaScript and backend stays Python. Don't add TypeScript or a Node backend.
- Secrets go in the root `.env` (git-ignored). Only `.env.example` is committed.
- Do not hardcode secrets, account identifiers, or personal info.

