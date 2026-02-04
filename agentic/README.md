# Repsense Agentic

AI-powered fitness analysis engine. Classifies user intent, extracts relevant training facts from a generated profile, and produces either personalized advice or structured workout routines using OpenAI's `gpt-4o-mini`.

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

## Usage

The agentic module is primarily called by the backend, but can also be run standalone for testing.

### Generate a user profile from CSV

```bash
# From the project root
python -m agentic.src.main_profile_gen
```

This reads a workout CSV, normalizes it, and writes `agentic/data/user_profile.json`.

### Interactive chat (standalone)

```bash
# From the project root
python -m agentic.src.main_chat
```

Starts an interactive loop where you can ask training questions and get AI responses.

### Programmatic usage (how the backend calls it)

```python
from agentic.src.main_profile_gen import generate_profile
from agentic.src.main_chat import handle_chat_turn

# Profile generation
generate_profile(csv_path="path/to/workout.csv")

# Chat turn
result = handle_chat_turn(
    user_query="Give me a push day routine",
    user_profile=profile_dict,
    openai_client=client  # optional, has mock fallback
)
# result -> {"type": "routine", "routine_json": {...}}
# or     -> {"type": "advice", "advice": "..."}
```

## How It Works

```
User Query
  │
  ├─ Intent Classifier (LLM)
  │    → ROUTINE_GENERATION or REASONING
  │
  ├─ Query Parameter Extraction (LLM)
  │    → target exercise, muscle group, timeframe
  │
  ├─ Fact Extraction (RAG over user_profile.json)
  │    → relevant stats, PRs, trends
  │
  └─ Response Generation (LLM)
       → structured routine JSON or text advice
```

## Input CSV Format

The CSV should contain these columns:

| Column | Description |
|--------|-------------|
| `exercise_title` | Name of the exercise |
| `start_time` | Session start timestamp |
| `end_time` | Session end timestamp |
| `weight_kg` | Weight used |
| `reps` | Number of reps |
| `set_index` | Set number within the exercise |

## Supported Exercises

Mapped in `src/config.py` across these muscle groups:

- **Chest**: Bench Press, Incline Fly, Chest Fly
- **Arms**: Bicep Curl, Reverse Curl, Triceps Pushdown, Triceps Extension
- **Back**: Lat Pulldown (Close Grip, Wide Grip)
- **Shoulders**: Shoulder Press, Shrug
- **Legs**: Squat, Deadlift, Romanian Deadlift

## Generated Profile Structure

`user_profile.json` contains:

- **exercises** — per-exercise stats: volume, PRs, estimated 1RM, trends, rep distribution, recent sessions
- **muscles** — per-muscle weekly sets, training status (undertrained/optimal/high_volume)
- **global** — push/pull ratio, upper/lower ratio, undertrained muscles summary

## Project Structure

```
agentic/
├── data/
│   ├── uploads/              # Uploaded CSV files
│   └── user_profile.json     # Generated profile
└── src/
    ├── main_chat.py          # Chat turn entry point
    ├── main_profile_gen.py   # Profile generation entry point
    ├── config.py             # Exercise-to-muscle mappings
    ├── router.py             # Intent-based query routing
    ├── intent_classifier.py  # LLM intent classification
    ├── data_access.py        # Query parameter extraction
    ├── data_loader.py        # CSV loading & normalization
    ├── data_analyzer.py      # Stats computation & profile building
    └── rag_pipeline.py       # Fact extraction & response generation
```
