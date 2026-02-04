# Repsense Backend

FastAPI REST API that serves as the bridge between the frontend and the agentic AI pipeline. Handles chat sessions, profile generation from workout CSVs, and routine storage.

## Prerequisites

- Python 3.10+
- An OpenAI API key

## Setup

```bash
# From the project root
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key
```

## Running

```bash
# From the project root
uvicorn backend.app:app --reload
```

The server starts at `http://localhost:8000`.

## API Endpoints

### `POST /profile/upload`

Upload a workout CSV and generate a user profile.

- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `user_id` (string) — unique user identifier
  - `file` (CSV file) — workout data export

**Expected CSV columns**: `exercise_title`, `start_time`, `end_time`, `weight_kg`, `reps`, `set_index`

```bash
curl -X POST http://localhost:8000/profile/upload \
  -F "user_id=user123" \
  -F "file=@workout_data.csv"
```

**Response**:
```json
{ "status": "profile_generated" }
```

---

### `POST /chat/message`

Send a chat message and get an AI-powered response.

- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "user_id": "user123",
    "chat_id": "chat_abc",
    "message": "How is my bench press progressing?"
  }
  ```

**Response** (advice):
```json
{ "type": "chat", "text": "Your bench press has been trending upward..." }
```

**Response** (routine generated):
```json
{ "type": "routine", "text": "routine-gen-<routine_id>" }
```

---

### `GET /routines/{routine_id}`

Fetch a previously generated routine.

**Response**:
```json
{
  "routine": {
    "title": "...",
    "goal": "...",
    "sessions": [...]
  }
}
```

## Storage

- **SQLite** database at `backend/storage/app.db`
- Tables: `chat_sessions`, `chat_messages`, `routines`
- User profiles are written to `agentic/data/user_profile.json`

## Project Structure

```
backend/
├── app.py                 # FastAPI app entry point, mounts all routes
├── routes/
│   ├── chat.py            # /chat endpoints
│   ├── profile.py         # /profile endpoints
│   └── routines.py        # /routines endpoints
└── storage/
    ├── chat_store.py      # Chat session & message persistence
    └── routine_store.py   # Routine persistence
```
