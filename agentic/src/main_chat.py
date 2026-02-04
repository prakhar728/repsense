"""Main entry point for the Fitness Data Assistant."""
import os
from dotenv import load_dotenv
import pandas as pd
import json

from .data_loader import load_and_normalize_csv, get_unsupported_exercises
from .data_analyzer import generate_user_profile
from .router import handle_user_query


def main():
    # Load environment
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize OpenAI client if key exists
    client = None
    if api_key:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        print("✓ OpenAI connected")
    else:
        print("⚠ No API key - running in mock mode")
    
    csv_path = "data/workout_data_normalized.csv"
    
    # # Load and normalize data
    # print("Loading data...")
    df = pd.read_csv(csv_path)
    # print(f"✓ Loaded {len(df)} sets from supported exercises")
    
    # # Generate profile
    # print("Generating user profile...")
    # profile = generate_user_profile(df)
    # print(f"✓ Profile: {len(profile['exercises'])} exercises, {len(profile['muscles'])} muscles")
    # print(f"  {profile['global']['summary']}")

    path = "data/user_profile.json"
    with open(path, "r") as f:
        profile = json.load(f)
    # # Show unsupported
    # unsupported = get_unsupported_exercises(csv_path)
    # if unsupported:
    #     print(f"\n⚠ {len(unsupported)} unmapped exercises (add to config.py later)")
    
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
        
        response = handle_user_query(query, df, profile, client)
        print(f"\n{response}\n")


if __name__ == "__main__":
    main()
