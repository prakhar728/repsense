"""
Feedback detection and routine resolution.

DEPRECATED: This module is superseded by unified_classifier.py which combines
feedback detection and intent classification in a single LLM call. This file
is kept for backward compatibility.
"""
import json
from typing import Dict, Any, Optional, Callable

from .feedback_resolver import resolve_routine_for_feedback
from .tracing import maybe_track, update_current_span, log_feedback_signals
from .tracing_models import FeedbackDetectionResult, OutcomeExtraction, TargetSignals


FEEDBACK_DETECTION_PROMPT = """Determine if the user's message contains feedback about a workout routine or training plan.

Feedback includes:
- Positive: "worked well", "loved it", "saw progress", "completed"
- Negative: "too hard", "didn't like", "wasn't effective"
- Injury/pain: "hurt my", "caused pain", "injured"
- Abandonment: "stopped", "gave up", "abandoned"

Respond with ONLY valid JSON:
{"is_feedback": true | false}"""


OUTCOME_EXTRACTION_PROMPT = """Extract the outcome from the user's feedback about a workout routine.

Return JSON with:
- outcome_type: "positive" | "negative" | "injury" | "abandoned"
- outcome_text: Short verbatim description (max 200 chars)

Examples:
"too hard, couldn't complete sets" → {"outcome_type": "negative", "outcome_text": "too hard, couldn't complete sets"}
"worked well, saw progress" → {"outcome_type": "positive", "outcome_text": "worked well, saw progress"}
"hurt my shoulder" → {"outcome_type": "injury", "outcome_text": "hurt my shoulder"}

Respond with ONLY valid JSON."""


TARGET_SIGNAL_EXTRACTION_PROMPT = """Extract target signals from the user's feedback message.

Return JSON with:
- mentioned_muscles: List of muscle groups mentioned (e.g. ["chest", "shoulder"])
- mentioned_exercises: List of exercises mentioned (optional, e.g. ["bench press"])
- explicit_routine_refs: List of explicit routine references (e.g. ["chest routine", "leg routine"])
- negations: List of negated targets (e.g. ["not the leg routine"])

Examples:
"the chest routine hurt my shoulder" → {
  "mentioned_muscles": ["chest", "shoulder"],
  "explicit_routine_refs": ["chest routine"]
}
"not the leg routine, the chest one" → {
  "mentioned_muscles": ["leg", "chest"],
  "explicit_routine_refs": ["chest routine"],
  "negations": ["not the leg routine"]
}

Respond with ONLY valid JSON."""


@maybe_track(name="feedback_turn")
def run_feedback_turn(
    user_id: str,
    chat_id: str,
    message: str,
    get_routine_candidates: Callable,
    routine_in_chat_check: Callable,
    client=None
) -> Dict[str, Any]:
    """
    Process feedback detection and routine resolution.

    Returns:
    - {"type": "ignore"} - not feedback or low confidence
    - {"type": "resolved", "routine_id": str, "outcome_type": str, "outcome_text": str}
    - {"type": "clarification", "candidates": List[Dict]} - ambiguous, needs clarification
    """
    # Detect feedback
    is_feedback, detection_method = _detect_feedback(message, client)

    # Log detection result
    log_feedback_signals(is_feedback)
    update_current_span(metadata={
        "feedback_detection": {
            "is_feedback": is_feedback,
            "method": detection_method
        }
    })

    if not is_feedback:
        return {"type": "ignore"}

    # Extract outcome and target signals
    outcome, outcome_method = _extract_outcome(message, client)
    target_signals, signals_method = _extract_target_signals(message, client)

    # Log extraction results
    log_feedback_signals(
        is_feedback=True,
        outcome_type=outcome["outcome_type"],
        outcome_text=outcome["outcome_text"],
        target_signals=target_signals
    )
    update_current_span(metadata={
        "outcome_extraction": {
            "outcome_type": outcome["outcome_type"],
            "outcome_text": outcome["outcome_text"],
            "method": outcome_method
        },
        "target_signal_extraction": {
            **target_signals,
            "method": signals_method
        }
    })

    # Get candidates and resolve
    candidates = get_routine_candidates(user_id, days_back=60)

    update_current_span(metadata={
        "candidates_fetched": len(candidates) if candidates else 0
    })

    if not candidates:
        return {"type": "ignore"}

    routine_id, resolution_metadata = resolve_routine_for_feedback(
        candidates, target_signals, chat_id, routine_in_chat_check
    )

    # Log final resolution
    update_current_span(metadata={
        "final_resolution": resolution_metadata
    })

    if routine_id:
        return {
            "type": "resolved",
            "routine_id": routine_id,
            "outcome_type": outcome["outcome_type"],
            "outcome_text": outcome["outcome_text"],
        }

    # Check if this was a clarification decision
    if resolution_metadata.get("decision") == "clarification":
        return {
            "type": "clarification",
            "candidates": candidates[:3],
        }

    return {"type": "ignore"}


