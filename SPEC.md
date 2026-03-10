# Pi Portal - Specification

## Overview

A web-based chat interface for the Pi coding agent, designed for R&D researchers who are not technical in agent development. Provides a simple, accessible way to interact with Pi while capturing session data and feedback for analysis and improvement.

| Aspect             | Description                                       |
| ------------------ | ------------------------------------------------- |
| **Project Name**   | pi-portal                                         |
| **Users**          | R&D researchers (<10), one instance per laptop    |
| **User Goal**      | Simple chat interface to Pi without CLI knowledge |
| **Developer Goal** | Collect sessions + feedback to improve Pi         |

## Execution Plan

| Phase | Milestone                 | Description                                                   |
| ----- | ------------------------- | ------------------------------------------------------------- |
| M0    | Project Setup             | Infrastructure, folder structure, dependencies, Honcho config |
| M1    | Basic Chat                | Frontend UI + backend WebSocket + Pi integration              |
| M2    | Session Persistence       | Parse Pi's JSONL sessions, session list, view past sessions   |
| M3    | Feedback System           | Per-message feedback (stored in JSONL)                        |
| M4    | Polish & Refinement       | UI improvements, error handling, documentation                |
| M5    | Docker Compose Deployment | Split services into containers                                |

## Milestones

> **⛔ STOP RULE:** Complete ONE sub-milestone, then STOP and wait for user review. Do not continue to the next sub-milestone without approval.

### M0 - Project Setup

#### M0.1 - Initialize project structure
- [x] Create project root folder
- [x] Create `backend/` folder for FastAPI code
- [x] Create `frontend/` folder for HTML/CSS/JS
- [x] Create `README.md` with project overview
- [x] Create `.gitignore` (Python, SQLite, environment files)
- [x] Initialize git repository
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M0.2 - Set up Python environment
- [x] Initialize project with `uv init`
- [x] Add FastAPI dependency with `uv add`
- [x] Add uvicorn dependency
- [x] Add websockets dependency
- [x] Document Python version requirement in `pyproject.toml`
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M0.3 - Set up process management
- [x] ~~Install Honcho~~ (removed - unnecessary for single service)
- [x] ~~Create Procfile~~ (removed - backend manages Pi directly)
- [x] Backend starts Pi subprocess on-demand
- [x] Document usage in README
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M0.4 - Basic FastAPI app
- [x] Create `backend/main.py` with FastAPI app
- [x] Add health check endpoint (`GET /health`)
- [x] Configure static file serving for `frontend/` folder
- [x] Add CORS configuration (for local development)
- [x] Test server starts and serves static files
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M0.5 - Verify Pi RPC communication
- [x] Create `backend/pi_client.py` module for Pi communication
- [x] Implement subprocess spawn for `pi --mode rpc` (with session saving enabled)
- [x] Configure Pi session directory (e.g., `data/pi_sessions/`)
- [x] Send test prompt via JSON-RPC
- [x] Receive and parse response
- [x] Handle subprocess lifecycle (start/stop)
- [x] Add basic error handling for Pi crashes
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

### M1 - Basic Chat

