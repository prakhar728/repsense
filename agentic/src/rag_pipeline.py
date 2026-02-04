"""RAG pipeline - fact extraction and advice generation."""
from .data_analyzer import load_user_profile
import json

COACH_PROMPT = """You are an experienced strength coach analyzing a user's training data.

RULES:
- Base advice ONLY on the provided facts
- Be specific and actionable
- Give 1-2 concrete recommendations
- Reference their actual numbers
- Keep response concise (3-5 sentences)

USER'S TRAINING DATA:
{facts}

Answer their question based on this data."""


def get_relevant_facts(params: dict, profile: dict) -> list[str]:
    """Extract rich, relevant facts from profile based on query params."""
    facts = []
    target = params["target"]
    
    g = profile["global"]
    facts.append(f"[Global] {g['summary']}")
    
    if target["type"] == "exercise" and target["value"] in profile["exercises"]:
        ex = profile["exercises"][target["value"]]
        facts.append(f"[Exercise: {target['value']}] {ex['summary']}")
        facts.append(f"  - Total: {ex['total_sets']} sets, {ex['total_reps']} reps, {ex['total_volume_kg']}kg total volume")
        facts.append(f"  - PR (heaviest): {ex['pr_weight']['display']} on {ex['pr_weight']['date']}")
        facts.append(f"  - PR (best volume set): {ex['pr_volume']['display']} on {ex['pr_volume']['date']}")
        facts.append(f"  - Estimated 1RM: {ex['estimated_1rm']['value']}kg (from {ex['estimated_1rm']['from_set']})")
        facts.append(f"  - Trend: {ex['trend']['direction']} ({ex['trend']['change_percent']}% change)")
        facts.append(f"  - Rep style: Heavy(1-5) {ex['rep_distribution']['heavy_1_5']}%, Moderate(6-10) {ex['rep_distribution']['moderate_6_10']}%, Light(11+) {ex['rep_distribution']['light_11_plus']}%")
        
        if ex.get("top_sets"):
            top_str = ", ".join([f"{s['display']} (e1RM:{s['e1rm']})" for s in ex["top_sets"][:3]])
            facts.append(f"  - Top sets: {top_str}")
        
        if ex["recent_sessions"]:
            for session in ex["recent_sessions"][:2]:
                facts.append(f"  - Session {session['date']}: {session['sets_display']} (vol: {session['session_volume']}kg)")
    
    elif target["type"] == "muscle" and target["value"] in profile["muscles"]:
        m = profile["muscles"][target["value"]]
        facts.append(f"[Muscle: {target['value']}] {m['summary']}")
        facts.append(f"  - Exercises: {', '.join(m['exercises'])}")
        facts.append(f"  - Weekly sets: {m['weekly_sets_avg']} (recommended: {m['recommended_weekly_sets']})")
        facts.append(f"  - Status: {m['status']}")
        
        for ex_id in m["exercises"]:
            if ex_id in profile["exercises"]:
                ex = profile["exercises"][ex_id]
                facts.append(f"  - {ex_id}: {ex['summary']}")
    
    else:
        facts.append(f"[Training Overview]")
        facts.append(f"  - Sessions: {g['total_sessions']} over {g['weeks_tracked']} weeks")
        facts.append(f"  - Push/Pull ratio: {g['push_pull_ratio']}:1")
        facts.append(f"  - Upper/Lower ratio: {g['upper_lower_ratio']}:1")
        
        if g["undertrained_muscles"]:
            facts.append(f"  - Undertrained: {', '.join(g['undertrained_muscles'])}")
        
        exercises = profile["exercises"]
        sorted_ex = sorted(exercises.items(), key=lambda x: x[1]["total_volume_kg"], reverse=True)[:3]
        top_str = ", ".join([f"{e[0]} ({e[1]['total_volume_kg']}kg)" for e in sorted_ex])
        facts.append(f"  - Top exercises: {top_str}")
    
    return facts


def generate_advice(query: str, facts: list[str], client=None) -> str:
    """Generate advice based on query and facts."""
    facts_text = "\n".join(facts)
    
    if client is None:
        return f"Based on your data:\n\n{facts_text}\n\n[LLM not connected - add OPENAI_API_KEY to .env for real advice]"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": COACH_PROMPT.format(facts=facts_text)},
            {"role": "user", "content": query}
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content.strip()

def generate_routine(
    query: str,
    facts: list[str],
    client=None
) -> dict:
    """
    Generate a structured training plan (single session, weekly plan, or multi-week program)
    based ONLY on extracted facts and the user's request.
    """

    # return {
    #     "TEST_MARKER": "GENERATE_TRAINING_PLAN_CALLED",
    #     "query": query,
    #     "facts_count": len(facts)
    # }

    facts_text = "\n".join(facts)
    query_text = query

    PLAN_PROMPT = f"""You are an expert strength coach designing a TRAINING PLAN.

    RULES:
    - Base ALL decisions ONLY on the provided facts
    - Do NOT assume missing information
    - Infer plan duration and structure from the user's request
    - Prefer exercises mentioned in the facts
    - Address imbalances or undertrained muscles if present in facts
    - Keep volume realistic
    - For suggested_weight_kg, use the user's actual numbers from the facts (recent sessions, PRs) to recommend appropriate working weights. If no data exists for an exercise, set to null.

    OUTPUT RULES:
    - Output VALID JSON ONLY
    - Do NOT include explanations outside JSON
    - Follow the schema exactly

    TRAINING PLAN JSON SCHEMA:
    {{
    "title": string,
    "goal": string,
    "level": string,
    "plan_type": "single_session" | "weekly_plan" | "multi_week_program",
    "duration": {{
        "weeks": number | null,
        "days_per_week": number | null
    }},
    "sessions": [
        {{
        "day": string,
        "focus": string,
        "exercises": [
            {{
            "name": string,
            "primary_muscle": string,
            "sets": number,
            "reps": string,
            "suggested_weight_kg": number | null,
            "rest_seconds": number,
            "notes": string
            }}
        ]
        }}
    ]
    }}

    FACTS:
    {facts_text}

    USER REQUEST:
    {query}
    """

    if client is None:
        # Safe deterministic fallback
        return {
            "title": "Full Body Training Plan",
            "goal": "general_strength",
            "level": "intermediate",
            "plan_type": "single_session",
            "duration": {
                "weeks": None,
                "days_per_week": None
            },
            "sessions": [
                {
                    "day": "Session 1",
                    "focus": "Full Body",
                    "exercises": [
                        {
                            "name": "Squat",
                            "primary_muscle": "legs",
                            "sets": 4,
                            "reps": "6-8",
                            "rest_seconds": 150,
                            "notes": "Progress when all reps feel solid"
                        }
                    ]
                }
            ]
        }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": PLAN_PROMPT
            }
        ],
        max_tokens=1200
    )

    return json.loads(response.choices[0].message.content.strip())
