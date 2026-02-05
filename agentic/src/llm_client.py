"""Centralized LLM client with optional Opik instrumentation.

This module provides a single source of truth for the OpenAI client,
with automatic Opik tracing when OPIK_ENABLED=1 is set.

Usage:
    from .llm_client import get_client

    client = get_client()
    # All calls through this client are automatically traced when Opik is enabled
"""
import os
from typing import Optional

_client = None
_initialized = False


def get_client(api_key: Optional[str] = None):
    """
    Get the singleton OpenAI client with optional Opik instrumentation.

    The client is lazily initialized on first call and cached for subsequent calls.
    When OPIK_ENABLED=1 is set, the client is wrapped with Opik's track_openai
    for automatic LLM call tracing.

    Args:
        api_key: Optional API key. If not provided, uses OPENAI_API_KEY env var.
                 Only used on first initialization.

    Returns:
        OpenAI client instance, or None if no API key is available.
    """
    global _client, _initialized

    if _initialized:
        return _client

    # Get API key from parameter or environment
    key = api_key or os.getenv("OPENAI_API_KEY")

    if not key:
        _initialized = True
        _client = None
        return None

    # Create base OpenAI client
    from openai import OpenAI
    _client = OpenAI(api_key=key)

    # Wrap with Opik if enabled
    if os.getenv("OPIK_ENABLED", "").lower() in ("1", "true", "yes"):
        try:
            from opik.integrations.openai import track_openai

            # Set default project name if not already set
            if not os.getenv("OPIK_PROJECT_NAME"):
                os.environ["OPIK_PROJECT_NAME"] = "Repsense"

            _client = track_openai(_client)
        except ImportError:
            # Opik not installed, continue without instrumentation
            pass

    _initialized = True
    return _client


def reset_client():
    """Reset the client singleton (useful for testing)."""
    global _client, _initialized
    _client = None
    _initialized = False


def is_opik_enabled() -> bool:
    """Check if Opik instrumentation is enabled."""
    return os.getenv("OPIK_ENABLED", "").lower() in ("1", "true", "yes")
