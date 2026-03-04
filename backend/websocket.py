"""WebSocket handler for Pi Portal."""

import asyncio
import logging
from pathlib import Path
from typing import Set

from fastapi import WebSocket, WebSocketDisconnect

from backend.pi_client import PiClient

# Session directory path
SESSIONS_PATH = Path("data/pi_sessions")

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(
            f"Client connected. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(
            f"Client disconnected. Total connections: {len(self.active_connections)}"
        )

    async def send_message(self, websocket: WebSocket, message: dict) -> None:
        """Send a JSON message to a specific client."""
        msg_type = message.get("type", "unknown")
        if msg_type == "text_delta":
            # Don't log every text delta, just note it
            logger.debug(f"[WS TX] text_delta ({len(message.get('delta', ''))} chars)")
        else:
            logger.info(f"[WS TX] {message}")
        await websocket.send_json(message)

    async def broadcast(self, message: dict) -> None:
        """Send a message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)


# Global connection manager instance
manager = ConnectionManager()


def get_most_recent_session_id() -> str | None:
    """Get the session ID of the most recently modified session file."""
    if not SESSIONS_PATH.exists():
        return None

    session_files = list(SESSIONS_PATH.glob("*.jsonl"))
    if not session_files:
        return None

    # Sort by modification time, most recent first
    session_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    # Extract session ID from filename (format: {timestamp}_{session_id}.jsonl)
    most_recent = session_files[0]
    filename = most_recent.stem  # Remove .jsonl
    parts = filename.split("_", 1)
    if len(parts) == 2:
        return parts[1]

    return None


# Shared Pi client instance
_pi_client: PiClient | None = None
_pi_lock = asyncio.Lock()


async def get_pi_client() -> PiClient:
    """Get or create the shared Pi client instance and ensure it's running."""
    global _pi_client

    async with _pi_lock:
        if _pi_client is None:
            _pi_client = PiClient()

        # Start if not running (handles initial start and crash recovery)
        if not _pi_client.is_running:
            logger.info("Starting Pi process...")
            await _pi_client.start()

    return _pi_client


async def ensure_pi_running() -> PiClient | None:
    """Ensure Pi is running, with crash recovery.

    Returns:
        PiClient if successful, None if unable to start.
    """
    max_retries = 3
    retry_delay = 1.0

    for attempt in range(max_retries):
        try:
            client = await get_pi_client()
            if client.is_running:
                return client
        except Exception as e:
            logger.error(
                f"Failed to start Pi (attempt {attempt + 1}/{max_retries}): {e}"
            )

        if attempt < max_retries - 1:
            await asyncio.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff

    logger.error("Failed to start Pi after all retries")
    return None


async def stop_pi_client() -> None:
    """Stop the shared Pi client instance."""
    global _pi_client

    async with _pi_lock:
        if _pi_client is not None and _pi_client.is_running:
            await _pi_client.stop()