#### M1.1 - Frontend HTML/CSS structure
- [x] Create `frontend/index.html` with base layout
- [x] Create `frontend/styles.css` with chat styling
- [x] Implement sidebar layout (left panel)
- [x] Implement main chat area (right panel)
- [x] Add message input field and send button
- [x] Add placeholder for session list in sidebar
- [x] Add starter prompt suggestions (clickable example questions)
- [x] Hide starter prompts once chat begins
- [x] Ensure responsive design basics
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M1.2 - WebSocket connection
- [x] Create `frontend/app.js` for client-side logic
- [x] Implement WebSocket connection to backend
- [x] Handle connection open/close/error events
- [x] Display connection status to user
- [x] Implement reconnection logic on disconnect
- [x] Create `backend/websocket.py` for WebSocket endpoint
- [x] Register WebSocket route in FastAPI
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M1.3 - Pi subprocess management
- [x] Implement Pi process spawning on first WebSocket connection
- [x] Manage Pi lifecycle per session (or shared instance)
- [x] Handle stdin/stdout communication with Pi process
- [x] Parse JSON-RPC responses from Pi
- [x] Implement graceful shutdown of Pi process
- [x] Handle Pi process crash and restart
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M1.4 - Backend message routing
- [x] Receive user message from WebSocket
- [x] Format message as JSON-RPC request for Pi
- [x] Send request to Pi subprocess
- [x] Stream Pi response chunks back to WebSocket
- [x] Handle tool execution events from Pi
- [x] Send completion signal when Pi finishes responding
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M1.5 - Frontend message rendering
- [x] Display user messages in chat (right-aligned or distinct style)
- [x] Display Pi responses in chat (left-aligned or distinct style)
- [x] Render streaming responses (append chunks as they arrive)
- [x] Auto-scroll to latest message
- [x] Support markdown rendering in Pi responses
- [x] Show typing/loading indicator while Pi is responding
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

### M2 - Session Persistence

> **Architecture Note:** Sessions are stored in Pi's native JSONL format. No SQLite needed.
> Pi manages session files in `data/pi_sessions/`. We parse these files to list and view sessions.

#### M2.1 - Session file parser
- [x] Create `backend/session_parser.py` module
- [x] Parse Pi's JSONL session format (see Pi's session.md docs)
- [x] Extract session header (id, timestamp, cwd)
- [x] Extract messages (user, assistant, toolResult roles)
- [x] Extract session name from `session_info` entry if present
- [x] Handle tree structure (follow parentId chain from leaf)
- [x] Generate session title from first user message if no name set
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M2.2 - Session list API
- [x] Create `GET /api/sessions` endpoint
- [x] Scan `data/pi_sessions/` directory for JSONL files
- [x] Parse each session file for metadata (id, title, timestamps)
- [x] Return list of sessions ordered by most recent first
- [x] Include message count per session
- [ ] Cache parsed metadata for performance (optional)
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M2.3 - Sidebar session list
- [x] Fetch session list from API on page load
- [x] Render sessions in sidebar
- [x] Display session title and date
- [x] Highlight currently active session
- [x] Auto-refresh list when new session created
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M2.4 - View past session
- [x] Create `GET /api/sessions/{id}` endpoint
- [x] Find session file by ID in `data/pi_sessions/`
- [x] Parse and return full message history
- [x] Handle click on session in sidebar
- [x] Load and display messages in chat area (read-only)
- [x] Disable input field for past sessions
- [x] Show visual indicator that session is read-only
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M2.5 - New session button
- [x] Add "New Session" button in sidebar
- [x] Send `new_session` RPC command to Pi
- [x] Clear chat area in frontend
- [x] Show starter prompts again
- [x] Update sidebar session list
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

### M3 - Feedback System

> **Architecture Note:** Feedback is stored in Pi's session JSONL as CustomEntry.
> Messages are identified by their `timestamp` field (unique within a session).
> The backend writes feedback directly to the session file to ensure it goes to the correct session.

