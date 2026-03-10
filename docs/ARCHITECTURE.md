# Pi Portal Architecture

Technical architecture documentation for Pi Portal.

---

## Table of Contents

- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Session Storage](#session-storage)
- [Technology Stack](#technology-stack)
- [Design Decisions](#design-decisions)
- [Scalability Considerations](#scalability-considerations)

---

## System Overview

Pi Portal is a web-based interface for the Pi coding agent, designed to run locally on a researcher's laptop. The architecture prioritizes simplicity and reliability over scalability.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Browser                          │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  HTML/CSS   │  │ JavaScript   │  │  WebSocket Client    │  │
│  │   (UI)      │  │  (Logic)     │  │  (Real-time Comm)    │  │
│  └─────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ WebSocket (ws://)
                             │ HTTP (REST API)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Python Backend                              │
│                        (FastAPI)                                │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐  │
│  │   WebSocket    │  │  REST API      │  │  Pi Client      │  │
│  │   Handler      │  │  Endpoints     │  │  Manager        │  │
│  └────────────────┘  └────────────────┘  └─────────────────┘  │
│                                                   │             │
│  ┌────────────────────────────────────────────────┘             │
│  │                                                              │
│  │  ┌────────────────┐  ┌────────────────┐                    │
│  │  │  Session       │  │  Config        │                    │
│  │  │  Parser        │  │  Manager       │                    │
│  └─►└────────────────┘  └────────────────┘                    │
└────────────────────────────┬────────────────────────────────────┘
                             │ JSON-RPC (stdin/stdout)
                             │ Subprocess
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Pi Agent (Node.js)                         │
│                     Subprocess (RPC mode)                       │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐  │
│  │  RPC Server    │  │  Agent Logic   │  │  Tool Executor  │  │
│  │  (JSON-RPC)    │  │  (Reasoning)   │  │  (Read/Bash...) │  │
│  └────────────────┘  └────────────────┘  └─────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ File I/O
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    File System Storage                          │
│                                                                 │
│                    data/pi_sessions/                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  session-<uuid>.jsonl                                    │  │
│  │                                                          │  │
│  │  {"type":"session","id":"...","timestamp":"..."}         │  │
│  │  {"type":"message","role":"user","content":"..."}        │  │
│  │  {"type":"message","role":"assistant","content":"..."}   │  │
│  │  {"type":"custom","customType":"pi-portal-feedback"...}  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Frontend (Browser)

**Technology:** HTML5, CSS3, Vanilla JavaScript

**Files:**
- `frontend/index.html` - Page structure
- `frontend/styles.css` - Styling and theming
- `frontend/app.js` - Main application logic
- `frontend/error-handler.js` - Error notifications

**Responsibilities:**
- Render user interface
- Manage WebSocket connection
- Handle user interactions
- Display streaming responses
- Submit feedback
- Navigate sessions

**Key Features:**
- No framework dependencies (vanilla JS)
- WebSocket client with auto-reconnect
- Real-time message streaming
- Session management UI
- Feedback submission UI
- Responsive design (mobile-friendly)

### Backend (FastAPI)

**Technology:** Python 3.12+, FastAPI, Uvicorn

**Modules:**

#### `backend/main.py`
- FastAPI application setup
- Route registration
- CORS configuration
- Static file serving
- Startup/shutdown handlers

#### `backend/websocket.py`
- WebSocket connection management
- Message routing
- Pi subprocess communication bridge
- Streaming response handling
- Connection lifecycle management

#### `backend/pi_client.py`
- Pi subprocess spawning
- JSON-RPC communication (stdin/stdout)
- Process lifecycle management
- Crash detection and recovery
- Session directory configuration

#### `backend/session_parser.py`
- Parse Pi's JSONL session format
- Extract messages and metadata
- Extract feedback entries
- Build session history tree
- Generate session summaries

#### `backend/config.py`
- Pydantic-based configuration
- Environment variable management
- Path resolution
- Type validation
- Default values

**Responsibilities:**
- Serve web frontend
- Manage WebSocket connections
- Control Pi subprocess lifecycle
- Parse and serve session data
- Write feedback to session files
- Handle errors and reconnections

### Pi Agent (Subprocess)

**Technology:** Node.js, Pi coding agent

**Mode:** RPC (JSON-RPC over stdin/stdout)

**Responsibilities:**
- Process user messages
- Generate responses with reasoning
- Execute tools (Read, Bash, Edit, Write)
- Save sessions to JSONL files
- Stream responses back to backend

**Configuration:**
- Session directory: Configured by backend
- RPC mode: Enabled with `--mode rpc`
- Session saving: Always enabled

---

## Data Flow

### User Sends Message

```
1. User types message and clicks send
   │
   ▼
2. Frontend sends via WebSocket
   │ {"type": "message", "content": "Hello Pi"}
   ▼
3. Backend receives WebSocket message
   │
   ▼
4. Backend forwards to Pi subprocess (JSON-RPC)
   │ {"method": "message", "params": {"content": "Hello Pi"}}
   ▼
5. Pi processes message
   │ - Generates response
   │ - Executes tools if needed
   │ - Saves to session JSONL
   ▼
6. Pi streams response chunks
   │ {"type": "text_delta", "delta": "Hello!"}
   │ {"type": "thinking_delta", "delta": "..."}
   │ {"type": "tool_start", "name": "Read"}
   ▼
7. Backend forwards chunks to frontend
   │
   ▼
8. Frontend displays streaming response
   │ - Appends text deltas
   │ - Shows thinking section
   │ - Displays tool indicators
   ▼
9. Response complete
   │
   ▼
10. Feedback buttons appear
```

### User Submits Feedback

```
1. User clicks thumbs up/down
   │
   ▼
2. Frontend sends feedback via WebSocket
   │ {"type": "feedback", "timestamp": 123, "rating": 1}
   ▼
3. Backend receives feedback
   │
   ▼
4. Backend opens session JSONL file
   │
   ▼
5. Backend appends CustomEntry
   │ {"type": "custom", "customType": "pi-portal-feedback", ...}
   ▼
6. Feedback persisted to file
   │
   ▼
7. Backend sends confirmation
   │ {"type": "feedback_saved"}
   ▼
8. Frontend shows saved animation
```

### User Views Past Session

```
1. User clicks session in sidebar
   │
   ▼
2. Frontend fetches session via REST API
   │ GET /api/sessions/{id}
   ▼
3. Backend finds session JSONL file
   │
   ▼
4. Backend parses JSONL file
   │ - Extract messages
   │ - Extract feedback
   │ - Match feedback to messages
   ▼
5. Backend returns JSON response
   │
   ▼
6. Frontend renders messages
   │ - Display in chronological order
   │ - Show existing feedback
   │ - Enable read-only mode
   ▼
7. User can view and rate messages
```

---

## Session Storage

### JSONL Format

Pi uses **JSON Lines** format - one JSON object per line.

**File location:** `data/pi_sessions/session-<uuid>.jsonl`

**Structure:**

```jsonl
{"type":"session","version":3,"id":"uuid","timestamp":"2024-12-03T14:00:00.000Z","cwd":"/workspace"}
{"type":"message","id":"msg1","parentId":null,"timestamp":"2024-12-03T14:00:01.000Z","message":{"role":"user","content":"Hello"}}
{"type":"message","id":"msg2","parentId":"msg1","timestamp":"2024-12-03T14:00:02.000Z","message":{"role":"assistant","content":"Hi!"}}
{"type":"custom","id":"fb1","parentId":"msg2","timestamp":"2024-12-03T14:00:03.000Z","customType":"pi-portal-feedback","data":{"target_timestamp":1733234568000,"rating":1,"comment":null}}
```

### Entry Types

**Session Header:**
```json
{
  "type": "session",
  "version": 3,
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-12-03T14:00:00.000Z",
  "cwd": "/workspace"
}
```

**Message Entry:**
```json
{
  "type": "message",
  "id": "msg123",
  "parentId": "msg122",
  "timestamp": "2024-12-03T14:00:01.000Z",
  "message": {
    "role": "user",
    "content": "Hello Pi",
    "timestamp": 1733234567890
  }
}
```

**Feedback Entry (CustomEntry):**
```json
{
  "type": "custom",
  "id": "fb123",
  "parentId": "msg123",
  "timestamp": "2024-12-03T14:00:02.000Z",
  "customType": "pi-portal-feedback",
  "data": {
    "target_timestamp": 1733234567890,
    "rating": 1,
    "comment": null,
    "timestamp": 1733234600000
  }
}
```

### Tree Structure

Messages form a tree via `parentId` references:

```
session (root)
  └─ msg1 (user)
      └─ msg2 (assistant)
          └─ msg3 (user)
              └─ msg4 (assistant)
```

Feedback entries reference their parent message.

### Parsing Strategy

1. Read JSONL file line by line
2. Parse session header (first line)
3. Collect all message entries
4. Collect all feedback entries
5. Build tree from parentId references
6. Traverse tree from leaf to root
7. Match feedback by `target_timestamp`

---

## Technology Stack

### Frontend

| Technology | Purpose | Version |
|------------|---------|---------|
| HTML5 | Page structure | - |
| CSS3 | Styling, animations | - |
| JavaScript | Application logic | ES6+ |
| WebSocket API | Real-time communication | Native |

**No frameworks or libraries** - Pure vanilla JavaScript for simplicity.

### Backend

| Technology | Purpose | Version |
|------------|---------|---------|
| Python | Primary language | 3.12+ |
| FastAPI | Web framework | Latest |
| Uvicorn | ASGI server | Latest |
| Pydantic | Configuration, validation | Latest |
| pytest | Testing | Latest |
| ruff | Linting, formatting | Latest |

**Package management:** uv (fast Python package manager)

### Pi Agent

| Technology | Purpose | Version |
|------------|---------|---------|
| Node.js | Runtime | 18+ |
| Pi | Coding agent | Latest |

**Installation:** `npm install -g @mariozechner/pi-coding-agent`

### Storage

| Technology | Purpose | Format |
|------------|---------|--------|
| File System | Session storage | JSONL |
| JSON Lines | Data format | .jsonl |

**No database required** - All data in structured text files.

---

## Design Decisions

### Why No Database?

**Decision:** Use Pi's JSONL session files directly instead of a database.

**Rationale:**
- **Single source of truth:** Avoid sync issues between DB and Pi
- **Simplicity:** No database setup, migrations, or management
- **Portability:** Session files are human-readable and portable
- **Pi compatibility:** Work with Pi's native format
- **Low complexity:** Fewer moving parts, easier to debug

**Trade-offs:**
- Limited query capabilities
- No indexing (slower for many sessions)
- No concurrent access control

**Acceptable because:**
- Small scale (< 10 users, local deployment)
- Read-heavy workload (mostly viewing sessions)
- Sessions accessed one at a time

### Why WebSocket Instead of HTTP Polling?

**Decision:** Use WebSocket for real-time communication.

**Rationale:**
- **Real-time streaming:** Display Pi's response as it's generated
- **Bi-directional:** Client and server can both initiate messages
- **Efficient:** One persistent connection vs. many HTTP requests
- **Low latency:** Immediate message delivery

**Trade-offs:**
- More complex than REST API
- Requires connection management
- Harder to debug

**Acceptable because:**
- Chat requires real-time updates
- Streaming improves user experience significantly
- WebSocket is well-supported in browsers

### Why Subprocess Instead of HTTP Service?

**Decision:** Run Pi as a subprocess, not a separate HTTP service.

**Rationale:**
- **Simplicity:** One process to manage (backend starts Pi)
- **Pi RPC mode:** Pi has built-in RPC mode via stdin/stdout
- **Process isolation:** Pi crash doesn't crash backend
- **Resource management:** Backend can restart Pi as needed

**Trade-offs:**
- Can't scale to multiple backend instances
- Subprocess communication overhead

**Acceptable because:**
- Single-user deployment (laptop)
- No need for horizontal scaling
- Simplicity > scalability for this use case

### Why No Authentication?

**Decision:** No authentication or authorization.

**Rationale:**
- **Local deployment:** Running on researcher's own laptop
- **Single user:** One person per instance
- **Simplicity:** Reduces complexity and setup time

**Trade-offs:**
- Cannot deploy to shared environment
- No multi-user support

**Acceptable because:**
- Designed for local use only
- Can add authentication later if needed

---

## Scalability Considerations

### Current Limitations

**Single Backend Instance:**
- One backend process per deployment
- Pi subprocess tied to backend lifecycle
- No load balancing

**File-Based Storage:**
- Linear scan to list sessions
- No indexing or caching
- Slower with many sessions (>1000)

**In-Memory State:**
- WebSocket connections in memory
- Session list refreshed on every API call
- No persistent state

### If Scaling Needed

**For 10-100 users:**
- Add SQLite database for session metadata
- Keep JSONL for detailed storage
- Add caching layer (Redis)
- Index sessions by timestamp

**For 100+ users:**
- Migrate to PostgreSQL
- Separate Pi service (HTTP API)
- Add authentication (OAuth, JWT)
- Use message queue (RabbitMQ, Redis)
- Add load balancer
- Horizontal scaling of backend

**For 1000+ users:**
- Microservices architecture
- Dedicated session storage service
- Distributed message queue
- CDN for frontend assets
- Database sharding

---

## Security Considerations

### Current Security

**Local Deployment Only:**
- Binds to `0.0.0.0:8000` (all interfaces)
- No authentication required
- No encryption (HTTP, not HTTPS)
- CORS allows all origins

**Acceptable because:**
- Runs on researcher's laptop
- Firewall protects from external access
- No sensitive data exposure

### For Production Deployment

**Must add:**
- **HTTPS/WSS:** Encrypt traffic
- **Authentication:** User login (OAuth, JWT)
- **Authorization:** Role-based access control
- **Rate limiting:** Prevent abuse
- **Input validation:** Prevent injection attacks
- **Output sanitization:** Prevent XSS
- **CORS restrictions:** Limit allowed origins
- **Session timeouts:** Auto-logout
- **Audit logging:** Track user actions

---

## Error Handling

### Frontend Errors

**WebSocket Disconnection:**
- Auto-reconnect with exponential backoff
- Max 10 attempts, 2-10 second delay
- Display connection status to user
- Show notification on reconnect success/failure

**API Errors:**
- Display error notifications
- Log to console for debugging
- Retry failed requests where appropriate
- Graceful degradation

### Backend Errors

**Pi Subprocess Crash:**
- Detect crash via return code
- Log crash details
- Restart Pi automatically
- Return error message to client
- Exponential backoff for repeated crashes

**Session Parse Errors:**
- Try to recover partial data
- Log error with file path
- Return 500 with error message
- Skip corrupted entries when possible

**File System Errors:**
- Handle missing directories
- Handle permission errors
- Create directories if needed
- Return appropriate HTTP status codes

---

## Testing Strategy

### Unit Tests

**Backend:**
- Test each module independently
- Mock external dependencies (Pi, filesystem)
- Test error scenarios
- Use pytest fixtures

**Coverage targets:**
- Business logic: 90%+
- API endpoints: 80%+
- Error handlers: 70%+

### Integration Tests

**WebSocket Flow:**
- Test full message roundtrip
- Test reconnection logic
- Test multiple concurrent connections

**Session Storage:**
- Test reading real JSONL files
- Test feedback writing
- Test concurrent file access

### Manual Testing

**UI Testing:**
- Test in multiple browsers
- Test on mobile devices
- Test all user flows
- Test error scenarios

---

## Performance Considerations

### Current Performance

**Expected Load:**
- < 10 concurrent users
- < 100 sessions per user
- < 1000 messages per session
- < 10 requests/second

**Bottlenecks:**
- Pi subprocess (CPU-bound reasoning)
- JSONL file parsing (I/O-bound)
- WebSocket fan-out (memory-bound)

### Optimizations

**Implemented:**
- Streaming responses (reduce latency)
- Async I/O (non-blocking file reads)
- WebSocket (efficient real-time comm)

**Potential:**
- Cache parsed sessions in memory
- Index sessions by timestamp
- Lazy load session list (pagination)
- Compress old sessions

---

## Monitoring & Debugging

### Logging

**Backend Logging:**
```python
logger.info("Pi process started")
logger.warning("Pi crashed, restarting...")
logger.error("Failed to parse session")
```

**Log Levels:**
- INFO: Normal operations
- WARNING: Recoverable errors
- ERROR: Unrecoverable errors

**Log Output:**
- Console (development)
- File (production)

### Debugging

**Frontend:**
- Browser console
- Network tab (WebSocket frames)
- Application tab (LocalStorage, etc.)

**Backend:**
- Python debugger (pdb)
- Log statements
- Pytest with -v flag

**Pi:**
- Pi's own logging
- Stdout/stderr captured by backend

---

## Deployment

### Development

```bash
make install
make start
```

**Configuration:**
- Set `PI_PORTAL_SERVER_RELOAD=true`
- Use `localhost` for testing
- Enable verbose logging

### Local Production

```bash
make install
cp .env.example .env
# Edit .env
make start
```

**Configuration:**
- Use absolute paths
- Disable reload
- Set appropriate host/port

### Docker (Future)

See M5 in SPEC.md for Docker Compose deployment plan.

---

## Future Enhancements

### Short Term

- Session search and filtering
- Export sessions (JSON, Markdown)
- Keyboard shortcuts
- Theme customization

### Medium Term

- Multiple Pi configurations
- Session sharing (read-only links)
- Analytics dashboard
- Batch feedback submission

### Long Term

- Multi-user support
- Cloud deployment
- Advanced analytics
- Machine learning on feedback data

---

## References

- [Pi Documentation](https://github.com/mariozechner/pi-coding-agent)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [JSON Lines Format](https://jsonlines.org/)
- [SPEC.md](../SPEC.md) - Detailed specification
- [API.md](API.md) - API reference
