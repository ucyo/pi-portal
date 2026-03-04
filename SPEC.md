# Pi Portal - Specification

## Overview

A web-based chat interface for the Pi coding agent, designed for R&D researchers who are not technical in agent development. Provides a simple, accessible way to interact with Pi while capturing session data and feedback for analysis and improvement.

| Aspect             | Description                                       |
| ------------------ | ------------------------------------------------- |
| **Project Name**   | pi-portal                                         |
| **Users**          | R&D researchers (<10), one instance per laptop    |
| **User Goal**      | Simple chat interface to Pi without CLI knowledge |
| **Developer Goal** | Collect traced sessions + feedback to improve Pi  |

## Execution Plan

| Phase | Milestone                 | Description                                                   |
| ----- | ------------------------- | ------------------------------------------------------------- |
| M0    | Project Setup             | Infrastructure, folder structure, dependencies, Honcho config |
| M1    | Basic Chat                | Frontend UI + backend WebSocket + Pi integration              |
| M2    | Session Persistence       | Parse Pi's JSONL sessions, session list, view past sessions   |
| M3    | Feedback System           | Per-message feedback via Pi extension (stored in JSONL)       |
| M4    | MLflow Integration        | Tracing + feedback sync to MLflow                             |
| M5    | Polish & Refinement       | UI improvements, error handling, documentation                |
| M6    | Docker Compose Deployment | Split services into containers                                |
| M7    | Databricks MLflow Export  | Migrate to hosted MLflow                                      |

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
- [x] Add aiosqlite dependency (async SQLite)
- [x] Add MLflow client dependency
- [x] Add websockets dependency
- [x] Document Python version requirement in `pyproject.toml`
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M0.3 - Set up Honcho
- [x] Install Honcho (`uv add honcho --dev`)
- [x] Create `Procfile` with entries for:
  - FastAPI (uvicorn)
  - MLflow server
  - Pi (RPC mode)
- [x] Test `honcho start` runs all processes
- [x] Document Honcho usage in README
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
- [ ] Create `GET /api/sessions/{id}` endpoint
- [ ] Find session file by ID in `data/pi_sessions/`
- [ ] Parse and return full message history
- [ ] Handle click on session in sidebar
- [ ] Load and display messages in chat area (read-only)
- [ ] Disable input field for past sessions
- [ ] Show visual indicator that session is read-only
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M2.5 - New session button
- [ ] Add "New Session" button in sidebar
- [ ] Send `new_session` RPC command to Pi
- [ ] Clear chat area in frontend
- [ ] Show starter prompts again
- [ ] Update sidebar session list
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

### M3 - Feedback System

> **Architecture Note:** Feedback is stored in Pi's session JSONL as CustomEntry via a Pi extension.
> The extension (`.pi/extensions/feedback.ts`) registers a `/feedback` command.
> Messages are identified by their `timestamp` field (unique within a session).

#### M3.1 - Pi feedback extension
- [x] Create `.pi/extensions/feedback.ts`
- [x] Register `/feedback` command accepting JSON args
- [x] Store feedback as CustomEntry with `customType: "pi-portal-feedback"`
- [x] Data format: `{targetTimestamp, rating, comment, timestamp}`
- [x] Register `/feedback-list` command for debugging
- [x] Test extension via RPC prompt command
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M3.2 - Message feedback UI
- [ ] Track message timestamps when rendering assistant messages
- [ ] Add thumbs up/down buttons to each Pi response
- [ ] Style feedback buttons (subtle, non-intrusive)
- [ ] Highlight selected feedback state
- [ ] Allow changing feedback (click other thumb)
- [ ] Only show feedback buttons on assistant messages
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M3.3 - Negative feedback modal
- [ ] Create modal/popup component in HTML/CSS
- [ ] Trigger modal when thumbs down is clicked
- [ ] Include text area for comment
- [ ] Add "Submit" and "Cancel" buttons
- [ ] Close modal on submit or cancel
- [ ] Allow submitting without comment (optional text)
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M3.4 - Feedback submission via Pi extension
- [ ] Send feedback via WebSocket to backend
- [ ] Backend invokes Pi `/feedback` command via RPC prompt
- [ ] Format: `/feedback {"targetTimestamp":123,"rating":1,"comment":null}`
- [ ] Handle extension response (notify event)
- [ ] Update UI to reflect saved state
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M3.5 - Load existing feedback
- [ ] Parse CustomEntry with `customType: "pi-portal-feedback"` from session
- [ ] Match feedback to messages by `targetTimestamp`
- [ ] Display correct thumbs state on each message
- [ ] Handle multiple feedback entries for same message (use latest)
- [ ] Show feedback on past sessions (read-only view)
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

