# Changelog

## Unreleased

* Added comprehensive testing and bug fixes (M4.5)
* Created TESTING.md with 60+ manual test cases
* Created TEST_RESULTS.md documenting all automated test results
* Verified all 132 automated tests passing
* Verified all API endpoints working correctly
* Verified server startup and health checks
* Verified session file parsing and retrieval
* Completed code review with no critical issues found
* No bugs identified in automated testing
* Added comprehensive documentation (M4.4)
* Rewrote README.md with detailed installation, configuration, and usage guides
* Added docs/API.md with complete REST and WebSocket API reference
* Added docs/USER_GUIDE.md with end-user focused guide and examples
* Added docs/ARCHITECTURE.md with technical architecture and design decisions
* Documented all configuration options and environment variables
* Added troubleshooting sections and FAQ
* Added example conversations and code snippets
* Added UI polish with smooth animations and transitions (M4.2)
* Added `:active` states to all interactive buttons for tactile feedback
* Added hover animations to session list, starter prompts, and buttons
* Improved typing indicator with color transitions and better animation
* Added fade-in and expand animations for collapsible sections
* Enhanced responsive design with 1024px and 480px breakpoints
* Added `:focus-visible` outlines for keyboard navigation accessibility
* Improved mobile layout with better padding and sizing across screen sizes
* Added smooth scroll behavior with scroll-padding
* Enhanced modal button interactions with lift effects and shadows
* Added comprehensive error handling (M4.1)
* Added error notification system with toast-style messages
* Added frontend/error-handler.js for centralized error management
* Improved error messages for session loading failures
* Added specific error handling for FileNotFoundError and ValueError
* Added reconnection success notifications
* Added feedback submission error notifications
* Improved logging for debugging
* Removed Honcho and Procfile (unnecessary for single service)
* Removed Pi from process management (backend manages Pi as subprocess)
* Added configuration system using Pydantic BaseSettings
* Added `.env.example` file with all configuration options
* All environment variables use PI_PORTAL_ prefix for namespacing
* Made Pi executable path configurable (PI_PORTAL_PI_EXECUTABLE)
* Made Pi session directory configurable (PI_PORTAL_PI_SESSION_DIR)
* Made server host/port configurable (PI_PORTAL_SERVER_HOST, PI_PORTAL_SERVER_PORT)
* Added server reload option for development (PI_PORTAL_SERVER_RELOAD)
* Configuration validates field types and supports .env file loading
* Removed unused Pi feedback extension (backend writes directly to JSONL)
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
* ~~Added Honcho process management~~ (removed - single service doesn't need process manager)
* Added Makefile with `install`, `start`, `test`, `fmt`, `check`, and `clean` commands
* Added Pi RPC client for subprocess communication with Pi agent
* Added chat interface with sidebar, message area, and input field
* Added configurable starter prompts via `config/starter_prompts.json`
* Added WebSocket endpoint for real-time chat communication
* Added frontend WebSocket client with auto-reconnect and connection status display
* Fixed WebSocket handler to gracefully handle malformed messages (null content, unknown types)
* Fixed WebSocket hanging when slash commands return no content (e.g., `/feedback` without arguments)
