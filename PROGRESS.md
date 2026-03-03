# Progress

## Completed: M0 - Project Setup

- [x] M0.1: completed - project structure initialized
- [x] M0.2: completed - Python environment set up
- [x] M0.3: completed - Honcho setup with Procfile
- [x] M0.4: completed - static files + CORS configured
- [x] M0.5: completed - Pi RPC communication verified

## Current: M1 - Basic Chat

- [x] M1.1: completed - Frontend HTML/CSS structure
- [x] M1.2: completed - WebSocket connection
- [x] M1.3: completed - Pi subprocess management

## Notes
- Dependencies: fastapi, uvicorn, aiosqlite, mlflow, websockets
- Dev deps: pytest, pytest-asyncio, httpx, ruff, honcho
- Makefile added for common commands
- Pi client tested: starts subprocess, sends commands, parses responses
- WebSocket: backend/websocket.py + frontend/app.js with reconnection logic
- M1.3: Pi lifecycle integrated into WebSocket (lazy start, crash recovery, shutdown hook)
