"""Data analysis - generates comprehensive user profile JSON."""
import pandas as pd
import json
from datetime import datetime, timedelta
from .config import EXERCISE_MUSCLE_MAP


def generate_user_profile(df: pd.DataFrame, output_path: str = None) -> dict:
    """Analyze DataFrame and generate comprehensive user profile."""
    now = datetime.now()
    weeks_tracked = max((df["start_time"].max() - df["start_time"].min()).days / 7, 1)

    profile = {
        "generated_at": now.isoformat(),
        "total_sets": len(df),
        "weeks_tracked": round(weeks_tracked, 1),
        "date_range": [str(df["start_time"].min().date()), str(df["start_time"].max().date())],
        "exercises": {},
        "muscles": {},
        "global": calculate_global_stats(df, weeks_tracked)
    }

    # Per-exercise stats
    for exercise_id in df["exercise_id"].unique():
        ex_df = df[df["exercise_id"] == exercise_id]
        profile["exercises"][exercise_id] = calculate_exercise_stats(ex_df, weeks_tracked)

    # Per-muscle stats
    for muscle in df["primary_muscle"].unique():
        muscle_df = df[df["primary_muscle"] == muscle]
        profile["muscles"][muscle] = calculate_muscle_stats(muscle_df, df, muscle, weeks_tracked)

    if output_path:
        with open(output_path, "w") as f:
            json.dump(profile, f, indent=2, default=str)

    return profile


def calculate_e1rm(weight: float, reps: int) -> float:
    """Calculate estimated 1RM using Epley formula."""
    if reps <= 0 or weight <= 0:
        return 0
    if reps == 1:
        return weight
    return weight * (1 + reps / 30)


def calculate_exercise_stats(df: pd.DataFrame, weeks_tracked: float) -> dict:
    """Calculate comprehensive stats for a single exercise."""
    df = df.copy()
    df["volume"] = df["weight_kg"] * df["reps"]
    df["e1rm"] = df.apply(lambda r: calculate_e1rm(r["weight_kg"], r["reps"]), axis=1)
    
    # Basic volume
    total_sets = len(df)
    total_reps = int(df["reps"].sum())
    total_volume = float(df["volume"].sum())
    
    # PRs
    valid = df[(df["reps"] > 0) & (df["weight_kg"] > 0)]
    pr_weight_row = valid.loc[valid["weight_kg"].idxmax()] if not valid.empty else None
    pr_volume_row = valid.loc[valid["volume"].idxmax()] if not valid.empty else None
    pr_e1rm_row = valid.loc[valid["e1rm"].idxmax()] if not valid.empty else None
    
    # Frequency & consistency
    sessions = df["start_time"].dt.date.nunique()
    frequency = round(sessions / weeks_tracked, 1)
    days_since_last = (datetime.now() - df["start_time"].max()).days
    
    # Trend analysis (last 4 weeks vs previous 4 weeks)
    trend = calculate_trend(df)
    
    # Rep distribution
    rep_dist = calculate_rep_distribution(df)
    
    # Recent sessions
    recent = get_recent_sessions(df, n=3)
    
    # Get top sets for detailed breakdown
    top_sets = get_top_sets(valid, n=5)
    
    # Build stats dict
    stats = {
        "total_sets": total_sets,
        "total_reps": total_reps,
        "total_volume_kg": round(total_volume, 1),
        
        "pr_weight": {
            "kg": float(pr_weight_row["weight_kg"]) if pr_weight_row is not None else 0,
            "reps": int(pr_weight_row["reps"]) if pr_weight_row is not None else 0,
            "date": str(pr_weight_row["start_time"].date()) if pr_weight_row is not None else None,
            "display": f"{pr_weight_row['weight_kg']}kg x {int(pr_weight_row['reps'])}" if pr_weight_row is not None else "N/A"
        },
        "pr_volume": {
            "kg": float(pr_volume_row["weight_kg"]) if pr_volume_row is not None else 0,
            "reps": int(pr_volume_row["reps"]) if pr_volume_row is not None else 0,
            "volume": float(pr_volume_row["volume"]) if pr_volume_row is not None else 0,
            "date": str(pr_volume_row["start_time"].date()) if pr_volume_row is not None else None,
            "display": f"{pr_volume_row['weight_kg']}kg x {int(pr_volume_row['reps'])} = {pr_volume_row['volume']}kg" if pr_volume_row is not None else "N/A"
        },
        "estimated_1rm": {
            "value": round(float(pr_e1rm_row["e1rm"]), 1) if pr_e1rm_row is not None else 0,
            "from_set": f"{pr_e1rm_row['weight_kg']}kg x {int(pr_e1rm_row['reps'])}" if pr_e1rm_row is not None else "N/A",
            "date": str(pr_e1rm_row["start_time"].date()) if pr_e1rm_row is not None else None
        },
        "top_sets": top_sets,
        
        "trend": trend,
        
        "frequency_per_week": frequency,
        "total_sessions": sessions,
        "days_since_last": days_since_last,
        
        "rep_distribution": rep_dist,
        "recent_sessions": recent
    }
    
    # Generate natural language summary
    stats["summary"] = generate_exercise_summary(stats)
    
    return stats


