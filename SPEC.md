# Pi Portal - Specification

## Overview

A web-based chat interface for the Pi coding agent, designed for R&D researchers who are not technical in agent development. Provides a simple, accessible way to interact with Pi while capturing session data and feedback for analysis and improvement.

| Aspect | Description |
|--------|-------------|
| **Project Name** | pi-portal |
| **Users** | R&D researchers (<10), one instance per laptop |
| **User Goal** | Simple chat interface to Pi without CLI knowledge |
| **Developer Goal** | Collect traced sessions + feedback to improve Pi |

## Execution Plan

| Phase | Milestone | Description |
|-------|-----------|-------------|
| M0 | Project Setup | Infrastructure, folder structure, dependencies, Honcho config |
| M1 | Basic Chat | Frontend UI + backend WebSocket + Pi integration |
| M2 | Session Persistence | SQLite storage, session list, view past sessions |
| M3 | Feedback System | Per-message and per-session feedback with comments |
| M4 | MLflow Integration | Tracing + feedback sync to MLflow |
| M5 | Polish & Refinement | UI improvements, error handling, documentation |
| M6 | Docker Compose Deployment | Split services into containers |
| M7 | Databricks MLflow Export | Migrate to hosted MLflow |

## Milestones

### M0 - Project Setup

#### M0.1 - Initialize project structure
- [x] Create project root folder
- [x] Create `backend/` folder for FastAPI code
- [x] Create `frontend/` folder for HTML/CSS/JS
- [x] Create `README.md` with project overview
- [x] Create `.gitignore` (Python, SQLite, environment files)
- [x] Initialize git repository

#### M0.2 - Set up Python environment
- [x] Initialize project with `uv init`
- [x] Add FastAPI dependency with `uv add`
- [x] Add uvicorn dependency
- [x] Add aiosqlite dependency (async SQLite)
- [x] Add MLflow client dependency
- [x] Add websockets dependency
- [x] Document Python version requirement in `pyproject.toml`

#### M0.3 - Set up Honcho
- [x] Install Honcho (`uv add honcho --dev`)
- [x] Create `Procfile` with entries for:
  - FastAPI (uvicorn)
  - MLflow server
  - Pi (RPC mode)
- [x] Test `honcho start` runs all processes
- [x] Document Honcho usage in README

#### M0.4 - Basic FastAPI app
- [x] Create `backend/main.py` with FastAPI app
- [x] Add health check endpoint (`GET /health`)
- [x] Configure static file serving for `frontend/` folder
- [x] Add CORS configuration (for local development)
- [x] Test server starts and serves static files

#### M0.5 - Verify Pi RPC communication
- [x] Create `backend/pi_client.py` module for Pi communication
- [x] Implement subprocess spawn for `pi --mode rpc` (with session saving enabled)
- [x] Configure Pi session directory (e.g., `data/pi_sessions/`)
- [x] Send test prompt via JSON-RPC
- [x] Receive and parse response
- [x] Handle subprocess lifecycle (start/stop)
- [x] Add basic error handling for Pi crashes

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

#### M1.2 - WebSocket connection
- [ ] Create `frontend/app.js` for client-side logic
- [ ] Implement WebSocket connection to backend
- [ ] Handle connection open/close/error events
- [ ] Display connection status to user
- [ ] Implement reconnection logic on disconnect
- [ ] Create `backend/websocket.py` for WebSocket endpoint
- [ ] Register WebSocket route in FastAPI

#### M1.3 - Pi subprocess management
- [ ] Implement Pi process spawning on first WebSocket connection
- [ ] Manage Pi lifecycle per session (or shared instance)
- [ ] Handle stdin/stdout communication with Pi process
- [ ] Parse JSON-RPC responses from Pi
- [ ] Implement graceful shutdown of Pi process
- [ ] Handle Pi process crash and restart

#### M1.4 - Backend message routing
- [ ] Receive user message from WebSocket
- [ ] Format message as JSON-RPC request for Pi
- [ ] Send request to Pi subprocess
- [ ] Stream Pi response chunks back to WebSocket
- [ ] Handle tool execution events from Pi
- [ ] Send completion signal when Pi finishes responding

