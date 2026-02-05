"""Feedback resolution - ranking and routine matching."""
from typing import List, Dict, Any, Optional
from datetime import datetime


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
    """
    now = datetime.utcnow()
    scored_candidates = []
    
    for candidate in candidates:
        score = 0.0
        
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
            recency_score = max(0, 100 * (1 - days_since / 60))
            score += recency_score
        except (ValueError, KeyError, TypeError, AttributeError):
            pass
        
        # 2. Same-Chat Proximity (+50)
        if routine_in_chat_check(chat_id, candidate["id"]):
            score += 50
        
        # 3. Missing Outcome Bonus (+30)
        if candidate.get("existing_outcomes", 0) == 0:
            score += 30
        
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
            
            target_match_score = 100 * (matched_signals / total_signals)
            score += target_match_score
        
        # 5. Negation Penalty (-1000)
        negations = [n.lower() for n in target_signals.get("negations", [])]
        for negation in negations:
            routine_title = routine_json.get("title", "").lower()
            if negation in routine_title or any(negation in m for m in routine_muscles):
                score -= 1000
                break
        
        scored_candidates.append({**candidate, "score": score})
    
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    return scored_candidates


def resolve_routine_for_feedback(
    candidates: List[Dict[str, Any]], target_signals: dict, chat_id: str, routine_in_chat_check
) -> Optional[str]:
    """
    Resolve which routine feedback refers to.
    
    Returns routine_id if resolved, None if ambiguous/low confidence.
    """
    # Check explicit refs first
    explicit_refs = target_signals.get("explicit_routine_refs", [])
    if explicit_refs:
        for candidate in candidates:
            routine_title = candidate.get("routine_json", {}).get("title", "").lower()
            for ref in explicit_refs:
                if ref.lower() in routine_title or routine_title in ref.lower():
                    return candidate["id"]
    
    # Rank and resolve
    ranked = rank_routine_candidates(candidates, target_signals, chat_id, routine_in_chat_check)
    if not ranked:
        return None
    
    top_candidate = ranked[0]
    top_score = top_candidate["score"]
    
    if top_score < 50:
        return None
    
    if len(ranked) > 1:
        second_score = ranked[1]["score"]
        score_gap = top_score - second_score
        
        if top_score > 70 and score_gap > 20:
            return top_candidate["id"]
        elif top_score > 50 and score_gap <= 20:
            return None  # Ambiguous
    else:
        if top_score > 50:
            return top_candidate["id"]
    
    return None
