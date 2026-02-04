"""Main entry point for the Fitness Data Assistant."""
import os

from .data_loader import load_and_normalize_csv, get_unsupported_exercises
from .data_analyzer import generate_user_profile

def run_profile_generation(csv_path: str, output_path: str = None) -> dict:
    df = load_and_normalize_csv(csv_path)
    profile = generate_user_profile(df, output_path)

    if output_path:
        import json
        with open(output_path, "w") as f:
            json.dump(profile, f, indent=2)

    return profile


def main():
    
    csv_path = "data/workout_data.csv"
    
    # Load and normalize data
    print("Loading data...")
    df = load_and_normalize_csv(csv_path)
    df.to_csv("data/workout_data_normalized.csv", index=False)
    print(f"✓ Loaded {len(df)} sets from supported exercises")
    
    # Generate profile
    print("Generating user profile...")
    profile = generate_user_profile(df)
    print(f"✓ Profile: {len(profile['exercises'])} exercises, {len(profile['muscles'])} muscles")
    print(f"  {profile['global']['summary']}")
    
    # Show unsupported
    unsupported = get_unsupported_exercises(csv_path)
    if unsupported:
        print(f"\n⚠ {len(unsupported)} unmapped exercises (add to config.py later)")
    

if __name__ == "__main__":
    main()
