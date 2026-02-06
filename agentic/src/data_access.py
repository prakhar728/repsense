"""Data access - filtering and retrieval."""
import json
import pandas as pd
from datetime import datetime, timedelta
from .config import EXERCISE_MUSCLE_MAP


EXTRACTION_PROMPT = """Extract query parameters from a fitness question.

Available exercises: {exercises}
Available muscles: {muscles}

Return JSON with this structure:
{{
  "target_type": "exercise" | "muscle" | "muscle_group" | "all",
  "target_values": ["<exercise_id or muscle name>"],
  "timeframe": "last_week" | "last_month" | "this_week" | "this_month" | "all"
}}

IMPORTANT: target_values is ALWAYS an array, even for single targets.

Muscle groups:
- "push": ["chest", "shoulders", "triceps"]
- "pull": ["back", "lats", "traps", "biceps"]
- "legs": ["quads", "hamstrings", "glutes"]

Examples:
"show bench press history" → {{"target_type": "exercise", "target_values": ["bench_press"], "timeframe": "all"}}
"chest exercises last week" → {{"target_type": "muscle", "target_values": ["chest"], "timeframe": "last_week"}}
"give me a push workout" → {{"target_type": "muscle_group", "target_values": ["chest", "shoulders", "triceps"], "timeframe": "all"}}
"what did I do this month" → {{"target_type": "all", "target_values": [], "timeframe": "this_month"}}

Respond with ONLY the JSON, no explanation."""


def extract_query_params(query: str, client=None) -> dict:
    """Extract targets (can be multiple) and timeframe from query."""
    if client is None:
        return _extract_mock(query)

    exercises = [info["exercise_id"] for info in EXERCISE_MUSCLE_MAP.values()]
    muscles = list(set(info["primary_muscle"] for info in EXERCISE_MUSCLE_MAP.values()))

    prompt = EXTRACTION_PROMPT.format(
        exercises=", ".join(exercises),
        muscles=", ".join(muscles)
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ],
        max_tokens=150
    )

    try:
        result = json.loads(response.choices[0].message.content.strip())
        target_type = result.get("target_type", "all")
        target_values = result.get("target_values", [])

        # Convert to targets list format
        targets = []
        if target_type != "all" and target_values:
            for value in target_values:
                targets.append({"type": target_type.replace("muscle_group", "muscle"), "value": value})

        return {
            "targets": targets,
            "timeframe": {"type": "relative" if result.get("timeframe", "all") != "all" else "all",
                         "value": result.get("timeframe")}
        }
    except:
        return _extract_mock(query)


def _extract_mock(query: str) -> dict:
    """Fallback keyword-based extraction with multi-target support."""
    targets = []
    query_lower = query.lower()

    # Check for muscle groups first
    muscle_groups = {
        "push": ["chest", "shoulders", "triceps"],
        "pull": ["back", "lats", "traps", "biceps"],
        "legs": ["quads", "hamstrings", "glutes"],
        "leg": ["quads", "hamstrings", "glutes"]  # Singular form
    }

    for group_name, muscles in muscle_groups.items():
        if group_name in query_lower:
            for muscle in muscles:
                targets.append({"type": "muscle", "value": muscle})
            break

    # If no group found, check for specific exercises
    if not targets:
        for title, info in EXERCISE_MUSCLE_MAP.items():
            if info["exercise_id"].replace("_", " ") in query_lower or title.lower() in query_lower:
                targets.append({"type": "exercise", "value": info["exercise_id"]})
                break

    # If no exercise found, check for specific muscles
    if not targets:
        muscles = ["chest", "biceps", "triceps", "shoulders", "back", "lats", "traps", "quads", "hamstrings", "glutes"]
        for muscle in muscles:
            if muscle in query_lower:
                targets.append({"type": "muscle", "value": muscle})
                break

    # Timeframe extraction
    timeframe = {"type": "all", "value": None}
    if "last week" in query_lower:
        timeframe = {"type": "relative", "value": "last_week"}
    elif "last month" in query_lower:
        timeframe = {"type": "relative", "value": "last_month"}

    return {
        "targets": targets,
        "timeframe": timeframe
    }


def apply_timeframe_filter(df: pd.DataFrame, timeframe: dict) -> pd.DataFrame:
    """Filter DataFrame by timeframe."""
    if timeframe["type"] == "all" or timeframe["value"] == "all":
        return df
    
    now = datetime.now()
    value = timeframe["value"]
    
    if value == "last_week":
        cutoff = now - timedelta(days=7)
    elif value == "last_month":
        cutoff = now - timedelta(days=30)
    elif value == "this_week":
        cutoff = now - timedelta(days=now.weekday())
    elif value == "this_month":
        cutoff = now.replace(day=1)
    else:
        return df
    
    return df[df["start_time"] >= cutoff]


def get_exercise_history(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Filter DataFrame based on extracted params (supports multiple targets)."""
    result = apply_timeframe_filter(df, params["timeframe"])

    targets = params.get("targets", [])
    if not targets:
        return result.sort_values("start_time", ascending=False)

    # Collect matching rows for all targets
    mask = pd.Series([False] * len(result), index=result.index)

    for target in targets:
        if target["type"] == "exercise" and target["value"]:
            mask |= (result["exercise_id"] == target["value"])
        elif target["type"] == "muscle" and target["value"]:
            mask |= (result["primary_muscle"] == target["value"])

    result = result[mask]
    return result.sort_values("start_time", ascending=False)


def format_history_response(df: pd.DataFrame) -> str:
    """Format DataFrame as readable text with set-by-set breakdown."""
    if df.empty:
        return "No matching records found."
    
    lines = []
    
    for (date, exercise), group in df.groupby([df["start_time"].dt.date, "exercise_title"]):
        group = group.sort_values("set_index")
        
        sets = [f"{row['weight_kg']}kg x {int(row['reps'])}" 
                for _, row in group.iterrows() if row["weight_kg"] > 0]
        
        sets_str = " → ".join(sets) if sets else "No weight data"
        total_vol = (group["weight_kg"] * group["reps"]).sum()
        max_weight = group["weight_kg"].max()
        
        lines.append(f"\n{date} | {exercise}")
        lines.append(f"  Sets: {sets_str}")
        lines.append(f"  Summary: {len(group)} sets, max {max_weight}kg, volume {total_vol:.0f}kg")
    
    return "\n".join(lines)
