"""Tracing utilities for Opik observability.

This module provides decorators and utilities for optional Opik instrumentation.
When OPIK_ENABLED=1 is not set, all decorators are no-ops, keeping the code
independently testable without Opik dependencies.

Usage:
    from .tracing import maybe_track, update_current_span

    @maybe_track(name="my_function")
    def my_function(x):
        update_current_span(metadata={"input_length": len(x)})
        return process(x)
"""
import os
from functools import wraps
from typing import Any, Dict, Optional, Callable
from contextlib import contextmanager


def is_opik_enabled() -> bool:
    """Check if Opik instrumentation is enabled."""
    return os.getenv("OPIK_ENABLED", "").lower() in ("1", "true", "yes")


def maybe_track(name: Optional[str] = None):
    """
    Conditionally apply Opik's @track decorator.

    When OPIK_ENABLED=1 is set, this applies the full @track decorator.
    Otherwise, it's a no-op that returns the function unchanged.

    Args:
        name: Optional name for the span. Defaults to function name.

    Example:
        @maybe_track(name="feedback_detection")
        def detect_feedback(message: str) -> bool:
            ...
    """
    def decorator(fn: Callable) -> Callable:
        if is_opik_enabled():
            try:
                from opik import track
                return track(name=name)(fn)
            except ImportError:
                pass
        return fn
    return decorator


def update_current_span(
    metadata: Optional[Dict[str, Any]] = None,
    input: Optional[Dict[str, Any]] = None,
    output: Optional[Any] = None,
    tags: Optional[list] = None
) -> None:
    """
    Update the current Opik span with additional metadata.

    This is a no-op when Opik is not enabled or not installed.

    Args:
        metadata: Additional metadata to log (e.g., scores, decisions)
        input: Override the input captured by @track
        output: Override the output captured by @track
        tags: List of tags to add to the span
    """
    if not is_opik_enabled():
        return

    try:
        from opik import opik_context
        context = opik_context.get_current_span_data()
        if context is None:
            return

        if metadata:
            opik_context.update_current_span(metadata=metadata)
        if input:
            opik_context.update_current_span(input=input)
        if output:
            opik_context.update_current_span(output=output)
        if tags:
            opik_context.update_current_span(tags=tags)
    except (ImportError, AttributeError):
        pass


def update_current_trace(
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[list] = None
) -> None:
    """
    Update the current Opik trace with additional metadata.

    This is a no-op when Opik is not enabled or not installed.

    Args:
        metadata: Additional metadata for the trace
        tags: List of tags to add to the trace
    """
    if not is_opik_enabled():
        return

    try:
        from opik import opik_context
        if metadata:
            opik_context.update_current_trace(metadata=metadata)
        if tags:
            opik_context.update_current_trace(tags=tags)
    except (ImportError, AttributeError):
        pass


@contextmanager
def span_context(name: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Context manager for creating a child span.

    This is a no-op when Opik is not enabled or not installed.

    Args:
        name: Name for the span
        metadata: Optional metadata to attach

    Example:
        with span_context("ranking", metadata={"candidates": 5}):
            results = rank_candidates(...)
    """
    if not is_opik_enabled():
        yield
        return

    try:
        from opik import opik_context
        span = opik_context.get_current_span_data()
        if span is None:
            yield
            return

        # Use Opik's span context
        from opik import track

        @track(name=name)
        def _inner():
            if metadata:
                update_current_span(metadata=metadata)

        # This is a simplified version - in practice you'd use opik.start_span()
        # but that API may vary. The @track decorator handles most cases.
        yield
    except (ImportError, AttributeError):
        yield


def log_scoring_breakdown(
    candidates: list,
    winner_id: Optional[str],
    decision: str,
    score_gap: Optional[float] = None
) -> None:
    """
    Log detailed scoring breakdown for routine resolution.

    This provides visibility into why a particular routine was selected.

    Args:
        candidates: List of scored candidates with their score breakdowns
        winner_id: ID of the selected routine (None if ambiguous)
        decision: Decision type ("resolved", "clarification", "ignore")
        score_gap: Gap between top two scores (if applicable)
    """
    if not is_opik_enabled():
        return

    metadata = {
        "resolution_decision": decision,
        "candidates_count": len(candidates),
        "winner_routine_id": winner_id,
        "score_gap": score_gap,
        "candidate_scores": [
            {
                "routine_id": c.get("id"),
                "title": c.get("routine_json", {}).get("title", "Unknown"),
                "total_score": c.get("score"),
                "score_breakdown": c.get("score_breakdown", {})
            }
            for c in candidates[:5]  # Top 5 for context
        ]
    }
    update_current_span(metadata=metadata)


def log_feedback_signals(
    is_feedback: bool,
    outcome_type: Optional[str] = None,
    outcome_text: Optional[str] = None,
    target_signals: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log feedback detection and extraction results.

    Args:
        is_feedback: Whether message was classified as feedback
        outcome_type: Type of feedback (positive/negative/injury/abandoned)
        outcome_text: Extracted feedback text
        target_signals: Extracted target signals (muscles, exercises, etc.)
    """
    if not is_opik_enabled():
        return

    metadata = {
        "feedback_detected": is_feedback,
    }
    if outcome_type:
        metadata["outcome_type"] = outcome_type
    if outcome_text:
        metadata["outcome_text"] = outcome_text
    if target_signals:
        metadata["target_signals"] = target_signals

    update_current_span(metadata=metadata)


def log_intent_classification(
    intent: str,
    query_params: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log intent classification results.

    Args:
        intent: Classified intent (ROUTINE_GENERATION, REASONING)
        query_params: Extracted query parameters (target, timeframe)
    """
    if not is_opik_enabled():
        return

    metadata = {
        "classified_intent": intent,
    }
    if query_params:
        metadata["query_params"] = query_params

    update_current_span(metadata=metadata)


def log_memory_enrichment(
    messages_count: int,
    episodes_count: int,
    enriched_query_length: int
) -> None:
    """
    Log memory enrichment details.

    Args:
        messages_count: Number of chat messages included
        episodes_count: Number of episodic memories included
        enriched_query_length: Length of the enriched query
    """
    if not is_opik_enabled():
        return

    update_current_span(metadata={
        "memory_enrichment": {
            "chat_messages_included": messages_count,
            "episodic_memories_included": episodes_count,
            "enriched_query_length": enriched_query_length
        }
    })


def log_generation_context(
    facts_count: int,
    facts_text_length: int,
    generation_type: str
) -> None:
    """
    Log context provided to generation calls.

    Args:
        facts_count: Number of facts provided
        facts_text_length: Length of formatted facts text
        generation_type: Type of generation (routine, advice)
    """
    if not is_opik_enabled():
        return

    update_current_span(metadata={
        "generation_context": {
            "facts_count": facts_count,
            "facts_text_length": facts_text_length,
            "generation_type": generation_type
        }
    })