#### M3.1 - Feedback data model
- [x] Define feedback CustomEntry format with `customType: "pi-portal-feedback"`
- [x] Data format: `{targetTimestamp, rating, comment, timestamp}`
- [x] Backend writes feedback directly to session JSONL files
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M3.2 - Message feedback UI
- [x] Track message timestamps when rendering assistant messages
- [x] Add thumbs up/down buttons to each Pi response
- [x] Style feedback buttons (subtle, non-intrusive)
- [x] Highlight selected feedback state
- [x] Allow changing feedback (click other thumb)
- [x] Only show feedback buttons on assistant messages
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M3.3 - Negative feedback modal
- [x] Create modal/popup component in HTML/CSS
- [x] Trigger modal when thumbs down is clicked
- [x] Include text area for comment
- [x] Add "Submit" and "Cancel" buttons
- [x] Close modal on submit or cancel
- [x] Allow submitting without comment (optional text)
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M3.4 - Feedback submission
- [x] Send feedback via WebSocket to backend
- [x] Backend writes feedback directly to session JSONL file
- [x] Include sessionId to target correct session (for past sessions)
- [x] Send confirmation back to frontend
- [x] Update UI to reflect saved state
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M3.5 - Load existing feedback
- [x] Parse CustomEntry with `customType: "pi-portal-feedback"` from session
- [x] Match feedback to messages by `targetTimestamp`
- [x] Display correct thumbs state on each message
- [x] Handle multiple feedback entries for same message (use latest)
- [x] Show feedback on past sessions (read-only view)
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

### M4 - Polish & Refinement

#### M4.1 - Error handling
- [x] Handle WebSocket disconnection gracefully
- [x] Handle Pi subprocess crash and auto-restart (already implemented)
- [x] Handle session file parsing errors
- [x] Display user-friendly error messages in UI
- [x] Log errors server-side for debugging
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M4.2 - UI polish
- [ ] Add loading spinner while Pi is responding
- [ ] Add smooth animations for message appearance
- [ ] Improve typography and spacing
- [ ] Style scrollbars
- [ ] Add hover states for interactive elements
- [ ] Ensure consistent color scheme
- [ ] Test on different screen sizes
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M4.3 - Configuration file
- [x] Create configuration system using Pydantic BaseSettings
- [x] Use PI_PORTAL_ prefix for all environment variables
- [x] Support .env file loading with python-dotenv
- [x] Configurable Pi executable path
- [x] Configurable Pi session directory
- [x] Configurable server host/port/reload
- [x] Type validation and sensible defaults
- [x] Document all configuration options
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M4.4 - Documentation
- [x] Write README with project overview
- [x] Document installation steps
- [x] Document development setup (backend manages Pi directly)
- [x] Document configuration options
- [x] Document usage guide for end users
- [x] Add architecture diagram
- [x] Document API endpoints
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M4.5 - Testing & bug fixes
- [ ] Manual testing of full chat flow
- [ ] Test session persistence and retrieval
- [ ] Test feedback submission and display
- [ ] Test error scenarios (Pi crash, disconnect)
- [ ] Fix identified bugs
- [ ] Final review and cleanup
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

### M5 - Docker Compose Deployment

#### M5.1 - Create Dockerfile for FastAPI backend
- [ ] Create `backend/Dockerfile`
- [ ] Use Python base image
- [ ] Install uv in container
- [ ] Copy and install dependencies
- [ ] Copy application code
- [ ] Configure uvicorn as entrypoint
- [ ] Expose port 8000
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M5.2 - Create Dockerfile for Pi service
- [ ] Create `pi/Dockerfile`
- [ ] Use Node.js base image (Pi is Node-based)
- [ ] Install Pi globally (`npm install -g @mariozechner/pi-coding-agent`)
- [ ] Configure Pi RPC mode as entrypoint
- [ ] Expose necessary ports for RPC communication
- [ ] Set up volume mount point for session data
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M5.3 - Create Docker Compose file
- [ ] Create `docker-compose.yml`
- [ ] Define `backend` service (FastAPI)
- [ ] Define `pi` service (Pi RPC)

- [ ] Configure service dependencies (backend depends on pi)
- [ ] Set environment variables for each service
- [ ] Configure network for inter-service communication
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M5.4 - Configure inter-service communication
- [ ] Create Docker network for services
- [ ] Configure backend to connect to Pi via container hostname
- [ ] Update config to use service names instead of localhost
- [ ] Test network connectivity between containers
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M5.5 - Volume mounts for Pi sessions
- [ ] Create `data/` directory for persistent storage
- [ ] Mount volume for Pi session files (JSONL)
- [ ] Ensure proper file permissions in containers
- [ ] Test data persists across container restarts
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M5.6 - Test full stack in Docker Compose
- [ ] Run `docker-compose up`
- [ ] Verify all services start without errors
- [ ] Test chat flow end-to-end
- [ ] Test session persistence
- [ ] Test feedback submission

