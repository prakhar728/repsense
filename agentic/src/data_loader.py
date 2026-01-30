"""CSV ingestion and normalization."""
import pandas as pd
from .config import EXERCISE_MUSCLE_MAP, DATE_FORMAT


def load_and_normalize_csv(filepath: str) -> pd.DataFrame:
    """Load CSV, filter to supported exercises, add canonical columns."""
    df = pd.read_csv(filepath)
    
    # Filter to supported exercises only
    df = df[df["exercise_title"].isin(EXERCISE_MUSCLE_MAP.keys())].copy()
    
    # Add canonical columns from mapping
    df["exercise_id"] = df["exercise_title"].map(lambda x: EXERCISE_MUSCLE_MAP[x]["exercise_id"])
    df["primary_muscle"] = df["exercise_title"].map(lambda x: EXERCISE_MUSCLE_MAP[x]["primary_muscle"])
    
    # Parse dates
    df["start_time"] = pd.to_datetime(df["start_time"], format=DATE_FORMAT)
    df["end_time"] = pd.to_datetime(df["end_time"], format=DATE_FORMAT)
    
    # Fill NaN
    df["weight_kg"] = df["weight_kg"].fillna(0)
    df["reps"] = df["reps"].fillna(0)
    
    return df


def get_unsupported_exercises(filepath: str) -> list[str]:
    """Return exercises in CSV not in our mapping."""
    df = pd.read_csv(filepath)
    all_exercises = df["exercise_title"].unique()
    return [e for e in all_exercises if e not in EXERCISE_MUSCLE_MAP]
