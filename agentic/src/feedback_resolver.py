"""Feedback resolution - LLM-based routine matching."""
from typing import List, Dict, Any, Optional, Tuple
import json

from .tracing import maybe_track, update_current_span


ROUTINE_RESOLUTION_PROMPT = """You are tasked to identify which routine the user is giving feedback about.
Compare the user query to the candidate routines and return only the routine_id
that best matches. If ambiguous or unclear, return null.

Return ONLY valid JSON:
{"routine_id": "<id>"}
or
{"routine_id": null}
"""


def _truncate(text: str, limit: int = 1800) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _format_candidates(candidates: List[Dict[str, Any]]) -> str:
    lines = []
    for idx, candidate in enumerate(candidates, 1):
        routine_json = candidate.get("routine_json", {}) or {}
        title = routine_json.get("title", "Untitled Routine")
        last_mentioned = candidate.get("last_mentioned_at", "unknown date")
        routine_id = candidate.get("id", "unknown")
        routine_blob = _truncate(json.dumps(routine_json, separators=(",", ":")))
        lines.append(
            f"{idx}. {title} {last_mentioned} ... {routine_blob} [{routine_id}]"
        )
    return "\n".join(lines)


@maybe_track(name="resolve_routine_for_feedback")
def resolve_routine_for_feedback(
    candidates: List[Dict[str, Any]],
    target_signals: dict,
    chat_id: str,
    routine_in_chat_check,
    client=None,
) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Resolve which routine feedback refers to.

    Returns:
        Tuple of (routine_id, resolution_metadata)
        - routine_id: Resolved routine ID, or None if ambiguous
        - resolution_metadata: Dict with decision details for tracing
    """
    resolution_metadata = {
        "decision": "ignore",
        "reason": "no_candidates",
        "routine_id": None,
        "candidates_considered": len(candidates),
    }

    if not candidates:
        update_current_span(metadata={"resolution": resolution_metadata})
        return None, resolution_metadata

    if client is None:
        resolution_metadata["reason"] = "no_llm_client"
        update_current_span(metadata={"resolution": resolution_metadata})
        return None, resolution_metadata

    candidates_text = _format_candidates(candidates)
    user_query = (
        target_signals.get("raw_feedback_text")
        or target_signals.get("feedback_text")
        or ""
    )

    prompt = (
        f"{ROUTINE_RESOLUTION_PROMPT}\n\n"
        f"Here is the user query:\n{user_query}\n\n"
        f"Here are the routines:\n{candidates_text}\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()
    routine_id = None
    try:
        parsed = json.loads(content)
        routine_id = parsed.get("routine_id")
    except Exception:
        routine_id = None

    candidate_ids = {c.get("id") for c in candidates}
    if routine_id not in candidate_ids:
        routine_id = None

    if routine_id is None:
        resolution_metadata.update({
            "decision": "clarification",
            "reason": "llm_ambiguous_or_invalid",
        })
        update_current_span(metadata={"resolution": resolution_metadata})
        return None, resolution_metadata

    resolution_metadata.update({
        "decision": "resolved",
        "reason": "llm_resolved",
        "routine_id": routine_id,
    })
    update_current_span(metadata={"resolution": resolution_metadata})
    return routine_id, resolution_metadata
