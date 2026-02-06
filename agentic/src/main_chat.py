"""Main entry point for the Fitness Data Assistant."""
import os
from dotenv import load_dotenv
import pandas as pd
import json
from typing import Optional, List, Dict, Any

from .router import handle_user_query
from .llm_client import get_client
from .tracing import maybe_track


@maybe_track(name="chat_turn")
def run_chat_turn(
    query: str,
    profile: dict,
    client=None,
    override_intent: Optional[str] = None,
    episodes: Optional[List[Dict[str, Any]]] = None
) -> dict:
    return handle_user_query(query, profile, client, override_intent=override_intent, episodes=episodes)


def main():
    # Load environment
    load_dotenv()

    # Use centralized client
    client = get_client()
    if client:
        print("✓ OpenAI connected")
    else:
        print("⚠ No API key - running in mock mode")

    path = "data/user_profile.json"
    with open(path, "r") as f:
        profile = json.load(f)

    # Interactive loop
    print("\n" + "="*60)
    print("Fitness Data Assistant" + (" (LLM Mode)" if client else " (Mock Mode)"))
    print("="*60)
    print("Examples:")
    print("  • show bench press history")
    print("  • how can I improve my squat?")
    print("  • am I training chest enough?")
    print("Type 'quit' to exit\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in ["quit", "exit", "q"]:
            break
        if not query:
            continue

        response = handle_user_query(query, profile, client)
        print(f"\n{response}\n")


if __name__ == "__main__":
    main()