#### M1.5 - Frontend message rendering
- [ ] Display user messages in chat (right-aligned or distinct style)
- [ ] Display Pi responses in chat (left-aligned or distinct style)
- [ ] Render streaming responses (append chunks as they arrive)
- [ ] Auto-scroll to latest message
- [ ] Support markdown rendering in Pi responses
- [ ] Show typing/loading indicator while Pi is responding

---

### M2 - Session Persistence

#### M2.1 - SQLite setup
- [ ] Create `backend/database.py` module
- [ ] Define `sessions` table schema
- [ ] Define `messages` table schema
- [ ] Implement async database connection
- [ ] Create database initialization function
- [ ] Auto-create tables on startup if not exist
- [ ] Configure database file location (`data/app.db`)

#### M2.2 - Session storage
- [ ] Create new session record when chat starts
- [ ] Save user messages to database as they're sent
- [ ] Save Pi responses to database as they complete
- [ ] Update session `updated_at` timestamp on new messages
- [ ] Generate session title from first user message (truncated)

#### M2.3 - Session list API
- [ ] Create `GET /api/sessions` endpoint
- [ ] Return list of sessions (id, title, created_at, updated_at)
- [ ] Order by most recent first
- [ ] Include message count per session
- [ ] Paginate if needed (optional for small user base)

#### M2.4 - Sidebar session list
- [ ] Fetch session list from API on page load
- [ ] Render sessions in sidebar
- [ ] Display session title and date
- [ ] Highlight currently active session
- [ ] Auto-refresh list when new session created

#### M2.5 - View past session
- [ ] Create `GET /api/sessions/{id}` endpoint
- [ ] Return session with all messages
- [ ] Handle click on session in sidebar
- [ ] Load and display messages in chat area (read-only)
- [ ] Disable input field for past sessions
- [ ] Show visual indicator that session is read-only

#### M2.6 - New session button
- [ ] Add "New Session" button in sidebar
- [ ] Create `POST /api/sessions` endpoint
- [ ] Archive current session (set status to archived)
- [ ] Create new session record
- [ ] Clear chat area in frontend
- [ ] Show starter prompts again
- [ ] Update sidebar session list

---

### M3 - Feedback System

#### M3.1 - Message feedback UI
- [ ] Add thumbs up/down buttons to each Pi response
- [ ] Style feedback buttons (subtle, non-intrusive)
- [ ] Highlight selected feedback state
- [ ] Allow changing feedback (click other thumb)
- [ ] Only show feedback buttons on Pi messages (not user messages)

#### M3.2 - Negative feedback modal
- [ ] Create modal/popup component in HTML/CSS
- [ ] Trigger modal when thumbs down is clicked
- [ ] Include text area for comment
- [ ] Add "Submit" and "Cancel" buttons
- [ ] Close modal on submit or cancel
- [ ] Allow submitting without comment (optional text)
- [ ] Clear comment when feedback changes from negative to positive
- [ ] Confirm with user before clearing comment (optional prompt)

#### M3.3 - Message feedback API
- [ ] Create `POST /api/messages/{id}/feedback` endpoint
- [ ] Accept rating as integer: `-1` (negative), `0` (none), `1` (positive)
- [ ] Accept optional comment (only relevant for `-1`)
- [ ] Update message feedback in database
- [ ] Clear comment if rating changes from `-1` to `0` or `1`
- [ ] Return updated message feedback state

#### M3.4 - Session feedback UI
- [ ] Add session feedback section at bottom of main chat window
- [ ] Show thumbs up/down for overall session rating
- [ ] Use integer ratings: `-1` (negative), `0` (none), `1` (positive)
- [ ] Display current feedback state
- [ ] Trigger negative feedback modal for session comments
- [ ] Clear comment when changing from `-1` to `0` or `1`
- [ ] Allow changing session feedback

#### M3.5 - Session feedback API
- [ ] Create `POST /api/sessions/{id}/feedback` endpoint
- [ ] Accept rating as integer: `-1` (negative), `0` (none), `1` (positive)
- [ ] Accept optional comment (only relevant for `-1`)
- [ ] Update session feedback in database
- [ ] Clear comment if rating changes from `-1` to `0` or `1`
- [ ] Return updated session feedback state