def calculate_trend(df: pd.DataFrame) -> dict:
    """Calculate trend comparing recent 4 weeks vs previous 4 weeks."""
    now = datetime.now()
    cutoff_recent = now - timedelta(days=28)
    cutoff_previous = now - timedelta(days=56)
    
    recent = df[df["start_time"] >= cutoff_recent]
    previous = df[(df["start_time"] >= cutoff_previous) & (df["start_time"] < cutoff_recent)]
    
    if recent.empty or previous.empty:
        return {"direction": "insufficient_data", "change_percent": 0}
    
    avg_recent = recent["weight_kg"].mean()
    avg_previous = previous["weight_kg"].mean()
    
    if avg_previous == 0:
        return {"direction": "insufficient_data", "change_percent": 0}
    
    change = ((avg_recent - avg_previous) / avg_previous) * 100
    
    if change > 5:
        direction = "increasing"
    elif change < -5:
        direction = "decreasing"
    else:
        direction = "plateau"
    
    return {
        "direction": direction,
        "avg_weight_recent": round(avg_recent, 1),
        "avg_weight_previous": round(avg_previous, 1),
        "change_percent": round(change, 1)
    }


def calculate_rep_distribution(df: pd.DataFrame) -> dict:
    """Calculate what percentage of sets fall into each rep range."""
    total = len(df)
    if total == 0:
        return {"heavy_1_5": 0, "moderate_6_10": 0, "light_11_plus": 0}
    
    heavy = len(df[(df["reps"] >= 1) & (df["reps"] <= 5)])
    moderate = len(df[(df["reps"] >= 6) & (df["reps"] <= 10)])
    light = len(df[df["reps"] > 10])
    
    return {
        "heavy_1_5": round(100 * heavy / total, 1),
        "moderate_6_10": round(100 * moderate / total, 1),
        "light_11_plus": round(100 * light / total, 1)
    }


def get_top_sets(df: pd.DataFrame, n: int = 5) -> list:
    """Get top n sets by weight."""
    if df.empty:
        return []
    top = df.nlargest(n, "weight_kg")
    return [
        {
            "weight_kg": float(row["weight_kg"]),
            "reps": int(row["reps"]),
            "volume": float(row["weight_kg"] * row["reps"]),
            "e1rm": round(calculate_e1rm(row["weight_kg"], row["reps"]), 1),
            "date": str(row["start_time"].date()),
            "display": f"{row['weight_kg']}kg x {int(row['reps'])}"
        }
        for _, row in top.iterrows()
    ]


