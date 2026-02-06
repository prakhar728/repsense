from fastapi import APIRouter, HTTPException, Depends

from backend.auth import require_user
from backend.storage.routine_store import get_routine, list_routines


router = APIRouter()


@router.get("")
async def list_user_routines(user_id: str = Depends(require_user)):
    """
    Return stored routines for a user (most recent first).
    """
    routines = list_routines(user_id)
    summaries = []
    for item in routines:
        routine = item.get("routine", {})
        sessions = routine.get("sessions", []) if isinstance(routine, dict) else []
        days_per_week = None
        if isinstance(routine, dict):
            duration = routine.get("duration", {})
            if isinstance(duration, dict):
                days_per_week = duration.get("days_per_week")
        if days_per_week is None and isinstance(sessions, list):
            days_per_week = len(sessions)

        focus_muscles = []
        if isinstance(sessions, list):
            for session in sessions:
                if not isinstance(session, dict):
                    continue
                for exercise in session.get("exercises", []) or []:
                    if not isinstance(exercise, dict):
                        continue
                    muscle = exercise.get("primary_muscle")
                    if muscle:
                        focus_muscles.append(muscle)

        muscle_counts = {}
        for muscle in focus_muscles:
            muscle_counts[muscle] = muscle_counts.get(muscle, 0) + 1
        top_muscles = [
            m for m, _ in sorted(muscle_counts.items(), key=lambda kv: kv[1], reverse=True)
        ][:3]

        summaries.append({
            "id": item.get("id"),
            "created_at": item.get("created_at"),
            "title": routine.get("title", "Generated Routine"),
            "goal": routine.get("goal", ""),
            "days_per_week": days_per_week,
            "focus_muscles": top_muscles,
        })
    return {"routines": summaries}


@router.get("/{routine_id}")
async def fetch_routine(routine_id: str, user_id: str = Depends(require_user)):
    """
    Fetch a stored routine by ID, verifying it belongs to the user.
    """
    routine = get_routine(routine_id, user_id)
    if routine is None:
        raise HTTPException(status_code=404, detail="Routine not found or access denied.")
    return {"routine": routine}


@router.get("/legacy/{user_id}/{routine_id}")
async def fetch_routine_legacy(
    user_id: str,
    routine_id: str,
    authed_user_id: str = Depends(require_user),
):
    """
    Legacy endpoint: still enforces auth and user ownership.
    """
    if user_id != authed_user_id:
        raise HTTPException(status_code=403, detail="Access denied.")
    routine = get_routine(routine_id, authed_user_id)
    if routine is None:
        raise HTTPException(status_code=404, detail="Routine not found or access denied.")
    return {"routine": routine}
