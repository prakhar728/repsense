import os
import tempfile

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from agentic.src.main_profile_gen import run_profile_generation
from agentic.src.data_access import extract_query_params
from agentic.src.rag_pipeline import get_relevant_facts, generate_routine
from backend.storage.profile_store import save_csv, save_profile, get_profile
from backend.storage.routine_store import save_routine


router = APIRouter()


class GenerateRoutinesRequest(BaseModel):
    user_id: str
    goal: str


def _get_openai_client():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    from openai import OpenAI
    return OpenAI(api_key=api_key)


@router.post("/upload")
async def upload_profile(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Handle workout CSV upload and trigger profile generation.
    """
    contents = await file.read()
    csv_text = contents.decode("utf-8")

    # Store raw CSV in the database
    save_csv(user_id, file.filename, csv_text)

    # Write to a temp file for the agentic pipeline (reads via pandas)
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    try:
        tmp.write(csv_text)
        tmp.close()

        # Run profile generation — returns the profile dict
        profile = run_profile_generation(tmp.name)

        # Store the generated profile in the database
        save_profile(user_id, profile)
    finally:
        os.unlink(tmp.name)

    return {"status": "profile_generated"}


@router.get("/{user_id}")
async def get_user_profile(user_id: str):
    """
    Check if a user profile exists.
    """
    profile = get_profile(user_id)
    if profile is None:
        return {"exists": False, "message": "Profile not found. Upload CSV via POST /profile/upload"}
    return {"exists": True, "user_id": user_id}


@router.post("/generate-routines")
async def generate_routines(payload: GenerateRoutinesRequest):
    """
    Generate a routine based on user goal text and their training profile.
    """
    profile = get_profile(payload.user_id)
    if profile is None:
        return {"error": "Profile not found. Please upload your CSV first."}

    client = _get_openai_client()

    # Extract query params and facts from the user's profile
    params = extract_query_params(payload.goal, client)
    facts = get_relevant_facts(params, profile)

    # Generate the routine
    routine_json = generate_routine(payload.goal, facts, client)

    # Persist it
    routine_id = save_routine(routine_json)

    return {"routine_id": routine_id, "routine": routine_json}