- [ ] Test data persists after `docker-compose down` and `up`
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M5.7 - Documentation for Docker deployment
- [ ] Document Docker prerequisites
- [ ] Document `docker-compose up` command
- [ ] Document environment variable configuration
- [ ] Document volume mount locations
- [ ] Document how to view logs
- [ ] Document how to stop and restart services
- [ ] Add troubleshooting section
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

## Architecture

### System Overview

```
┌─────────────┐    WebSocket     ┌─────────────────┐    JSON-RPC     ┌─────────┐
│   Browser   │ ◄──────────────► │  Python Backend │ ◄─────────────► │   Pi    │
│  (HTML/JS)  │                  │    (FastAPI)    │   (subprocess)  │  (RPC)  │
└─────────────┘                  └─────────────────┘                 └─────────┘
                                                                          │
                                                                          ▼
                                                               ┌──────────────────┐
                                                               │   Pi Sessions    │
                                                               │     (JSONL)      │
                                                               │  - messages      │
                                                               │  - feedback      │
                                                               └──────────────────┘
```

### Components

| Component    | Technology         | Responsibilities                                                                         |
| ------------ | ------------------ | ---------------------------------------------------------------------------------------- |
| **Frontend** | HTML/CSS/JS        | Chat UI, sidebar, WebSocket connection, feedback capture, display past sessions          |
| **Backend**  | Python/FastAPI     | Serve frontend, WebSocket handling, Pi subprocess management, session parsing, REST APIs |
| **Pi**       | Node.js (RPC mode) | Agent capabilities via JSON-RPC, session storage (JSONL)                                 |

### Data Storage

| Storage      | What's Stored                              | Managed By     |
| ------------ | ------------------------------------------ | -------------- |
| **Pi JSONL** | Sessions, messages, feedback (CustomEntry) | Pi + Extension |

> **Single Source of Truth:** Pi's JSONL session files store everything - messages AND feedback.
> Backend parses JSONL files to list sessions and retrieve messages.

### Communication Flow

1. User types message in browser
2. Frontend sends message via WebSocket to backend
3. Backend forwards to Pi via JSON-RPC (stdin)
4. Pi streams response via JSON-RPC (stdout)
5. Backend streams chunks to frontend via WebSocket
6. Pi saves messages to session JSONL automatically

### Feedback Flow

1. User clicks thumbs up/down on a message
2. Frontend sends feedback via WebSocket (includes message timestamp and sessionId)
3. Backend writes CustomEntry directly to the session JSONL file
4. Feedback persists in same file as messages

---

## User Interface

### Layout

```
┌─────────────┬──────────────────────────────┐
│  Sidebar    │         Main Chat            │
│             │                              │
│ [+ New]     │   Message history            │
│             │                              │
│ Session 3   │   ...                        │
│ Session 2   │                              │
│ Session 1   │   [User message]             │
│ (view-only) │   [Pi response] 👍👎         │
│             │                              │
│             │   ┌────────────────────┐     │
│             │   │ Type message...    │     │
│             │   └────────────────────┘     │
│             │                              │
│             │   [Session Feedback] 👍👎    │
└─────────────┴──────────────────────────────┘
```

### Key UI Elements

- **Sidebar**: Session list (view-only), new session button
- **Chat area**: Message history with streaming responses
- **Starter prompts**: Clickable example questions for new users
- **Feedback buttons**: Thumbs up/down on each Pi message
- **Session feedback**: Overall session rating at bottom of chat
- **Negative feedback modal**: Popup for comment when thumbs down

