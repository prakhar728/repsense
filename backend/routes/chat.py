import json
import os
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agentic.src.main_chat import run_chat_turn
from backend.storage.chat_store import (
    ensure_chat_session,
    get_recent_messages,
    save_message,
)
from backend.storage.routine_store import save_routine


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "agentic" / "data"


class ChatMessageRequest(BaseModel):
    user_id: str
    chat_id: str
    message: str


def _load_context() -> tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Load workout dataframe and user profile from disk.
    """

    profile_path = DATA_DIR / "user_profile.json"

    if not profile_path.exists():
        raise HTTPException(status_code=500, detail="User profile not found.")


    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)
    return profile


def _get_openai_client():
    """
    Lazily initialize the OpenAI client if an API key is available.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    from openai import OpenAI

    return OpenAI(api_key=api_key)


@router.post("/message")
async def chat_message(payload: ChatMessageRequest):
    """
    Handle a single chat message with persistent memory and optional routine generation.
    """
    # Ensure a chat session exists and persist the user message.
    ensure_chat_session(payload.chat_id, payload.user_id)
    save_message(payload.chat_id, "user", payload.message)

    # Load recent messages for this chat (for persistence / potential future use).
    _ = get_recent_messages(payload.chat_id, limit=10)

    # Prepare context for the agentic chat turn.
    profile = _load_context()
    client = _get_openai_client()

    response = run_chat_turn(
        query=payload.message,
        profile=profile,
        client=client,
    )

    # Routine generation path
    if isinstance(response, dict) and response.get("type") == "routine":
        routine_json = response.get("routine_json") or {}
        routine_id = save_routine(routine_json)
        assistant_text = f"routine-gen-{routine_id}"

        # Persist assistant message referencing the routine by ID only.
        save_message(payload.chat_id, "assistant", assistant_text, routine_id=routine_id)

        return {"type": "routine", "text": assistant_text}

    # Normal chat response path
    if isinstance(response, str) and response.get("type") == "advice":
        save_message(payload.chat_id, "assistant", response)
        return {"type": "chat", "text": response}

    # Fallback if agentic code returns an unexpected shape.
    raise HTTPException(status_code=500, detail="Unexpected response from chat engine.")