def get_recent_sessions(df: pd.DataFrame, n: int = 3) -> list:
    """Get detailed summary of last n sessions."""
    sessions = []
    dates = df["start_time"].dt.date.unique()
    dates = sorted(dates, reverse=True)[:n]
    
    for date in dates:
        session_df = df[df["start_time"].dt.date == date].sort_values("set_index")
        sets_list = [
            f"{row['weight_kg']}kg x {int(row['reps'])}"
            for _, row in session_df.iterrows()
            if row["weight_kg"] > 0
        ]
        top_set = session_df.loc[session_df["weight_kg"].idxmax()]
        total_vol = (session_df["weight_kg"] * session_df["reps"]).sum()
        
        sessions.append({
            "date": str(date),
            "sets": sets_list,
            "sets_display": " → ".join(sets_list),
            "top_set": f"{top_set['weight_kg']}kg x {int(top_set['reps'])}",
            "total_sets": len(session_df),
            "session_volume": round(total_vol, 1)
        })
    
    return sessions


def generate_exercise_summary(stats: dict) -> str:
    """Generate natural language summary for an exercise."""
    parts = []
    
    # Frequency
    parts.append(f"Trained {stats['frequency_per_week']}x/week")
    
    # PR and e1RM
    pr = stats["pr_weight"]
    e1rm = stats["estimated_1rm"]
    if pr["kg"] > 0:
        parts.append(f"PR: {pr['display']}")
    if e1rm["value"] > 0 and e1rm["value"] != pr["kg"]:
        parts.append(f"Est. 1RM: {e1rm['value']}kg (from {e1rm['from_set']})")
    
    # Trend
    trend = stats["trend"]
    if trend["direction"] != "insufficient_data":
        if trend["direction"] == "increasing":
            parts.append(f"Trending up (+{trend['change_percent']}%)")
        elif trend["direction"] == "decreasing":
            parts.append(f"Trending down ({trend['change_percent']}%)")
        else:
            parts.append("Plateau")
    
    # Rep style
    rep_dist = stats["rep_distribution"]
    if rep_dist["heavy_1_5"] > 50:
        parts.append("Favors heavy singles/doubles")
    elif rep_dist["moderate_6_10"] > 50:
        parts.append("Favors moderate reps (6-10)")
    elif rep_dist["light_11_plus"] > 50:
        parts.append("Favors high reps (11+)")
    
    # Recency
    days = stats["days_since_last"]
    if days > 14:
        parts.append(f"Not trained in {days} days")
    elif days > 7:
        parts.append(f"Last trained {days} days ago")
    
    return ". ".join(parts) + "."


def calculate_muscle_stats(muscle_df: pd.DataFrame, full_df: pd.DataFrame, muscle: str, weeks_tracked: float) -> dict:
    """Calculate comprehensive stats for a muscle group."""
    exercises = muscle_df["exercise_id"].unique().tolist()
    total_sets = len(muscle_df)
    percentage = round(100 * total_sets / len(full_df), 1)
    weekly_avg = round(total_sets / weeks_tracked, 1)
    
    # Find dominant exercise
    exercise_counts = muscle_df["exercise_id"].value_counts()
    dominant = exercise_counts.index[0] if len(exercise_counts) > 0 else None
    dominant_pct = round(100 * exercise_counts.iloc[0] / total_sets, 1) if dominant else 0
    
    # Determine status based on weekly sets (rough guidelines)
    recommended = get_recommended_sets(muscle)
    if weekly_avg < recommended["min"]:
        status = "undertrained"
    elif weekly_avg > recommended["max"]:
        status = "high_volume"
    else:
        status = "optimal"
    
    stats = {
        "exercises": exercises,
        "total_sets": total_sets,
        "percentage_of_training": percentage,
        "weekly_sets_avg": weekly_avg,
        "dominant_exercise": dominant,
        "dominant_exercise_percent": dominant_pct,
        "recommended_weekly_sets": f"{recommended['min']}-{recommended['max']}",
        "status": status
    }
    
    # Summary
    stats["summary"] = f"{muscle.title()}: {percentage}% of training ({weekly_avg} sets/week). " \
                       f"{dominant} is dominant ({dominant_pct}%). Status: {status}."
    
    return stats


