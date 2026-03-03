"""Pi Portal - FastAPI backend."""

import json
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.websocket import websocket_endpoint

app = FastAPI(title="Pi Portal")

# Paths
ROOT_PATH = Path(__file__).parent.parent
CONFIG_PATH = ROOT_PATH / "config"
FRONTEND_PATH = ROOT_PATH / "frontend"

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


# WebSocket endpoint for chat
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat communication."""
    await websocket_endpoint(websocket)


# Static files - must be mounted after API routes
app.mount("/", StaticFiles(directory=FRONTEND_PATH, html=True), name="frontend")