#### M3.6 - Display feedback state
- [ ] Load existing feedback when viewing messages
- [ ] Show correct thumbs state on each Pi message
- [ ] Show correct session feedback state at chat bottom
- [ ] Persist feedback visually after page reload
- [ ] Show feedback on past sessions (read-only view)

---

### M4 - MLflow Integration

#### M4.1 - MLflow setup
- [ ] Add MLflow server to Honcho Procfile
- [ ] Create `backend/config.py` for configuration
- [ ] Add configurable MLflow tracking URI (env variable or config file)
- [ ] Default to local MLflow (`http://localhost:5000`)
- [ ] Test MLflow server starts and UI is accessible
- [ ] Document MLflow configuration options

#### M4.2 - Create MLflow run per session
- [ ] Create `backend/mlflow_client.py` module
- [ ] Create MLflow experiment for the application
- [ ] Start new MLflow run when chat session starts
- [ ] Store `mlflow_run_id` in session database record
- [ ] End MLflow run when session is archived
- [ ] Handle MLflow connection failures gracefully

#### M4.3 - Trace Pi interactions
- [ ] Use `mlflow.start_span()` for manual tracing
- [ ] Create span for each user prompt
- [ ] Create span for each Pi response
- [ ] Create child spans for tool calls from Pi
- [ ] Set inputs/outputs on each span
- [ ] Record timing automatically via span context
- [ ] Add session metadata as run parameters
- [ ] Handle tracing errors without breaking chat

