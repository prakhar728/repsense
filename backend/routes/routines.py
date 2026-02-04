from fastapi import APIRouter, HTTPException

from backend.storage.routine_store import get_routine


router = APIRouter()


@router.get("/{routine_id}")
async def fetch_routine(routine_id: str):
    """
    Fetch a stored routine by ID.
    """
    routine = get_routine(routine_id)
    if routine is None:
        raise HTTPException(status_code=404, detail="Routine not found.")
    return {"routine": routine}

