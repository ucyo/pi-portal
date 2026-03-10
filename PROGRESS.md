# Progress

## Completed: M0 - Project Setup

- [x] M0.1: completed - project structure initialized
- [x] M0.2: completed - Python environment set up
- [x] M0.3: completed - Process management setup (removed Honcho - unnecessary for single service)
- [x] M0.4: completed - static files + CORS configured
- [x] M0.5: completed - Pi RPC communication verified

## Completed: M1 - Basic Chat

- [x] M1.1: completed - Frontend HTML/CSS structure
- [x] M1.2: completed - WebSocket connection
- [x] M1.3: completed - Pi subprocess management
- [x] M1.4: completed - Backend message routing
- [x] M1.5: completed - Frontend message rendering

## Completed: M2/M3 - Session Persistence & Feedback

- [x] M2.1: completed - Session file parser (backend/session_parser.py)
- [x] M2.2: completed - Session list API (GET /api/sessions)
- [x] M3.1: completed - Feedback data model
- [x] Bug fix: WebSocket hanging on slash commands without content
- [x] M2.3: completed - Sidebar session list (fetch, render, highlight, auto-refresh)
- [x] M2.4: completed - View past session (API, load messages, read-only mode)
- [x] M2.5: completed - New session button (WebSocket command, UI reset)
- [x] M3.2: completed - Message feedback UI (thumbs up/down buttons, styling, toggle state)
- [x] M3.3: completed - Negative feedback modal (opens on thumbs down, comment textarea, submit/cancel)
- [x] M3.4: completed - Feedback submission (WebSocket handler, direct JSONL write)
- [x] Bug fix: Feedback for past sessions written to correct session file (not current)
- [x] M3.5: completed - Load existing feedback (parse from JSONL, match by timestamp, show on past sessions)

## Current: M4 - Polish & Refinement

- [x] M4.1: Error handling - completed
- [ ] M4.2: UI polish
- [x] M4.3: Configuration file - completed
- [ ] M4.4: Documentation
- [ ] M4.5: Testing & bug fixes

## Notes
- Architecture changed: No database, use Pi's JSONL sessions as single source of truth
- Feedback stored directly to JSONL by backend using CustomEntry (customType: "pi-portal-feedback")
- Messages identified by timestamp field for feedback matching
- Configuration via Pydantic BaseSettings with PI_PORTAL_ prefix (.env file support)
- Dependencies: fastapi, uvicorn, websockets, pydantic-settings, python-dotenv
- Dev deps: pytest, pytest-asyncio, httpx, ruff
- Pi client tested: starts subprocess, sends commands, parses responses
- WebSocket: backend/websocket.py + frontend/app.js with reconnection logic
- M1.3: Pi lifecycle integrated into WebSocket (lazy start, crash recovery, shutdown hook)
- M1.4: Handles Pi RPC events (message_update, text_delta, thinking_delta, tool events)
- M1.5: Streaming UI with thinking section, tool indicators, markdown rendering