### M4 - MLflow Integration

#### M4.1 - MLflow setup
- [ ] Add MLflow server to Honcho Procfile
- [ ] Create `backend/config.py` for configuration
- [ ] Add configurable MLflow tracking URI (env variable or config file)
- [ ] Default to local MLflow (`http://localhost:5000`)
- [ ] Test MLflow server starts and UI is accessible
- [ ] Document MLflow configuration options
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M4.2 - Create MLflow run per session
- [ ] Create `backend/mlflow_client.py` module
- [ ] Create MLflow experiment for the application
- [ ] Start new MLflow run when chat session starts
- [ ] Store `mlflow_run_id` in session database record
- [ ] End MLflow run when session is archived
- [ ] Handle MLflow connection failures gracefully
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M4.3 - Trace Pi interactions
- [ ] Use `mlflow.start_span()` for manual tracing
- [ ] Create span for each user prompt
- [ ] Create span for each Pi response
- [ ] Create child spans for tool calls from Pi
- [ ] Set inputs/outputs on each span
- [ ] Record timing automatically via span context
- [ ] Add session metadata as run parameters
- [ ] Handle tracing errors without breaking chat
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M4.4 - Sync feedback to MLflow
- [ ] When feedback is submitted, retrieve session's `mlflow_run_id`
- [ ] Log message feedback as run tags: `feedback_msg_{timestamp}` = `-1/0/1`
- [ ] Log feedback comments as run tags: `feedback_comment_msg_{timestamp}`
- [ ] Update tags when feedback changes (overwrite previous)
- [ ] Handle MLflow sync failures gracefully (feedback still saved in Pi session)
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M4.5 - Verify traces in MLflow UI
- [ ] Start a test chat session
- [ ] Verify MLflow run appears in UI
- [ ] Verify spans show prompt/response flow
- [ ] Verify tool calls appear as child spans
- [ ] Verify feedback tags are visible on run
- [ ] Document how to access and navigate MLflow UI
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

### M5 - Polish & Refinement

#### M5.1 - Error handling
- [ ] Handle WebSocket disconnection gracefully
- [ ] Handle Pi subprocess crash and auto-restart
- [ ] Handle MLflow connection failures (continue without tracing)
- [ ] Handle session file parsing errors
- [ ] Display user-friendly error messages in UI
- [ ] Log errors server-side for debugging
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M5.2 - UI polish
- [ ] Add loading spinner while Pi is responding
- [ ] Add smooth animations for message appearance
- [ ] Improve typography and spacing
- [ ] Style scrollbars
- [ ] Add hover states for interactive elements
- [ ] Ensure consistent color scheme
- [ ] Test on different screen sizes
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M5.3 - Configuration file
- [ ] Create `config.yaml` or `.env` file for settings
- [ ] Configurable MLflow tracking URI
- [ ] Configurable Pi executable path
- [ ] Configurable Pi session directory
- [ ] Configurable server host/port
- [ ] Load config on startup
- [ ] Document all configuration options
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M5.4 - Documentation
- [ ] Write README with project overview
- [ ] Document installation steps
- [ ] Document development setup (Honcho)
- [ ] Document configuration options
- [ ] Document usage guide for end users
- [ ] Add architecture diagram
- [ ] Document API endpoints
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M5.5 - Testing & bug fixes
- [ ] Manual testing of full chat flow
- [ ] Test session persistence and retrieval
- [ ] Test feedback submission and display
- [ ] Test MLflow tracing and tag syncing
- [ ] Test error scenarios (Pi crash, disconnect)
- [ ] Fix identified bugs
- [ ] Final review and cleanup
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

### M6 - Docker Compose Deployment

