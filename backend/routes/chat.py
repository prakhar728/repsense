import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agentic.src.main_chat import run_chat_turn
from backend.storage.chat_store import (
    ensure_chat_session,
    get_all_messages,
    get_recent_messages,
    get_user_sessions,
    save_message,
)
from backend.storage.routine_store import save_routine
from backend.storage.profile_store import get_profile


router = APIRouter()


class ChatMessageRequest(BaseModel):
    user_id: str
    chat_id: str
    message: str


def _load_context(user_id: str) -> Dict[str, Any]:
    """
    Load user profile from the database.
    """
    profile = get_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=500, detail="User profile not found.")
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


@router.get("/sessions/{user_id}")
async def list_sessions(user_id: str):
    """
    Return all chat sessions for a user with their last message.
    """
    sessions = get_user_sessions(user_id)
    return {"sessions": sessions}


@router.get("/sessions/{user_id}/{chat_id}/messages")
async def list_messages(user_id: str, chat_id: str):
    """
    Return all messages for a chat session.
    """
    messages = get_all_messages(chat_id)
    return {"messages": messages}


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
    profile = _load_context(payload.user_id)
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
        assistant_text = f"I've generated a routine for you based on your training data.\n\n[routine:{routine_id}]"

        # Persist assistant message referencing the routine by ID only.
        save_message(payload.chat_id, "assistant", assistant_text, routine_id=routine_id)

        return {"type": "routine", "text": assistant_text}

    # Normal chat response path
    if isinstance(response, dict) and response.get("type") == "advice":
        advice_text = response.get("advice", "")
        save_message(payload.chat_id, "assistant", advice_text)
        return {"type": "chat", "text": advice_text}

    # Fallback if agentic code returns an unexpected shape.
    raise HTTPException(status_code=500, detail="Unexpected response from chat engine.")
