from pathlib import Path

from fastapi import FastAPI

from backend.routes.chat import router as chat_router
from backend.routes.profile import router as profile_router
from backend.routes.routines import router as routines_router


BASE_DIR = Path(__file__).resolve().parents[1]

app = FastAPI(
    title="Repsense Backend",
    description="FastAPI backend for the agentic fitness system.",
    version="0.1.0",
)


app.include_router(profile_router, prefix="/profile", tags=["profile"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(routines_router, prefix="/routines", tags=["routines"])

