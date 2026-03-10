"""Pi Portal - FastAPI backend."""

import json
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import config
from backend.websocket import websocket_endpoint, stop_pi_client
from backend.session_parser import get_session_metadata, parse_session_file

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

# Paths from configuration
SESSIONS_PATH = config.get_absolute_session_dir()

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
    prompts_file = config.config_path / "starter_prompts.json"

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


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get a specific session with full message history.

    Args:
        session_id: The session ID (without .jsonl extension)

    Returns:
        Session metadata and full message list
    """
    from fastapi import HTTPException

    # Find session file - files are named {timestamp}_{id}.jsonl
    session_file = None
    if SESSIONS_PATH.exists():
        for path in SESSIONS_PATH.glob(f"*_{session_id}.jsonl"):
            session_file = path
            break

    if not session_file or not session_file.exists():
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    try:
        parsed = parse_session_file(session_file)

        # Convert messages to JSON-serializable format
        messages = []
        for msg in parsed.messages:
            # Extract content blocks for assistant messages (thinking, text, toolCall)
            content_blocks = None
            if msg.role == "assistant" and isinstance(
                msg.raw_message.get("content"), list
            ):
                content_blocks = msg.raw_message.get("content")

            messages.append(
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "content_blocks": content_blocks,
                    "timestamp": msg.timestamp,
                    "message_timestamp": msg.message_timestamp,
                }
            )

        # Convert feedback to JSON-serializable format
        feedback = []
        for fb in parsed.feedback:
            feedback.append(
                {
                    "target_timestamp": fb.target_timestamp,
                    "rating": fb.rating,
                    "comment": fb.comment,
                    "timestamp": fb.timestamp,
                }
            )

        return {
            "id": parsed.header.id,
            "timestamp": parsed.header.timestamp,
            "cwd": parsed.header.cwd,
            "name": parsed.name,
            "display_name": parsed.display_name,
            "messages": messages,
            "feedback": feedback,
        }

    except FileNotFoundError:
        logger.error(f"Session file not found: {session_id}")
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Session file not found")

    except ValueError as e:
        logger.error(f"Invalid session file {session_id}: {e}")
        from fastapi import HTTPException

        raise HTTPException(status_code=422, detail=f"Invalid session file: {str(e)}")

    except Exception:
        logger.exception(f"Error parsing session {session_id}")
        from fastapi import HTTPException

        raise HTTPException(
            status_code=500, detail="Failed to load session. The file may be corrupted."
        )


# WebSocket endpoint for chat
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat communication."""
    await websocket_endpoint(websocket)


# Static files - must be mounted after API routes
app.mount("/", StaticFiles(directory=config.frontend_path, html=True), name="frontend")
