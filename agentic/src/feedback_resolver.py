"""Feedback resolution - ranking and routine matching."""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .tracing import maybe_track, update_current_span, log_scoring_breakdown
from .tracing_models import ScoreBreakdown, ScoredCandidate


@maybe_track(name="rank_routine_candidates")
def rank_routine_candidates(
    candidates: List[Dict[str, Any]], target_signals: dict, chat_id: str, routine_in_chat_check
) -> List[Dict[str, Any]]:
    """
    Rank routine candidates deterministically.

    Scoring:
    1. Recency (0-100)
    2. Same-chat proximity (+50)
    3. Missing outcome bonus (+30)
    4. Target signal match (0-100)
    5. Negation penalty (-1000)

    Returns candidates with 'score' and 'score_breakdown' fields.
    """
    now = datetime.utcnow()
    scored_candidates = []

    for candidate in candidates:
        score_breakdown = ScoreBreakdown()

        # 1. Recency Score (0-100)
        try:
            last_mentioned_str = candidate["last_mentioned_at"]
            if "Z" in last_mentioned_str:
                last_mentioned = datetime.fromisoformat(last_mentioned_str.replace("Z", "+00:00"))
                if last_mentioned.tzinfo:
                    last_mentioned = last_mentioned.replace(tzinfo=None)
            else:
                last_mentioned = datetime.fromisoformat(last_mentioned_str)
            days_since = (now - last_mentioned).days
            score_breakdown.recency = max(0, 100 * (1 - days_since / 60))
        except (ValueError, KeyError, TypeError, AttributeError):
            pass

        # 2. Same-Chat Proximity (+50)
        if routine_in_chat_check(chat_id, candidate["id"]):
            score_breakdown.same_chat = 50

        # 3. Missing Outcome Bonus (+30)
        if candidate.get("existing_outcomes", 0) == 0:
            score_breakdown.missing_outcome = 30

        # 4. Target Signal Match (0-100)
        routine_json = candidate.get("routine_json", {})
        routine_muscles = set()
        routine_exercises = set()

        for session in routine_json.get("sessions", []):
            for exercise in session.get("exercises", []):
                muscle = exercise.get("primary_muscle", "").lower()
                if muscle:
                    routine_muscles.add(muscle)
                exercise_name = exercise.get("name", "").lower()
                if exercise_name:
                    routine_exercises.add(exercise_name)

        mentioned_muscles = [m.lower() for m in target_signals.get("mentioned_muscles", [])]
        mentioned_exercises = [e.lower() for e in target_signals.get("mentioned_exercises", [])]

        total_signals = len(mentioned_muscles) + len(mentioned_exercises)
        matched_signals = 0

        if total_signals > 0:
            for muscle in mentioned_muscles:
                if muscle in routine_muscles:
                    matched_signals += 1
            for exercise in mentioned_exercises:
                if any(ex in routine_exercises for ex in [exercise, exercise.replace(" ", "_")]):
                    matched_signals += 1

            score_breakdown.target_match = 100 * (matched_signals / total_signals)

        # 5. Negation Penalty (-1000)
        negations = [n.lower() for n in target_signals.get("negations", [])]
        for negation in negations:
            routine_title = routine_json.get("title", "").lower()
            if negation in routine_title or any(negation in m for m in routine_muscles):
                score_breakdown.negation = -1000
                break

        # Calculate total
        score_breakdown.total = (
            score_breakdown.recency +
            score_breakdown.same_chat +
            score_breakdown.missing_outcome +
            score_breakdown.target_match +
            score_breakdown.negation
        )

        scored_candidates.append({
            **candidate,
            "score": score_breakdown.total,
            "score_breakdown": score_breakdown.to_dict()
        })

    scored_candidates.sort(key=lambda x: x["score"], reverse=True)

    # Log scoring breakdown for Opik
    update_current_span(metadata={
        "candidates_scored": len(scored_candidates),
        "target_signals_used": target_signals,
        "scoring_results": [
            {
                "routine_id": c["id"],
                "title": c.get("routine_json", {}).get("title", "Unknown"),
                "score": c["score"],
                "breakdown": c["score_breakdown"]
            }
            for c in scored_candidates[:5]
        ]
    })

    return scored_candidates


