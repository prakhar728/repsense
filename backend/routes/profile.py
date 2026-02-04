import os
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from agentic.src.main_profile_gen import run_profile_generation


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "agentic" / "data"
UPLOADS_DIR = DATA_DIR / "uploads"


@router.post("/upload")
async def upload_profile(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Handle workout CSV upload and trigger profile generation.
    """
    # Ensure uploads directory exists
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    # Save uploaded CSV
    csv_path = UPLOADS_DIR / f"{user_id}_{file.filename}"
    contents = await file.read()
    with open(csv_path, "wb") as f:
        f.write(contents)

    # Run profile generation using the agentic pipeline
    # Use absolute paths to avoid CWD issues.
    output_path = DATA_DIR / "user_profile.json"
    run_profile_generation(str(csv_path), output_path=str(output_path))

    return {"status": "profile_generated"}

