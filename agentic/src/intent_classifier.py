"""
Intent classification using LLM.

DEPRECATED: This module is superseded by unified_classifier.py which combines
intent classification and feedback detection in a single LLM call. This file
is kept for backward compatibility with CLI mode (main_chat.py).
"""
import json
from typing import Tuple

from .config import Intent
from .tracing import maybe_track, update_current_span, log_intent_classification


INTENT_PROMPT = """Classify the user's fitness query into one of the following intents:

ROUTINE_GENERATION
- User asks for a workout, training plan, split, or program
- User implies wanting a routine or plan to follow
Examples:
"give me a push workout"
"make a 4 day gym split"
"I want a leg day routine"
"design a plan to build muscle"
"what should I train today"

REASONING
- User asks for advice, analysis, explanation, or coaching
- User wants insight, feedback, or understanding
Examples:
"how can I improve my squat"
"am I overtraining"
"why am I stuck at the same weight"
"what muscles am I neglecting"

Respond with ONLY one label:
ROUTINE_GENERATION or REASONING
"""


@maybe_track(name="classify_intent")
def classify_intent(query: str, client=None) -> Tuple[str, str]:
    """
    Classify query as REASONING or ROUTINE_GENERATION.

    Returns:
        Tuple of (intent, classification_method)
    """
    if client is None:
        intent = _classify_mock(query)
        log_intent_classification(intent)
        update_current_span(metadata={
            "intent": intent,
            "classification_method": "keyword"
        })
        return intent, "keyword"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content": query}
            ],
            max_tokens=25
        )

        result = response.choices[0].message.content.strip().upper()
        intent = Intent.ROUTINE_GENERATION if "ROUTINE_GENERATION" in result else Intent.REASONING

        log_intent_classification(intent)
        update_current_span(metadata={
            "intent": intent,
            "classification_method": "llm",
            "raw_response": result
        })

        return intent, "llm"
    except Exception as e:
        intent = _classify_mock(query)
        update_current_span(metadata={
            "intent": intent,
            "classification_method": "llm_error",
            "error": str(e)
        })
        return intent, "llm_error"


def _classify_mock(query: str) -> str:
    """Fallback keyword-based classification."""
    data_keywords = ["show", "list", "see", "display", "what did", "history"]
    if any(kw in query.lower() for kw in data_keywords):
        return Intent.ROUTINE_GENERATION
    return Intent.REASONING
