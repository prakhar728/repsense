# Repsense

Repsense is an AI-powered fitness companion that turns workout history into adaptive programming. It combines a FastAPI backend, an agentic LLM pipeline, and a Next.js frontend to generate routines, capture feedback, and iterate on training plans.

## Key Features

- Routine generation based on uploaded workout history
- Feedback capture with routine resolution and episodic memory
- Routine history with contextual metadata and quick “Add to chat”
- Magic authentication for secured routine access
- Turso-backed storage with a lightweight SQL migration system

## Architecture

- `frontend/` — Next.js app (Magic auth, chat UI, routines, history)
- `backend/` — FastAPI API (profiles, chat, routines)
- `agentic/` — LLM pipeline and intent/feedback logic

## Requirements

- Python 3.9+
- Node.js 18+
- Turso database (libsql)

## Environment Variables

Backend (`/Users/prakharojha/Desktop/me/personal/repsense/.env`):

- `OPENAI_API_KEY` — required for LLM calls
- `TURSO_DATABASE_URL` — Turso connection URL
- `TURSO_AUTH_TOKEN` — Turso auth token (if required)
- `MAGIC_SECRET_KEY` — Magic admin secret for token validation
- `OPIK_ENABLED` — optional (`1` to enable tracing)

Frontend (`/Users/prakharojha/Desktop/me/personal/repsense/frontend/.env.local`):

- `NEXT_PUBLIC_API_URL` — backend URL (default `http://localhost:8000`)
- `NEXT_PUBLIC_MAGIC_PUBLISHABLE_KEY` — Magic publishable key

## Setup

### Backend

```bash
cd /Users/prakharojha/Desktop/me/personal/repsense
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run database reset and migrations (Turso):

```bash
python3 -m backend.storage.reset_db
```

Start the API:

```bash
uvicorn backend.app:app --reload
```

### Frontend

```bash
cd /Users/prakharojha/Desktop/me/personal/repsense/frontend
npm install
npm run dev
```

Frontend routes:

- `http://localhost:3000/` — Login
- `http://localhost:3000/home` — Landing page
- `http://localhost:3000/routines` — Routine history

## Routine Feedback Resolution

Feedback is resolved via a single LLM call that compares the user’s feedback text against the five most recent routine candidates. If ambiguous, the system asks a clarification question.

## Migrations

Migrations are stored in:

- `/Users/prakharojha/Desktop/me/personal/repsense/backend/storage/migrations`

The reset script drops all tables and re-applies migrations:

```bash
python3 -m backend.storage.reset_db
```

## Notes

- Routine endpoints are protected with Magic auth. If `MAGIC_SECRET_KEY` is missing, routine fetches will fail.
- Routine history titles are disambiguated in the UI when duplicates exist.

