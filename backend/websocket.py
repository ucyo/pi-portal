"""WebSocket handler for Pi Portal."""

import asyncio
import logging
from typing import Set

from fastapi import WebSocket, WebSocketDisconnect

from backend.pi_client import PiClient

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
        got_response = False
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
                    got_response = True
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
                        logger.info("Slash command completed without content, finishing")
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
                # Send complete message for storage/display
                await manager.send_message(
                    websocket,
                    {
                        "type": "message_complete",
                        "role": "assistant",
                        "content": full_response,
                        "messages": messages,
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


async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    Handle WebSocket connections for chat.

    Message protocol:
    - Client sends: {"type": "message", "content": "user message"}
    - Server sends: {"type": "text_delta", "delta": "..."}  (streaming)
    - Server sends: {"type": "message_complete", "role": "assistant", "content": "..."}
    - Server sends: {"type": "tool_start", "tool": "tool_name"}
    - Server sends: {"type": "tool_result", "tool": "tool_name", "success": true}
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