---

## Data Schema

### Pi Session JSONL Format

Session files are stored in `data/pi_sessions/` as JSONL (one JSON object per line).
See Pi's `docs/session.md` for full specification.

**Session Header** (first line):
```json
{"type":"session","version":3,"id":"uuid","timestamp":"2024-12-03T14:00:00.000Z","cwd":"/workspace"}
```

**Message Entry**:
```json
{
  "type": "message",
  "id": "a1b2c3d4",
  "parentId": "prev1234",
  "timestamp": "2024-12-03T14:00:01.000Z",
  "message": {
    "role": "user|assistant|toolResult",
    "content": [...],
    "timestamp": 1733234567890
  }
}
```

**Feedback Entry** (CustomEntry written by backend):
```json
{
  "type": "custom",
  "id": "f1e2d3c4",
  "parentId": "curr-leaf",
  "timestamp": "2024-12-03T14:05:00.000Z",
  "customType": "pi-portal-feedback",
  "data": {
    "targetTimestamp": 1733234567890,
    "rating": 1,
    "comment": null,
    "timestamp": 1733234600000
  }
}
```

**Key Fields for Feedback:**
| Field             | Type    | Description                                   |
| ----------------- | ------- | --------------------------------------------- |
| `targetTimestamp` | number  | Message's `timestamp` field (Unix ms)         |
| `rating`          | integer | -1 (negative), 0 (none), 1 (positive)         |
| `comment`         | string? | Optional comment (only for negative feedback) |
| `timestamp`       | number  | When feedback was submitted (Unix ms)         |

---

## Folder Structure

```
pi-portal/
├── backend/
│   ├── main.py           # FastAPI app entry point
│   ├── session_parser.py # Parse Pi's JSONL session files
│   ├── pi_client.py      # Pi RPC communication
│   └── websocket.py      # WebSocket handlers
├── frontend/
│   ├── index.html        # Main HTML page
│   ├── styles.css        # Styling
│   └── app.js            # Client-side logic
├── data/
│   └── pi_sessions/      # Pi's JSONL sessions (messages + feedback)
├── Procfile              # Honcho process definitions
├── pyproject.toml        # Python project config (uv)
├── README.md             # Project documentation
├── SPEC.md               # This file
├── AGENTS.md             # Implementation guidelines
└── .gitignore            # Git ignore patterns
```

---

## Technology Stack

| Component       | Technology          | Version |
| --------------- | ------------------- | ------- |
| Language        | Python              | 3.12    |
| Package Manager | uv                  | latest  |
| Web Framework   | FastAPI             | latest  |
| ASGI Server     | uvicorn             | latest  |
| Session Storage | Pi JSONL files      | -       |
| Process Manager | Honcho              | latest  |
| Frontend        | HTML/CSS/JavaScript | -       |
| Pi Integration  | JSON-RPC            | -       |
| Pi Extension    | TypeScript          | -       |
| Deployment      | Docker Compose      | later   |

### Suggested JS Libraries (nice-to-have)

| Library      | Purpose                  |
| ------------ | ------------------------ |
| marked.js    | Markdown rendering       |
| highlight.js | Code syntax highlighting |

---

## Out of Scope

- Authentication/authorization (local machine assumption)
- Shared sessions between users
- Continuing past sessions (view-only)
- Editing Pi's JSONL session files
- Docker Compose in initial milestones (M5)

---

## Notes

- **Feedback integers**: Use -1 (negative), 0 (none), 1 (positive)
- **Feedback comments**: Only relevant for negative feedback; clear when rating changes to positive/neutral
- **Pi sessions**: Pi's JSONL sessions are the single source of truth for messages AND feedback
- **Feedback storage**: Backend appends CustomEntry to session JSONL; identified by `targetTimestamp`
- **No database**: All data stored in Pi's JSONL files directly
- **WebSocket protocol**: Define JSON structure during M1 implementation
