"""WebSocket handler for Pi Portal."""

import logging
from typing import Set

from fastapi import WebSocket, WebSocketDisconnect

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


async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    Handle WebSocket connections for chat.

    Message protocol:
    - Client sends: {"type": "message", "content": "user message"}
    - Server sends: {"type": "message", "role": "assistant", "content": "..."}
    - Server sends: {"type": "status", "status": "connected" | "processing" | "error"}
    - Server sends: {"type": "error", "message": "error description"}
    """
    await manager.connect(websocket)

    # Send connected status
    await manager.send_message(websocket, {"type": "status", "status": "connected"})

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

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

                # TODO: M1.3 - Forward to Pi subprocess
                # For now, echo back a placeholder response
                await manager.send_message(
                    websocket,
                    {
                        "type": "message",
                        "role": "assistant",
                        "content": f"[Pi integration pending] You said: {content}",
                    },
                )

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