#### M4.4 - Sync feedback to MLflow
- [ ] When feedback is submitted, retrieve session's `mlflow_run_id`
- [ ] Log message feedback as run tags: `feedback_msg_{id}` = `-1/0/1`
- [ ] Log feedback comments as run tags: `feedback_comment_msg_{id}`
- [ ] Log session feedback as run tags: `session_feedback`, `session_feedback_comment`
- [ ] Update tags when feedback changes (overwrite previous)
- [ ] Handle MLflow sync failures gracefully (don't lose feedback in SQLite)

#### M4.5 - Verify traces in MLflow UI
- [ ] Start a test chat session
- [ ] Verify MLflow run appears in UI
- [ ] Verify spans show prompt/response flow
- [ ] Verify tool calls appear as child spans
- [ ] Verify feedback tags are visible on run
- [ ] Document how to access and navigate MLflow UI

---

### M5 - Polish & Refinement

#### M5.1 - Error handling
- [ ] Handle WebSocket disconnection gracefully
- [ ] Handle Pi subprocess crash and auto-restart
- [ ] Handle MLflow connection failures (continue without tracing)
- [ ] Handle SQLite write failures
- [ ] Display user-friendly error messages in UI
- [ ] Log errors server-side for debugging

#### M5.2 - UI polish
- [ ] Add loading spinner while Pi is responding
- [ ] Add smooth animations for message appearance
- [ ] Improve typography and spacing
- [ ] Style scrollbars
- [ ] Add hover states for interactive elements
- [ ] Ensure consistent color scheme
- [ ] Test on different screen sizes

#### M5.3 - Configuration file
- [ ] Create `config.yaml` or `.env` file for settings
- [ ] Configurable MLflow tracking URI
- [ ] Configurable Pi executable path
- [ ] Configurable Pi session directory
- [ ] Configurable SQLite database path
- [ ] Configurable server host/port
- [ ] Load config on startup
- [ ] Document all configuration options

#### M5.4 - Documentation
- [ ] Write README with project overview
- [ ] Document installation steps
- [ ] Document development setup (Honcho)
- [ ] Document configuration options
- [ ] Document usage guide for end users
- [ ] Add architecture diagram
- [ ] Document API endpoints

#### M5.5 - Testing & bug fixes
- [ ] Manual testing of full chat flow
- [ ] Test session persistence and retrieval
- [ ] Test feedback submission and display
- [ ] Test MLflow tracing and tag syncing
- [ ] Test error scenarios (Pi crash, disconnect)
- [ ] Fix identified bugs
- [ ] Final review and cleanup

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

#### M6.2 - Create Dockerfile for Pi service
- [ ] Create `pi/Dockerfile`
- [ ] Use Node.js base image (Pi is Node-based)
- [ ] Install Pi globally (`npm install -g @mariozechner/pi-coding-agent`)
- [ ] Configure Pi RPC mode as entrypoint
- [ ] Expose necessary ports for RPC communication
- [ ] Set up volume mount point for session data

#### M6.3 - Create Docker Compose file
- [ ] Create `docker-compose.yml`
- [ ] Define `backend` service (FastAPI)
- [ ] Define `pi` service (Pi RPC)
- [ ] Define `mlflow` service (MLflow server)
- [ ] Configure service dependencies (backend depends on pi, mlflow)
- [ ] Set environment variables for each service
- [ ] Configure network for inter-service communication

#### M6.4 - Configure inter-service communication
- [ ] Create Docker network for services
- [ ] Configure backend to connect to Pi via container hostname
- [ ] Configure backend to connect to MLflow via container hostname
- [ ] Update config to use service names instead of localhost
- [ ] Test network connectivity between containers

#### M6.5 - Volume mounts for SQLite and Pi sessions
- [ ] Create `data/` directory for persistent storage
- [ ] Mount volume for SQLite database
- [ ] Mount volume for Pi session files
- [ ] Mount volume for MLflow artifacts
- [ ] Ensure proper file permissions in containers
- [ ] Test data persists across container restarts

#### M6.6 - Test full stack in Docker Compose
- [ ] Run `docker-compose up`
- [ ] Verify all services start without errors
- [ ] Test chat flow end-to-end
- [ ] Test session persistence
- [ ] Test feedback submission
- [ ] Test MLflow tracing
- [ ] Test data persists after `docker-compose down` and `up`

#### M6.7 - Documentation for Docker deployment
- [ ] Document Docker prerequisites
- [ ] Document `docker-compose up` command
- [ ] Document environment variable configuration
- [ ] Document volume mount locations
- [ ] Document how to view logs
- [ ] Document how to stop and restart services
- [ ] Add troubleshooting section

---

### M7 - Databricks MLflow Export

#### M7.1 - Databricks MLflow connection setup
- [ ] Document Databricks workspace requirements
- [ ] Add Databricks authentication config options (token, host)
- [ ] Update config file to support Databricks tracking URI
- [ ] Install `databricks-sdk` dependency if needed
- [ ] Test authentication with Databricks workspace

#### M7.2 - Export existing local traces to Databricks MLflow
- [ ] Create export script for local MLflow data
- [ ] Read existing runs from local MLflow
- [ ] Recreate runs in Databricks MLflow
- [ ] Preserve spans, metrics, tags, and artifacts
- [ ] Handle large data sets in batches
- [ ] Log export progress and errors
- [ ] Verify exported data in Databricks UI

#### M7.3 - Switch live tracing to Databricks endpoint
- [ ] Update MLflow tracking URI config to Databricks
- [ ] Test new sessions trace directly to Databricks
- [ ] Verify spans appear in Databricks MLflow
- [ ] Verify feedback tags sync to Databricks
- [ ] Handle Databricks connection failures gracefully
- [ ] Optionally keep local MLflow as fallback

#### M7.4 - Verify traces in Databricks MLflow UI
- [ ] Access Databricks MLflow UI
- [ ] Verify experiment and runs appear
- [ ] Verify spans show prompt/response flow
- [ ] Verify feedback tags are visible
- [ ] Compare with local MLflow data for consistency
- [ ] Test querying and filtering traces

#### M7.5 - Documentation for Databricks configuration
- [ ] Document Databricks workspace setup requirements
- [ ] Document authentication options (token, OAuth)
- [ ] Document how to switch from local to Databricks MLflow
- [ ] Document export script usage
- [ ] Document Databricks UI navigation for traces
- [ ] Add troubleshooting for common connection issues

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
                                 ┌───────────────┐
                                 │    SQLite     │
                                 │  (sessions,   │
                                 │   feedback)   │
                                 └───────────────┘
                                         │
                                         ▼
                                 ┌───────────────┐
                                 │    MLflow     │
                                 │   (tracing)   │
                                 └───────────────┘
```

### Components

| Component | Technology | Responsibilities |
|-----------|------------|------------------|
| **Frontend** | HTML/CSS/JS | Chat UI, sidebar, WebSocket connection, feedback capture, display past sessions |
| **Backend** | Python/FastAPI | Serve frontend, WebSocket handling, Pi subprocess management, SQLite storage, MLflow tracing, REST endpoints |
| **Pi** | Node.js (RPC mode) | Agent capabilities via JSON-RPC, maintains own JSONL sessions |
| **MLflow** | Python | Local tracing server, configurable endpoint URL |
| **SQLite** | File-based DB | Sessions + feedback storage |

### Data Storage

| Storage | What's Stored | Managed By |
|---------|---------------|------------|
| **SQLite** | Session metadata, messages, feedback (for UI) | Backend |
| **MLflow** | Traces, spans, feedback tags (for analysis) | MLflow |
| **Pi JSONL** | Pi's native session data | Pi (untouched) |

### Communication Flow

1. User types message in browser
2. Frontend sends message via WebSocket to backend
3. Backend forwards to Pi via JSON-RPC (stdin)
4. Pi streams response via JSON-RPC (stdout)
5. Backend streams chunks to frontend via WebSocket
6. Backend saves messages to SQLite
7. Backend logs traces to MLflow

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

### SQLite Tables

**sessions**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Auto-generated from first message |
| created_at | DATETIME | Session start time |
| updated_at | DATETIME | Last activity time |
| mlflow_run_id | TEXT | Links to MLflow run |
| status | TEXT | active/archived |
| feedback_rating | INTEGER | -1, 0, or 1 |
| feedback_comment | TEXT | Comment if negative |

**messages**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| session_id | INTEGER | Foreign key to sessions |
| role | TEXT | user/assistant |
| content | TEXT | Message text |
| created_at | DATETIME | Message timestamp |
| feedback_rating | INTEGER | -1, 0, or 1 |
| feedback_comment | TEXT | Comment if negative |

### MLflow Data

**Run-level tags for feedback:**
- `feedback_msg_{id}`: Message feedback rating
- `feedback_comment_msg_{id}`: Message feedback comment
- `session_feedback`: Session feedback rating
- `session_feedback_comment`: Session feedback comment

**Spans:**
- User prompts with inputs
- Pi responses with outputs
- Tool calls as child spans

---

## Folder Structure

```
pi-portal/
├── backend/
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Configuration management
│   ├── database.py       # SQLite setup and queries
│   ├── pi_client.py      # Pi RPC communication
│   ├── mlflow_client.py  # MLflow tracing
│   └── websocket.py      # WebSocket handlers
├── frontend/
│   ├── index.html        # Main HTML page
│   ├── styles.css        # Styling
│   └── app.js            # Client-side logic
├── data/
│   ├── app.db            # SQLite database
│   └── pi_sessions/      # Pi's JSONL sessions
├── Procfile              # Honcho process definitions
├── pyproject.toml        # Python project config (uv)
├── README.md             # Project documentation
├── SPEC.md               # This file
├── AGENTS.md             # Implementation guidelines
└── .gitignore            # Git ignore patterns
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.12 |
| Package Manager | uv | latest |
| Web Framework | FastAPI | latest |
| ASGI Server | uvicorn | latest |
| Database | SQLite (aiosqlite) | latest |
| Tracing | MLflow | latest |
| Process Manager | Honcho | latest |
| Frontend | HTML/CSS/JavaScript | - |
| Pi Integration | JSON-RPC | - |
| Deployment | Docker Compose | later |

### Suggested JS Libraries (nice-to-have)

| Library | Purpose |
|---------|---------|
| marked.js | Markdown rendering |
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
- **Pi sessions**: Pi maintains its own JSONL sessions; we don't modify them
- **MLflow endpoint**: Configurable URL for later Databricks migration
- **WebSocket protocol**: Define JSON structure during M1 implementation