async def process_pi_message(
    websocket: WebSocket,
    content: str,
) -> None:
    """Send a message to Pi and stream the response back.

    Args:
        websocket: The WebSocket to send responses to.
        content: The user message content.
    """
    logger.info(
        f"[WS] Processing user message: {content[:100]}{'...' if len(content) > 100 else ''}"
    )

    # Ensure Pi is running (with crash recovery)
    client = await ensure_pi_running()
    if client is None:
        await manager.send_message(
            websocket,
            {
                "type": "error",
                "message": "Failed to start Pi process. Please try again.",
            },
        )
        await manager.send_message(websocket, {"type": "status", "status": "ready"})
        return

    try:
        # Send prompt to Pi
        await client.send_command({"type": "prompt", "message": content})

        # Track accumulated response and command state
        full_response = ""
        got_content = False
        is_command = content.startswith("/")

        # Stream events from Pi
        async for event in client.read_events():
            event_type = event.get("type")
            logger.debug(f"[WS] Processing Pi event: {event_type}")

            # Handle different event types
            if event_type == "response":
                # Command acknowledgement
                if event.get("command") == "prompt":
                    if not event.get("success"):
                        error_msg = event.get("error", "Unknown error")
                        await manager.send_message(
                            websocket,
                            {"type": "error", "message": f"Pi error: {error_msg}"},
                        )
                        break

                    # For slash commands that don't generate content (like /feedback with errors),
                    # Pi sends response but no agent_end. If we got response for a command
                    # without any content, finish immediately.
                    if is_command and not got_content:
                        logger.info(
                            "Slash command completed without content, finishing"
                        )
                        await manager.send_message(
                            websocket,
                            {
                                "type": "message_complete",
                                "role": "assistant",
                                "content": "",
                            },
                        )
                        break

            elif event_type == "message_update":
                # Mark that we got content (agent is responding)
                got_content = True

                # Handle nested assistant message events
                assistant_event = event.get("assistantMessageEvent", {})
                assistant_event_type = assistant_event.get("type")

                if assistant_event_type == "text_delta":
                    # Streaming text chunk
                    delta = assistant_event.get("delta", "")
                    if delta:
                        full_response += delta
                        await manager.send_message(
                            websocket,
                            {
                                "type": "text_delta",
                                "delta": delta,
                            },
                        )

                elif assistant_event_type == "thinking_delta":
                    # Streaming thinking chunk (send to frontend for transparency)
                    delta = assistant_event.get("delta", "")
                    if delta:
                        await manager.send_message(
                            websocket,
                            {
                                "type": "thinking_delta",
                                "delta": delta,
                            },
                        )

                elif assistant_event_type == "tool_use_start":
                    # Tool execution started
                    tool_name = assistant_event.get("name", "unknown")
                    await manager.send_message(
                        websocket,
                        {
                            "type": "tool_start",
                            "tool": tool_name,
                            "tool_use_id": assistant_event.get("toolUseId"),
                        },
                    )

                elif assistant_event_type == "tool_use_end":
                    # Tool use block completed (input fully received)
                    pass  # We'll show result when tool_result comes

            elif event_type == "tool_result":
                # Tool execution completed with result
                await manager.send_message(
                    websocket,
                    {
                        "type": "tool_result",
                        "tool_use_id": event.get("toolUseId"),
                        "success": not event.get("isError", False),
                    },
                )

            elif event_type == "agent_end":
                # Agent finished responding
                messages = event.get("messages", [])

                # Get the current session ID from most recent session file
                session_id = get_most_recent_session_id()

                # Send complete message for storage/display
                await manager.send_message(
                    websocket,
                    {
                        "type": "message_complete",
                        "role": "assistant",
                        "content": full_response,
                        "messages": messages,
                        "session_id": session_id,
                    },
                )
                break

            elif event_type == "error":
                # Pi reported an error
                error_msg = event.get("message", "Unknown Pi error")
                await manager.send_message(
                    websocket,
                    {"type": "error", "message": error_msg},
                )
                break

    except Exception as e:
        logger.exception("Error processing Pi message")

        # Check if Pi crashed
        if not client.is_running:
            logger.warning("Pi process crashed during message processing")
            await manager.send_message(
                websocket,
                {
                    "type": "error",
                    "message": "Pi process crashed. Attempting to restart...",
                },
            )

            # Try to restart for next message
            restarted_client = await ensure_pi_running()
            if restarted_client:
                await manager.send_message(
                    websocket,
                    {
                        "type": "status",
                        "status": "pi_restarted",
                        "message": "Pi has been restarted. Please try again.",
                    },
                )
            else:
                await manager.send_message(
                    websocket,
                    {
                        "type": "error",
                        "message": "Failed to restart Pi. Please refresh the page.",
                    },
                )
        else:
            await manager.send_message(
                websocket,
                {"type": "error", "message": str(e)},
            )


async def process_new_session(websocket: WebSocket) -> None:
    """Create a new Pi session.

    Args:
        websocket: The WebSocket to send responses to.
    """
    logger.info("[WS] Creating new session")

    # Ensure Pi is running
    client = await ensure_pi_running()
    if client is None:
        await manager.send_message(
            websocket,
            {
                "type": "error",
                "message": "Failed to start Pi process. Please try again.",
            },
        )
        return

    try:
        # Send new_session command to Pi
        await client.send_command({"type": "new_session"})

        # Read the response
        async for event in client.read_events():
            event_type = event.get("type")
            logger.debug(f"[WS] New session event: {event_type}")

            if event_type == "response":
                if event.get("command") == "new_session":
                    if event.get("success"):
                        # Pi doesn't return session_id directly, so we get it from
                        # the most recent session file (created by Pi)
                        # Small delay to ensure file is written
                        await asyncio.sleep(0.1)
                        session_id = get_most_recent_session_id()
                        logger.info(f"[WS] New session created: {session_id}")
                        await manager.send_message(
                            websocket,
                            {
                                "type": "new_session_created",
                                "session_id": session_id,
                            },
                        )
                    else:
                        error_msg = event.get("error", "Failed to create session")
                        await manager.send_message(
                            websocket,
                            {"type": "error", "message": error_msg},
                        )
                    break

    except Exception as e:
        logger.exception("Error creating new session")
        await manager.send_message(
            websocket,
            {"type": "error", "message": f"Failed to create session: {e}"},
        )


