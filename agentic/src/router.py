"""Query router - orchestrates query handling."""
import pandas as pd
from .config import Intent
from .intent_classifier import classify_intent
from .data_access import extract_query_params, get_exercise_history, format_history_response
from .rag_pipeline import get_relevant_facts, generate_advice, generate_routine


def handle_user_query(query: str, df: pd.DataFrame, profile: dict, client=None) -> str:
    """Main entry point for handling user queries."""
    intent = classify_intent(query, client)
    params = extract_query_params(query, client)
    facts = get_relevant_facts(params, profile)

    if intent == Intent.DATA_ACCESS:
        history = get_exercise_history(df, params)
        return format_history_response(history)

    elif intent == Intent.ROUTINE_GENERATION:
        return generate_routine(query, facts, client)

    else:  # REASONING
        return generate_advice(query, facts, client)
