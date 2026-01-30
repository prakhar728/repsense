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
  "target_type": "exercise" | "muscle" | "all",
  "target_value": "<exercise_id or muscle name or null>",
  "timeframe": "last_week" | "last_month" | "this_week" | "this_month" | "all"
}}

Examples:
"show bench press history" → {{"target_type": "exercise", "target_value": "bench_press", "timeframe": "all"}}
"chest exercises last week" → {{"target_type": "muscle", "target_value": "chest", "timeframe": "last_week"}}
"what did I do this month" → {{"target_type": "all", "target_value": null, "timeframe": "this_month"}}

Respond with ONLY the JSON, no explanation."""


def extract_query_params(query: str, client=None) -> dict:
    """Extract target and timeframe from query."""
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
        max_tokens=100
    )
    
    try:
        result = json.loads(response.choices[0].message.content.strip())
        return {
            "target": {"type": result.get("target_type", "all"), "value": result.get("target_value")},
            "timeframe": {"type": "relative" if result.get("timeframe", "all") != "all" else "all", 
                         "value": result.get("timeframe")}
        }
    except:
        return _extract_mock(query)


def _extract_mock(query: str) -> dict:
    """Fallback keyword-based extraction."""
    params = {
        "target": {"type": "all", "value": None},
        "timeframe": {"type": "all", "value": None}
    }
    
    query_lower = query.lower()
    
    for title, info in EXERCISE_MUSCLE_MAP.items():
        if info["exercise_id"].replace("_", " ") in query_lower or title.lower() in query_lower:
            params["target"] = {"type": "exercise", "value": info["exercise_id"]}
            break
    
    muscles = ["chest", "biceps", "triceps", "shoulders", "lats", "traps", "quads", "hamstrings", "glutes"]
    for muscle in muscles:
        if muscle in query_lower:
            params["target"] = {"type": "muscle", "value": muscle}
            break
    
    if "last week" in query_lower:
        params["timeframe"] = {"type": "relative", "value": "last_week"}
    elif "last month" in query_lower:
        params["timeframe"] = {"type": "relative", "value": "last_month"}
    
    return params


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
    """Filter DataFrame based on extracted params."""
    result = apply_timeframe_filter(df, params["timeframe"])
    
    target = params["target"]
    if target["type"] == "exercise" and target["value"]:
        result = result[result["exercise_id"] == target["value"]]
    elif target["type"] == "muscle" and target["value"]:
        result = result[result["primary_muscle"] == target["value"]]
    
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
