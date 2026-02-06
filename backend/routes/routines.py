from fastapi import APIRouter, HTTPException

from backend.storage.routine_store import get_routine


router = APIRouter()


@router.get("/{user_id}/{routine_id}")
async def fetch_routine(user_id: str, routine_id: str):
    """
    Fetch a stored routine by ID, verifying it belongs to the user.
    """
    routine = get_routine(routine_id, user_id)
    if routine is None:
        raise HTTPException(status_code=404, detail="Routine not found or access denied.")
    return {"routine": routine}

