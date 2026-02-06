"""Query router - orchestrates query handling."""
import pandas as pd
from typing import Dict, Any, Optional, List

from .config import Intent
from .intent_classifier import classify_intent
from .data_access import extract_query_params, get_exercise_history, format_history_response
from .rag_pipeline import get_relevant_facts, generate_advice, generate_routine
from .tracing import maybe_track, update_current_span, update_current_trace


@maybe_track(name="handle_user_query")
def handle_user_query(
    query: str,
    profile: dict,
    client=None,
    override_intent: Optional[str] = None,
    episodes: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Main entry point for handling user queries.

    Args:
        query: Enriched query string
        profile: User profile dict
        client: OpenAI client
        override_intent: If provided, skip classify_intent and use this intent (from unified_classify)
        episodes: Optional list of formatted episodes for routine generation
    """

    if override_intent:
        intent = override_intent
        intent_method = "unified_classifier"
    else:
        intent, intent_method = classify_intent(query, client)

    # Extract query params
    params = extract_query_params(query, client)

    # Get relevant facts
    facts = get_relevant_facts(params, profile)

    # Log the routing decision
    targets = params.get("targets", [])
    update_current_span(metadata={
        "routing": {
            "intent": intent,
            "intent_method": intent_method,
            "targets_count": len(targets),
            "target_types": [t["type"] for t in targets],
            "target_values": [t["value"] for t in targets],
            "facts_count": len(facts)
        }
    })

    if intent == Intent.ROUTINE_GENERATION:
        # Generate routine (now returns tuple)
        plan, gen_method = generate_routine(query, facts, client, episodes=episodes)

        update_current_span(metadata={
            "response_type": "routine",
            "generation_method": gen_method
        })

        return {
            "type": "routine",
            "routine_json": plan
        }

    elif intent == Intent.REASONING:
        # Generate advice (now returns tuple)
        advice, gen_method = generate_advice(query, facts, client)

        update_current_span(metadata={
            "response_type": "advice",
            "generation_method": gen_method,
            "advice_length": len(advice)
        })

        return {
            "type": "advice",
            "advice": advice
        }

    else:
        update_current_span(metadata={
            "response_type": "error",
            "error": "unknown_intent"
        })
        return {
            "type": "error",
            "error": "Wrong intent output from intent classifier."
        }