#### M6.1 - Create Dockerfile for FastAPI backend
- [ ] Create `backend/Dockerfile`
- [ ] Use Python base image
- [ ] Install uv in container
- [ ] Copy and install dependencies
- [ ] Copy application code
- [ ] Configure uvicorn as entrypoint
- [ ] Expose port 8000
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M6.2 - Create Dockerfile for Pi service
- [ ] Create `pi/Dockerfile`
- [ ] Use Node.js base image (Pi is Node-based)
- [ ] Install Pi globally (`npm install -g @mariozechner/pi-coding-agent`)
- [ ] Configure Pi RPC mode as entrypoint
- [ ] Expose necessary ports for RPC communication
- [ ] Set up volume mount point for session data
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M6.3 - Create Docker Compose file
- [ ] Create `docker-compose.yml`
- [ ] Define `backend` service (FastAPI)
- [ ] Define `pi` service (Pi RPC)
- [ ] Define `mlflow` service (MLflow server)
- [ ] Configure service dependencies (backend depends on pi, mlflow)
- [ ] Set environment variables for each service
- [ ] Configure network for inter-service communication
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M6.4 - Configure inter-service communication
- [ ] Create Docker network for services
- [ ] Configure backend to connect to Pi via container hostname
- [ ] Configure backend to connect to MLflow via container hostname
- [ ] Update config to use service names instead of localhost
- [ ] Test network connectivity between containers
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M6.5 - Volume mounts for Pi sessions
- [ ] Create `data/` directory for persistent storage
- [ ] Mount volume for Pi session files (JSONL)
- [ ] Mount volume for MLflow artifacts
- [ ] Ensure proper file permissions in containers
- [ ] Test data persists across container restarts
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M6.6 - Test full stack in Docker Compose
- [ ] Run `docker-compose up`
- [ ] Verify all services start without errors
- [ ] Test chat flow end-to-end
- [ ] Test session persistence
- [ ] Test feedback submission
- [ ] Test MLflow tracing
- [ ] Test data persists after `docker-compose down` and `up`
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M6.7 - Documentation for Docker deployment
- [ ] Document Docker prerequisites
- [ ] Document `docker-compose up` command
- [ ] Document environment variable configuration
- [ ] Document volume mount locations
- [ ] Document how to view logs
- [ ] Document how to stop and restart services
- [ ] Add troubleshooting section
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

### M7 - Databricks MLflow Export

#### M7.1 - Databricks MLflow connection setup
- [ ] Document Databricks workspace requirements
- [ ] Add Databricks authentication config options (token, host)
- [ ] Update config file to support Databricks tracking URI
- [ ] Install `databricks-sdk` dependency if needed
- [ ] Test authentication with Databricks workspace
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M7.2 - Export existing local traces to Databricks MLflow
- [ ] Create export script for local MLflow data
- [ ] Read existing runs from local MLflow
- [ ] Recreate runs in Databricks MLflow
- [ ] Preserve spans, metrics, tags, and artifacts
- [ ] Handle large data sets in batches
- [ ] Log export progress and errors
- [ ] Verify exported data in Databricks UI
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M7.3 - Switch live tracing to Databricks endpoint
- [ ] Update MLflow tracking URI config to Databricks
- [ ] Test new sessions trace directly to Databricks
- [ ] Verify spans appear in Databricks MLflow
- [ ] Verify feedback tags sync to Databricks
- [ ] Handle Databricks connection failures gracefully
- [ ] Optionally keep local MLflow as fallback
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M7.4 - Verify traces in Databricks MLflow UI
- [ ] Access Databricks MLflow UI
- [ ] Verify experiment and runs appear
- [ ] Verify spans show prompt/response flow
- [ ] Verify feedback tags are visible
- [ ] Compare with local MLflow data for consistency
- [ ] Test querying and filtering traces
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

#### M7.5 - Documentation for Databricks configuration
- [ ] Document Databricks workspace setup requirements
- [ ] Document authentication options (token, OAuth)
- [ ] Document how to switch from local to Databricks MLflow
- [ ] Document export script usage
- [ ] Document Databricks UI navigation for traces
- [ ] Add troubleshooting for common connection issues
<!-- ⛔ STOP: Complete this sub-milestone, run tests, then wait for user review before continuing -->

---

## Architecture

### System Overview

