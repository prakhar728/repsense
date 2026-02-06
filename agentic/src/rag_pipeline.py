"""RAG pipeline - fact extraction and advice generation."""
from typing import Tuple, Optional, List, Dict, Any
import json

from .data_analyzer import load_user_profile
from .tracing import maybe_track, update_current_span, log_generation_context


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


@maybe_track(name="get_relevant_facts")
def get_relevant_facts(params: dict, profile: dict) -> list[str]:
    """Extract rich, relevant facts from profile based on query params (supports multiple targets)."""
    facts = []
    targets = params.get("targets", [])

    g = profile["global"]
    facts.append(f"[Global] {g['summary']}")

    if not targets:
        # No specific targets - show training overview
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
    else:
        # Process each target
        for target in targets:
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

    # Log facts extraction
    facts_text = "\n".join(facts)
    log_generation_context(
        facts_count=len(facts),
        facts_text_length=len(facts_text),
        generation_type="extraction"
    )
    update_current_span(metadata={
        "facts_extracted": len(facts),
        "targets_count": len(targets),
        "target_types": [t["type"] for t in targets],
        "target_values": [t["value"] for t in targets],
        "facts_preview": facts[:3]  # First 3 facts for context
    })

    return facts


@maybe_track(name="generate_advice")
def generate_advice(query: str, facts: list[str], client=None) -> Tuple[str, str]:
    """
    Generate advice based on query and facts.

    Returns:
        Tuple of (advice_text, generation_method)
    """
    facts_text = "\n".join(facts)

    # Log generation context
    log_generation_context(
        facts_count=len(facts),
        facts_text_length=len(facts_text),
        generation_type="advice"
    )
    update_current_span(metadata={
        "generation_type": "advice",
        "facts_count": len(facts),
        "facts_text_length": len(facts_text),
        "query_length": len(query)
    })

    if client is None:
        result = f"Based on your data:\n\n{facts_text}\n\n[LLM not connected - add OPENAI_API_KEY to .env for real advice]"
        return result, "mock"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": COACH_PROMPT.format(facts=facts_text)},
                {"role": "user", "content": query}
            ],
            max_tokens=300
        )

        advice = response.choices[0].message.content.strip()
        update_current_span(metadata={
            "advice_length": len(advice),
            "generation_method": "llm"
        })
        return advice, "llm"
    except Exception as e:
        update_current_span(metadata={
            "generation_method": "llm_error",
            "error": str(e)
        })
        return f"Error generating advice: {str(e)}", "llm_error"


@maybe_track(name="generate_routine")
def generate_routine(
    query: str,
    facts: list[str],
    client=None,
    episodes: Optional[List[Dict[str, Any]]] = None
) -> Tuple[dict, str]:
    """
    Generate a structured training plan (single session, weekly plan, or multi-week program)
    based ONLY on extracted facts and the user's request.

    Args:
        query: Enriched query string
        facts: List of extracted facts about user's training data
        client: OpenAI client
        episodes: Optional list of formatted episodes with past feedback

    Returns:
        Tuple of (routine_dict, generation_method)
    """
    facts_text = "\n".join(facts)

    # Format episodes for prompt
    episodes_text = ""
    if episodes:
        episode_lines = []
        for ep in episodes[:5]:  # Limit to 5 most recent
            title = ep.get("routine_title", "Unknown")
            muscles = ep.get("muscles", "")
            outcome = ep.get("outcome_text", "")
            episode_lines.append(f"- {title} ({muscles}): {outcome}")
        episodes_text = "\n".join(episode_lines)

    # Log generation context
    log_generation_context(
        facts_count=len(facts),
        facts_text_length=len(facts_text),
        generation_type="routine"
    )
    update_current_span(metadata={
        "generation_type": "routine",
        "facts_count": len(facts),
        "facts_text_length": len(facts_text),
        "query_length": len(query),
        "episodes_count": len(episodes) if episodes else 0,
        "episodes_included": bool(episodes_text)
    })

    PLAN_PROMPT = f"""You are an expert strength coach designing a TRAINING PLAN.

    RULES:
    - Base ALL decisions ONLY on the provided facts and previous feedback
    - Do NOT assume missing information
    - Infer plan duration and structure from the user's request
    - Prefer exercises mentioned in the facts
    - Address imbalances or undertrained muscles if present in facts
    - Keep volume realistic
    - For suggested_weight_kg, use the user's actual numbers from the facts (recent sessions, PRs) to recommend appropriate working weights. If no data exists for an exercise, set to null.
    - IMPORTANT: If previous feedback indicates routines were too hard/easy, adjust volume and intensity accordingly

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

    {f'''PREVIOUS FEEDBACK:
{episodes_text}

IMPORTANT: Use this feedback to adjust volume and intensity. If past routines were "too hard", reduce sets/reps by 20-30%. If they "worked well", maintain similar volume. If "too easy", increase volume by 10-20%.
''' if episodes_text else ''}

    USER REQUEST:
    {query}
    """

    if client is None:
        # Safe deterministic fallback
        routine = {
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
        return routine, "mock"

    try:
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

        routine = json.loads(response.choices[0].message.content.strip())

        # Log routine details
        update_current_span(metadata={
            "routine_title": routine.get("title"),
            "routine_type": routine.get("plan_type"),
            "sessions_count": len(routine.get("sessions", [])),
            "total_exercises": sum(
                len(s.get("exercises", []))
                for s in routine.get("sessions", [])
            ),
            "generation_method": "llm"
        })

        return routine, "llm"
    except json.JSONDecodeError as e:
        update_current_span(metadata={
            "generation_method": "llm_json_error",
            "error": str(e)
        })
        # Return fallback on parse error
        return {
            "title": "Training Plan",
            "goal": "general",
            "level": "intermediate",
            "plan_type": "single_session",
            "duration": {"weeks": None, "days_per_week": None},
            "sessions": [],
            "_error": "Failed to parse LLM response"
        }, "llm_json_error"
    except Exception as e:
        update_current_span(metadata={
            "generation_method": "llm_error",
            "error": str(e)
        })
        return {
            "title": "Training Plan",
            "goal": "general",
            "level": "intermediate",
            "plan_type": "single_session",
            "duration": {"weeks": None, "days_per_week": None},
            "sessions": [],
            "_error": str(e)
        }, "llm_error"
