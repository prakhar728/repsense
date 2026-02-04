import tempfile
import os

from fastapi import APIRouter, File, Form, UploadFile

from agentic.src.main_profile_gen import run_profile_generation
from backend.storage.profile_store import save_csv, save_profile


router = APIRouter()


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
