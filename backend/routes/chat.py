import os
import json
import logging
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

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
from agentic.src.feedback_router import run_feedback_turn
from backend.storage.episodic_store import (
    save_episode,
    get_routine_candidates,
    get_episodes_by_user,
)


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


def _routine_in_chat_check(chat_id: str, routine_id: str) -> bool:
    """Check if routine was mentioned in this chat."""
    messages = get_all_messages(chat_id)
    return any(msg.get("routine_id") == routine_id for msg in messages)


def _format_episodes_for_query(episodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format episodes for query enrichment."""
    formatted = []
    for episode in episodes:
        routine_json = episode.get("routine_json", {})
        routine_title = routine_json.get("title", "Unknown Routine")
        
        # Extract muscles
        routine_muscles = set()
        for session in routine_json.get("sessions", []):
            for exercise in session.get("exercises", []):
                muscle = exercise.get("primary_muscle", "")
                if muscle:
                    routine_muscles.add(muscle)
        
        muscles_str = ", ".join(sorted(routine_muscles)[:3])
        
        formatted.append({
            "routine_title": routine_title,
            "muscles": muscles_str,
            "outcome_text": episode.get("outcome_text", ""),
        })
    return formatted


def _enrich_query_with_memory(
    query: str, messages: List[Dict[str, Any]], episodes: List[Dict[str, Any]]
) -> str:
    """
    Enrich query with chat history and episodic memories.
    
    Format:
    === Chat History ===
    User: ...
    Assistant: ...
    
    === Previous Routines ===
    Routine X (chest): Too hard.
    
    === Current Query ===
    {original_query}
    """
    parts = []
    
    # Chat History
    if messages:
        parts.append("=== Chat History ===")
        for msg in messages[-10:]:  # Last 10 messages
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "")
            # Truncate long messages
            if len(content) > 200:
                content = content[:200] + "..."
            parts.append(f"{role}: {content}")
        parts.append("")
    
    # Previous Routines
    if episodes:
        parts.append("=== Previous Routines ===")
        for episode in episodes:
            title = episode.get("routine_title", "Unknown Routine")
            muscles = episode.get("muscles", "")
            outcome = episode.get("outcome_text", "")
            parts.append(f"- Routine \"{title}\" ({muscles}): {outcome}")
        parts.append("")
    
    # Current Query
    parts.append("=== Current Query ===")
    parts.append(query)
    
    return "\n".join(parts)


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
    # Validate chat_id belongs to user_id
    from backend.storage.db import get_connection
    conn = get_connection()
    cursor = conn.execute(
        "SELECT 1 FROM chat_sessions WHERE id = ? AND user_id = ?",
        (chat_id, user_id)
    )
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Chat session not found.")
    
    messages = get_all_messages(chat_id)
    return {"messages": messages}


@router.post("/message")
async def chat_message(payload: ChatMessageRequest):
    """
    Handle a single chat message with persistent memory and optional routine generation.
    
    Two-stage processing:
    - Stage A: Feedback detection & resolution (side-channel)
    - Stage B: Intent handling with enriched context
    """
    # Ensure a chat session exists and persist the user message.
    ensure_chat_session(payload.chat_id, payload.user_id)
    save_message(payload.chat_id, "user", payload.message)

    client = _get_openai_client()

    # ===== STAGE A: Feedback Detection & Resolution =====
    feedback_result = run_feedback_turn(
        payload.user_id,
        payload.chat_id,
        payload.message,
        get_routine_candidates,
        _routine_in_chat_check,
        client,
    )
    
    if feedback_result.get("type") == "resolved":
        save_episode(
            payload.user_id,
            feedback_result["routine_id"],
            feedback_result["outcome_type"],
            feedback_result["outcome_text"],
        )
    elif feedback_result.get("type") == "clarification":
        candidates = feedback_result.get("candidates", [])
        lines = ["Which routine are you referring to?"]
        for i, candidate in enumerate(candidates[:3], 1):
            routine_title = candidate.get("routine_json", {}).get("title", f"Routine {candidate.get('id', 'unknown')[:8]}")
            lines.append(f"{i}. {routine_title}")
        return {"type": "clarification", "text": "\n".join(lines)}

    # ===== STAGE B: Intent Handling =====
    profile = _load_context(payload.user_id)
    messages = get_recent_messages(payload.chat_id, limit=10)
    episodes_raw = get_episodes_by_user(payload.user_id, limit=20)
    episodes = _format_episodes_for_query(episodes_raw[:5])
    
    enriched_query = _enrich_query_with_memory(payload.message, messages, episodes)
    
    # Log enriched query for debugging
    logger.info("=" * 80)
    logger.info("ENRICHED QUERY SENT TO AGENTIC LAYER:")
    logger.info("=" * 80)
    logger.info(enriched_query)
    logger.info("=" * 80)

    response = run_chat_turn(
        query=enriched_query,
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