@maybe_track(name="detect_feedback")
def _detect_feedback(message: str, client) -> tuple[bool, str]:
    """
    Detect if message contains feedback.

    Returns:
        Tuple of (is_feedback, detection_method)
    """
    if client is None:
        keywords = [
            "too hard", "worked well", "didn't like", "completed", "stopped",
            "hurt", "injury", "pain", "abandoned", "finished", "loved", "hated"
        ]
        is_feedback = any(keyword in message.lower() for keyword in keywords)
        return is_feedback, "keyword"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": FEEDBACK_DETECTION_PROMPT},
                {"role": "user", "content": message}
            ],
            max_tokens=50,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content.strip())
        return result.get("is_feedback", False), "llm"
    except Exception:
        return False, "llm_error"


@maybe_track(name="extract_outcome")
def _extract_outcome(message: str, client) -> tuple[Dict[str, str], str]:
    """
    Extract outcome type and text.

    Returns:
        Tuple of (outcome_dict, extraction_method)
    """
    if client is None:
        message_lower = message.lower()
        if any(word in message_lower for word in ["hurt", "injury", "pain", "injured"]):
            outcome_type = "injury"
        elif any(word in message_lower for word in ["stopped", "abandoned", "gave up"]):
            outcome_type = "abandoned"
        elif any(word in message_lower for word in ["worked", "loved", "great", "good", "completed"]):
            outcome_type = "positive"
        else:
            outcome_type = "negative"

        return {
            "outcome_type": outcome_type,
            "outcome_text": message[:200]
        }, "keyword"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": OUTCOME_EXTRACTION_PROMPT},
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content.strip())
        return {
            "outcome_type": result.get("outcome_type", "negative"),
            "outcome_text": result.get("outcome_text", message[:200])
        }, "llm"
    except Exception:
        return {
            "outcome_type": "negative",
            "outcome_text": message[:200]
        }, "llm_error"


@maybe_track(name="extract_target_signals")
def _extract_target_signals(message: str, client) -> tuple[Dict[str, Any], str]:
    """
    Extract target signals (muscles, exercises, refs, negations).

    Returns:
        Tuple of (signals_dict, extraction_method)
    """
    if client is None:
        message_lower = message.lower()
        muscles = ["chest", "shoulder", "bicep", "tricep", "back", "leg", "quad", "hamstring"]
        mentioned_muscles = [m for m in muscles if m in message_lower]

        return {
            "mentioned_muscles": mentioned_muscles,
            "mentioned_exercises": [],
            "explicit_routine_refs": [],
            "negations": []
        }, "keyword"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": TARGET_SIGNAL_EXTRACTION_PROMPT},
                {"role": "user", "content": message}
            ],
            max_tokens=200,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content.strip())
        return {
            "mentioned_muscles": result.get("mentioned_muscles", []),
            "mentioned_exercises": result.get("mentioned_exercises", []),
            "explicit_routine_refs": result.get("explicit_routine_refs", []),
            "negations": result.get("negations", [])
        }, "llm"
    except Exception:
        return {
            "mentioned_muscles": [],
            "mentioned_exercises": [],
            "explicit_routine_refs": [],
            "negations": []
        }, "llm_error"
