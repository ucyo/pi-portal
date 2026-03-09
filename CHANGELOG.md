# Changelog

## Unreleased

* Removed MLflow integration (simplified architecture)
* Removed aiosqlite dependency (no longer needed)
* Added test for multiple feedback entries (use latest timestamp)
* Fixed feedback for past sessions being written to wrong session file
* Fixed feedback display showing first entry instead of most recent
* Added negative feedback modal with optional comment textarea
* Added thumbs up/down feedback buttons on assistant messages
* Added visual indicator for active session (green dot + left border)
* Simplified session state management (2 variables instead of 3)
* Added "New Session" button to start fresh conversation
* Added WebSocket new_session command to create new Pi session
* Added UI reset when starting new session (clears chat, shows welcome)
* Fixed current session remaining editable when switching between sessions
* Added session_id tracking from session files for accurate active session detection
* Added GET /api/sessions/{id} endpoint to fetch full session with messages
* Added session viewing - click sidebar to load and display past session
* Added read-only mode with banner and disabled input for past sessions
* Added GET /api/sessions endpoint to list all sessions with metadata
* Added session file parser for Pi's JSONL format (extracts messages, feedback, metadata)
* Added Pi feedback extension for storing ratings in session JSONL
* Changed architecture to use Pi session files instead of SQLite for persistence
* Added tests for feedback extension and session parser
* Added streaming message display with real-time text updates
* Added collapsible "Thinking..." section showing Pi's reasoning
* Added tool execution indicators with status (running/success/error)
* Added basic markdown rendering (code blocks, bold, italic)
* Added Pi subprocess integration with WebSocket for real-time chat
* Added crash recovery with automatic Pi restart (exponential backoff)
* Added structured logging for Pi communication (TX/RX format)
* Added FastAPI backend with health check endpoint
* Added static file serving and CORS support for web frontend
* Added Honcho process management with Procfile for web and pi services
* Added Makefile with `install`, `start`, `test`, `fmt`, `check`, and `clean` commands
* Added Pi RPC client for subprocess communication with Pi agent
* Added chat interface with sidebar, message area, and input field
* Added configurable starter prompts via `config/starter_prompts.json`
* Added WebSocket endpoint for real-time chat communication
* Added frontend WebSocket client with auto-reconnect and connection status display
* Fixed WebSocket handler to gracefully handle malformed messages (null content, unknown types)
* Fixed WebSocket hanging when slash commands return no content (e.g., `/feedback` without arguments)