def get_recommended_sets(muscle: str) -> dict:
    """Return rough recommended weekly set ranges per muscle."""
    # Based on general hypertrophy guidelines
    recommendations = {
        "chest": {"min": 10, "max": 20},
        "shoulders": {"min": 8, "max": 16},
        "triceps": {"min": 6, "max": 12},
        "biceps": {"min": 6, "max": 12},
        "lats": {"min": 10, "max": 20},
        "upper_back": {"min": 10, "max": 20},
        "traps": {"min": 6, "max": 12},
        "quads": {"min": 10, "max": 20},
        "hamstrings": {"min": 8, "max": 16},
        "glutes": {"min": 8, "max": 16},
        "lower_back": {"min": 6, "max": 12},
        "core": {"min": 6, "max": 12},
        "forearms": {"min": 4, "max": 10}
    }
    return recommendations.get(muscle, {"min": 8, "max": 16})


def calculate_global_stats(df: pd.DataFrame, weeks_tracked: float) -> dict:
    """Calculate global training insights."""
    # Sessions per week
    total_sessions = df["start_time"].dt.date.nunique()
    sessions_per_week = round(total_sessions / weeks_tracked, 1)
    
    # Push/Pull classification
    push_muscles = ["chest", "shoulders", "triceps"]
    pull_muscles = ["lats", "upper_back", "biceps", "forearms"]
    leg_muscles = ["quads", "hamstrings", "glutes"]
    
    push_sets = len(df[df["primary_muscle"].isin(push_muscles)])
    pull_sets = len(df[df["primary_muscle"].isin(pull_muscles)])
    leg_sets = len(df[df["primary_muscle"].isin(leg_muscles)])
    upper_sets = push_sets + pull_sets
    
    push_pull_ratio = round(push_sets / pull_sets, 2) if pull_sets > 0 else 0
    upper_lower_ratio = round(upper_sets / leg_sets, 2) if leg_sets > 0 else 0
    
    # Find undertrained muscles
    muscle_weekly = df.groupby("primary_muscle").size() / weeks_tracked
    undertrained = []
    for muscle, weekly in muscle_weekly.items():
        rec = get_recommended_sets(muscle)
        if weekly < rec["min"]:
            undertrained.append(muscle)
    
    # Overall trend (simplified - based on total volume trend)
    stats = {
        "avg_sessions_per_week": sessions_per_week,
        "total_sessions": total_sessions,
        "weeks_tracked": round(weeks_tracked, 1),
        "push_pull_ratio": push_pull_ratio,
        "upper_lower_ratio": upper_lower_ratio,
        "push_sets": push_sets,
        "pull_sets": pull_sets,
        "leg_sets": leg_sets,
        "undertrained_muscles": undertrained
    }
    
    # Summary
    balance = "balanced" if 0.8 <= push_pull_ratio <= 1.2 else ("push dominant" if push_pull_ratio > 1.2 else "pull dominant")
    focus = "balanced" if 0.8 <= upper_lower_ratio <= 1.5 else ("upper focused" if upper_lower_ratio > 1.5 else "lower focused")
    
    stats["summary"] = f"Training {sessions_per_week}x/week for {round(weeks_tracked)} weeks. " \
                       f"Push/Pull: {balance} ({push_pull_ratio}:1). " \
                       f"Upper/Lower: {focus} ({upper_lower_ratio}:1). " \
                       f"Undertrained: {', '.join(undertrained) if undertrained else 'none'}."
    
    return stats


def load_user_profile(path: str = "data/user_profile.json") -> dict:
    """Load pre-computed profile from JSON."""
    with open(path, "r") as f:
        return json.load(f)