async def process_feedback(websocket: WebSocket, data: dict) -> None:
    """Submit feedback directly to the session file.

    Always writes directly to the session JSONL file to ensure feedback
    goes to the correct session (avoids issues with Pi's current session).

    Args:
        websocket: The WebSocket to send responses to.
        data: Feedback data containing targetTimestamp, rating, sessionId, and optional comment.
    """
    target_timestamp = data.get("targetTimestamp")
    rating = data.get("rating")
    comment = data.get("comment")
    session_id = data.get("sessionId")

    if target_timestamp is None or rating is None:
        await manager.send_message(
            websocket,
            {
                "type": "error",
                "message": "Feedback requires targetTimestamp and rating",
            },
        )
        return

    if not session_id:
        await manager.send_message(
            websocket,
            {
                "type": "error",
                "message": "Feedback requires sessionId",
            },
        )
        return

    logger.info(
        f"[WS] Processing feedback: session={session_id}, timestamp={target_timestamp}, rating={rating}"
    )

    # Always write directly to the session file
    await _write_feedback_to_session_file(
        websocket, session_id, target_timestamp, rating, comment
    )


async def _write_feedback_to_session_file(
    websocket: WebSocket,
    session_id: str,
    target_timestamp: int,
    rating: int,
    comment: str | None,
) -> None:
    """Write feedback directly to a session JSONL file.

    Args:
        websocket: The WebSocket to send responses to.
        session_id: The session ID to write to.
        target_timestamp: The message timestamp being rated.
        rating: The rating (-1, 0, or 1).
        comment: Optional comment for negative feedback.
    """
    import json
    import time
    import uuid

    # Find the session file
    session_file = None
    if SESSIONS_PATH.exists():
        for path in SESSIONS_PATH.glob(f"*_{session_id}.jsonl"):
            session_file = path
            break

    if not session_file or not session_file.exists():
        await manager.send_message(
            websocket,
            {"type": "error", "message": f"Session not found: {session_id}"},
        )
        return

    try:
        # Read the file to get the last entry's ID for parentId
        last_entry_id = None
        with open(session_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        if entry.get("id"):
                            last_entry_id = entry["id"]
                    except json.JSONDecodeError:
                        continue

        # Build the custom feedback entry (same format as Pi extension)
        entry = {
            "type": "custom",
            "customType": "pi-portal-feedback",
            "id": str(uuid.uuid4()),
            "parentId": last_entry_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "data": {
                "targetTimestamp": target_timestamp,
                "rating": rating,
                "comment": comment if rating == -1 else None,
                "timestamp": int(time.time() * 1000),
            },
        }

        # Append to the session file
        with open(session_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        logger.info(f"[WS] Feedback written to session file: {session_file.name}")

        await manager.send_message(
            websocket,
            {
                "type": "feedback_saved",
                "targetTimestamp": target_timestamp,
                "rating": rating,
            },
        )

    except Exception as e:
        logger.exception(f"Error writing feedback to session file: {e}")
        await manager.send_message(
            websocket,
            {"type": "error", "message": f"Failed to save feedback: {e}"},
        )


async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    Handle WebSocket connections for chat.

    Message protocol:
    - Client sends: {"type": "message", "content": "user message"}
    - Client sends: {"type": "new_session"}
    - Client sends: {"type": "feedback", "targetTimestamp": 123, "rating": 1, "comment": null}
    - Server sends: {"type": "text_delta", "delta": "..."}  (streaming)
    - Server sends: {"type": "message_complete", "role": "assistant", "content": "..."}
    - Server sends: {"type": "tool_start", "tool": "tool_name"}
    - Server sends: {"type": "tool_result", "tool": "tool_name", "success": true}
    - Server sends: {"type": "new_session_created", "session_id": "..."}
    - Server sends: {"type": "feedback_saved", "targetTimestamp": 123, "rating": 1}
    - Server sends: {"type": "status", "status": "connected" | "processing" | "ready"}
    - Server sends: {"type": "error", "message": "error description"}
    """
    await manager.connect(websocket)

    # Send connected status
    await manager.send_message(websocket, {"type": "status", "status": "connected"})

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            logger.info(f"[WS RX] {data}")

            if data.get("type") == "ping":
                # Handle ping for keepalive
                await manager.send_message(websocket, {"type": "pong"})
                continue

            if data.get("type") == "new_session":
                # Handle new session request
                await manager.send_message(
                    websocket, {"type": "status", "status": "processing"}
                )
                await process_new_session(websocket)
                await manager.send_message(
                    websocket, {"type": "status", "status": "ready"}
                )
                continue

            if data.get("type") == "feedback":
                # Handle feedback submission
                await process_feedback(websocket, data)
                continue

            if data.get("type") == "message":
                content = data.get("content") or ""
                if isinstance(content, str):
                    content = content.strip()
                else:
                    content = ""
                if not content:
                    continue

                # Notify client we're processing
                await manager.send_message(
                    websocket, {"type": "status", "status": "processing"}
                )

                # Process message with Pi
                await process_pi_message(websocket, content)

                # Signal done processing
                await manager.send_message(
                    websocket, {"type": "status", "status": "ready"}
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.exception("WebSocket error")
        try:
            await manager.send_message(websocket, {"type": "error", "message": str(e)})
        except Exception:
            pass
        manager.disconnect(websocket)