@maybe_track(name="resolve_routine_for_feedback")
def resolve_routine_for_feedback(
    candidates: List[Dict[str, Any]], target_signals: dict, chat_id: str, routine_in_chat_check
) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Resolve which routine feedback refers to.

    Returns:
        Tuple of (routine_id, resolution_metadata)
        - routine_id: Resolved routine ID, or None if ambiguous/low confidence
        - resolution_metadata: Dict with decision details for tracing
    """
    resolution_metadata = {
        "decision": "ignore",
        "reason": "no_candidates",
        "top_score": None,
        "score_gap": None,
        "candidates_considered": len(candidates)
    }

    if not candidates:
        update_current_span(metadata={"resolution": resolution_metadata})
        return None, resolution_metadata

    # Check explicit refs first
    explicit_refs = target_signals.get("explicit_routine_refs", [])
    if explicit_refs:
        for candidate in candidates:
            routine_title = candidate.get("routine_json", {}).get("title", "").lower()
            for ref in explicit_refs:
                if ref.lower() in routine_title or routine_title in ref.lower():
                    resolution_metadata.update({
                        "decision": "resolved",
                        "reason": "explicit_reference_match",
                        "matched_ref": ref,
                        "matched_title": routine_title
                    })
                    update_current_span(metadata={"resolution": resolution_metadata})
                    return candidate["id"], resolution_metadata

    # Rank and resolve
    ranked = rank_routine_candidates(candidates, target_signals, chat_id, routine_in_chat_check)
    if not ranked:
        resolution_metadata["reason"] = "ranking_failed"
        update_current_span(metadata={"resolution": resolution_metadata})
        return None, resolution_metadata

    top_candidate = ranked[0]
    top_score = top_candidate["score"]
    resolution_metadata["top_score"] = top_score
    resolution_metadata["top_candidate_id"] = top_candidate["id"]
    resolution_metadata["top_candidate_title"] = top_candidate.get("routine_json", {}).get("title", "Unknown")

    if top_score < 50:
        resolution_metadata.update({
            "decision": "ignore",
            "reason": "score_below_threshold",
            "threshold": 50
        })
        log_scoring_breakdown(ranked, None, "ignore", None)
        update_current_span(metadata={"resolution": resolution_metadata})
        return None, resolution_metadata

    if len(ranked) > 1:
        second_score = ranked[1]["score"]
        score_gap = top_score - second_score
        resolution_metadata["score_gap"] = score_gap
        resolution_metadata["second_score"] = second_score
        resolution_metadata["second_candidate_id"] = ranked[1]["id"]

        if top_score > 70 and score_gap > 20:
            resolution_metadata.update({
                "decision": "resolved",
                "reason": "high_confidence_clear_winner"
            })
            log_scoring_breakdown(ranked, top_candidate["id"], "resolved", score_gap)
            update_current_span(metadata={"resolution": resolution_metadata})
            return top_candidate["id"], resolution_metadata
        elif top_score > 50 and score_gap <= 20:
            resolution_metadata.update({
                "decision": "clarification",
                "reason": "ambiguous_close_scores"
            })
            log_scoring_breakdown(ranked, None, "clarification", score_gap)
            update_current_span(metadata={"resolution": resolution_metadata})
            return None, resolution_metadata
    else:
        if top_score > 50:
            resolution_metadata.update({
                "decision": "resolved",
                "reason": "single_candidate_above_threshold"
            })
            log_scoring_breakdown(ranked, top_candidate["id"], "resolved", None)
            update_current_span(metadata={"resolution": resolution_metadata})
            return top_candidate["id"], resolution_metadata

    resolution_metadata.update({
        "decision": "ignore",
        "reason": "fallthrough_no_match"
    })
    log_scoring_breakdown(ranked, None, "ignore", None)
    update_current_span(metadata={"resolution": resolution_metadata})
    return None, resolution_metadata