```
┌─────────────┐    WebSocket     ┌─────────────────┐    JSON-RPC     ┌─────────┐
│   Browser   │ ◄──────────────► │  Python Backend │ ◄─────────────► │   Pi    │
│  (HTML/JS)  │                  │    (FastAPI)    │   (subprocess)  │  (RPC)  │
└─────────────┘                  └─────────────────┘                 └─────────┘
                                         │                                │
                                         │                                ▼
                                         │                     ┌──────────────────┐
                                         │                     │   Pi Sessions    │
                                         │                     │     (JSONL)      │
                                         │                     │  - messages      │
                                         │                     │  - feedback      │
                                         │                     └──────────────────┘
                                         ▼
                                 ┌───────────────┐
                                 │    MLflow     │
                                 │   (tracing)   │
                                 └───────────────┘
```

### Components

| Component        | Technology         | Responsibilities                                                                          |
| ---------------- | ------------------ | ----------------------------------------------------------------------------------------- |
| **Frontend**     | HTML/CSS/JS        | Chat UI, sidebar, WebSocket connection, feedback capture, display past sessions          |
| **Backend**      | Python/FastAPI     | Serve frontend, WebSocket handling, Pi subprocess management, session parsing, REST APIs |
| **Pi**           | Node.js (RPC mode) | Agent capabilities via JSON-RPC, session storage (JSONL), feedback extension             |
| **Pi Extension** | TypeScript         | `/feedback` command to store user feedback as CustomEntry in session                     |
| **MLflow**       | Python             | Local tracing server, configurable endpoint URL                                          |

### Data Storage

| Storage       | What's Stored                               | Managed By       |
| ------------- | ------------------------------------------- | ---------------- |
| **Pi JSONL**  | Sessions, messages, feedback (CustomEntry)  | Pi + Extension   |
| **MLflow**    | Traces, spans, feedback tags (for analysis) | MLflow           |

> **Single Source of Truth:** Pi's JSONL session files store everything - messages AND feedback.
> No SQLite database needed. Backend parses JSONL files to list sessions and retrieve messages.

### Communication Flow

1. User types message in browser
2. Frontend sends message via WebSocket to backend
3. Backend forwards to Pi via JSON-RPC (stdin)
4. Pi streams response via JSON-RPC (stdout)
5. Backend streams chunks to frontend via WebSocket
6. Pi saves messages to session JSONL automatically
7. Backend logs traces to MLflow

### Feedback Flow

1. User clicks thumbs up/down on a message
2. Frontend sends feedback via WebSocket (includes message timestamp)
3. Backend invokes `/feedback` command via Pi RPC
4. Pi extension appends CustomEntry to session JSONL
5. Feedback persists in same file as messages

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

**Feedback Entry** (CustomEntry from Pi extension):
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
| Field             | Type    | Description                                    |
| ----------------- | ------- | ---------------------------------------------- |
| `targetTimestamp` | number  | Message's `timestamp` field (Unix ms)          |
| `rating`          | integer | -1 (negative), 0 (none), 1 (positive)          |
| `comment`         | string? | Optional comment (only for negative feedback)  |
| `timestamp`       | number  | When feedback was submitted (Unix ms)          |

### MLflow Data

**Run-level tags for feedback:**
- `feedback_msg_{timestamp}`: Message feedback rating
- `feedback_comment_msg_{timestamp}`: Message feedback comment

**Spans:**
- User prompts with inputs
- Pi responses with outputs
- Tool calls as child spans

---

## Folder Structure

```
pi-portal/
├── .pi/
│   └── extensions/
│       └── feedback.ts   # Pi extension for feedback storage
├── backend/
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Configuration management
│   ├── session_parser.py # Parse Pi's JSONL session files
│   ├── pi_client.py      # Pi RPC communication
│   ├── mlflow_client.py  # MLflow tracing
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
| Tracing         | MLflow              | latest  |
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
- Docker Compose in initial milestones (M6)
- Databricks MLflow in initial milestones (M7)

---

## Notes

- **Feedback integers**: Use -1 (negative), 0 (none), 1 (positive)
- **Feedback comments**: Only relevant for negative feedback; clear when rating changes to positive/neutral
- **Pi sessions**: Pi's JSONL sessions are the single source of truth for messages AND feedback
- **Feedback storage**: Pi extension appends CustomEntry to session; identified by `targetTimestamp`
- **No SQLite**: Removed in favor of parsing Pi's JSONL files directly
- **MLflow endpoint**: Configurable URL for later Databricks migration
- **WebSocket protocol**: Define JSON structure during M1 implementation
