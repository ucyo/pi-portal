"""Pi Portal - FastAPI backend."""

import json
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.websocket import websocket_endpoint, stop_pi_client
from backend.session_parser import get_session_metadata

# Configure logging for Docker (stdout)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
    force=True,  # Override any existing configuration
)

# Set DEBUG level for Pi communication
logging.getLogger("backend.pi_client").setLevel(logging.DEBUG)
logging.getLogger("backend.websocket").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup
    logger.info("Pi Portal starting up...")
    yield
    # Shutdown
    logger.info("Pi Portal shutting down...")
    await stop_pi_client()
    logger.info("Pi process stopped")


app = FastAPI(title="Pi Portal", lifespan=lifespan)

# Paths
ROOT_PATH = Path(__file__).parent.parent
CONFIG_PATH = ROOT_PATH / "config"
FRONTEND_PATH = ROOT_PATH / "frontend"
SESSIONS_PATH = ROOT_PATH / "data" / "pi_sessions"

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/config/starter-prompts")
async def get_starter_prompts():
    """Get starter prompts for the welcome screen."""
    prompts_file = CONFIG_PATH / "starter_prompts.json"

    if prompts_file.exists():
        with open(prompts_file) as f:
            return json.load(f)

    # Default prompts if config file doesn't exist
    return {"prompts": [{"icon": "💡", "text": "What can you help me with?"}]}


@app.get("/api/sessions")
async def list_sessions():
    """
    List all sessions with metadata.

    Returns sessions ordered by most recent first.
    """
    sessions = []

    if not SESSIONS_PATH.exists():
        return {"sessions": []}

    # Scan for JSONL session files
    session_files = list(SESSIONS_PATH.glob("*.jsonl"))

    for path in session_files:
        try:
            metadata = get_session_metadata(path)
            sessions.append(metadata)
        except Exception as e:
            logger.warning(f"Failed to parse session {path.name}: {e}")
            continue

    # Sort by timestamp (most recent first)
    sessions.sort(key=lambda s: s.get("timestamp", ""), reverse=True)

    return {"sessions": sessions}


# WebSocket endpoint for chat
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat communication."""
    await websocket_endpoint(websocket)


# Static files - must be mounted after API routes
app.mount("/", StaticFiles(directory=FRONTEND_PATH, html=True), name="frontend")
