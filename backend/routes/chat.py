import os
import json
import logging
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from agentic.src.main_chat import run_chat_turn
from agentic.src.llm_client import get_client
from agentic.src.tracing import maybe_track, update_current_span, log_memory_enrichment
from agentic.src.unified_classifier import unified_classify
from agentic.src.feedback_resolver import resolve_routine_for_feedback
from backend.storage.chat_store import (
    ensure_chat_session,
    get_all_messages,
    get_recent_messages,
    get_user_sessions,
    save_message,
)
from backend.storage.routine_store import save_routine
from backend.storage.profile_store import get_profile
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
    Get the centralized OpenAI client with optional Opik instrumentation.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    return get_client(api_key)


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
            "routine_json": routine_json,  # Include full routine structure for baseline
        })
    return formatted


@maybe_track(name="enrich_query_with_memory")
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

    enriched = "\n".join(parts)

    # Log memory enrichment details
    log_memory_enrichment(
        messages_count=len(messages) if messages else 0,
        episodes_count=len(episodes) if episodes else 0,
        enriched_query_length=len(enriched)
    )
    update_current_span(metadata={
        "memory_enrichment": {
            "original_query_length": len(query),
            "chat_messages_included": len(messages) if messages else 0,
            "episodic_memories_included": len(episodes) if episodes else 0,
            "enriched_query_length": len(enriched),
            "expansion_ratio": len(enriched) / len(query) if query else 0
        }
    })

    return enriched


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


@maybe_track(name="chat_message_handler")
@router.post("/message")
async def chat_message(payload: ChatMessageRequest):
    """
    Handle a single chat message using unified intent classification.

    New flow:
    1. Build enriched query (chat history + episodes)
    2. Unified classification (1 LLM call)
    3. Handle FEEDBACK intent if present
    4. Handle ROUTINE_GENERATION or REASONING intent
    """
    update_current_span(metadata={
        "request": {
            "user_id": payload.user_id,
            "chat_id": payload.chat_id,
            "message_length": len(payload.message)
        }
    })

    ensure_chat_session(payload.chat_id, payload.user_id)
    save_message(payload.chat_id, "user", payload.message)

    client = _get_openai_client()
    profile = _load_context(payload.user_id)

    # Step 1: Build enriched query
    messages = get_recent_messages(payload.chat_id, limit=10)
    episodes_raw = get_episodes_by_user(payload.user_id, limit=20)
    episodes = _format_episodes_for_query(episodes_raw[:5])
    enriched_query = _enrich_query_with_memory(payload.message, messages, episodes)

    logger.info(f"Enriched query length: {len(enriched_query)}")

    # Step 2: Unified classification (1 LLM call)
    classification = unified_classify(enriched_query, client)

    update_current_span(metadata={
        "unified_classification": classification.to_metadata(),
        "classifier_version": "v2"
    })

    # Step 3: Handle FEEDBACK intent
    if classification.has_feedback and classification.target_signals:
        candidates = get_routine_candidates(payload.user_id, days_back=60)

        if candidates:
            routine_id, resolution_metadata = resolve_routine_for_feedback(
                candidates,
                classification.target_signals,
                payload.chat_id,
                _routine_in_chat_check
            )

            update_current_span(metadata={"feedback_resolution": resolution_metadata})

            if routine_id:
                save_episode(
                    payload.user_id,
                    routine_id,
                    classification.outcome_type,
                    classification.outcome_text,
                )
            elif resolution_metadata.get("decision") == "clarification":
                # Always ask for clarification first, even if other intents exist
                lines = ["Which routine are you referring to?"]
                for i, candidate in enumerate(candidates[:3], 1):
                    routine_title = candidate.get("routine_json", {}).get(
                        "title", f"Routine {candidate.get('id', 'unknown')[:8]}"
                    )
                    lines.append(f"{i}. {routine_title}")

                clarification_text = "\n".join(lines)
                save_message(payload.chat_id, "assistant", clarification_text)
                return {"type": "clarification", "text": clarification_text}

    # Step 4: Handle action intent (ROUTINE_GENERATION or REASONING)
    action_intent = classification.primary_intent

    if action_intent == "FEEDBACK":
        # Pure feedback with no other intent
        ack_text = "Thanks for the feedback! I've noted that for your training history."
        save_message(payload.chat_id, "assistant", ack_text)
        return {"type": "chat", "text": ack_text}

    # Route to generation pipeline with override
    response = run_chat_turn(
        query=enriched_query,
        profile=profile,
        client=client,
        override_intent=action_intent,
        episodes=episodes
    )

    # Handle routine generation
    if isinstance(response, dict) and response.get("type") == "routine":
        routine_json = response.get("routine_json") or {}
        routine_id = save_routine(routine_json, payload.user_id)
        assistant_text = f"I've generated a routine for you based on your training data.\n\n[routine:{routine_id}]"

        save_message(payload.chat_id, "assistant", assistant_text, routine_id=routine_id)

        update_current_span(metadata={
            "response_type": "routine",
            "routine_id": routine_id
        })

        return {"type": "routine", "text": assistant_text}

    # Handle advice generation
    if isinstance(response, dict) and response.get("type") == "advice":
        advice_text = response.get("advice", "")
        save_message(payload.chat_id, "assistant", advice_text)

        update_current_span(metadata={
            "response_type": "advice",
            "advice_length": len(advice_text)
        })

        return {"type": "chat", "text": advice_text}

    # Unexpected response shape
    update_current_span(metadata={
        "response_type": "error",
        "error": "unexpected_response_shape"
    })
    raise HTTPException(status_code=500, detail="Unexpected response from chat engine.")
