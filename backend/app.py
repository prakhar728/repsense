import logging
import os
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.chat import router as chat_router
from backend.routes.profile import router as profile_router
from backend.routes.routines import router as routines_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


BASE_DIR = Path(__file__).resolve().parents[1]

app = FastAPI(
    title="Repsense Backend",
    description="FastAPI backend for the agentic fitness system.",
    version="0.1.0",
)

# Get allowed origins from environment, fallback to localhost for dev
allowed_origins = os.getenv("FRONTEND_URL", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router, prefix="/profile", tags=["profile"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(routines_router, prefix="/routines", tags=["routines"])


@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check(response: Response):
    response.status_code = 200
    return Response(content="OK", status_code=200)