# Changelog

## Unreleased

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
* Added Honcho process management with Procfile for web, mlflow, and pi services
* Added Makefile with `install`, `start`, `test`, `fmt`, `check`, and `clean` commands
* Added Pi RPC client for subprocess communication with Pi agent
* Added chat interface with sidebar, message area, and input field
* Added configurable starter prompts via `config/starter_prompts.json`
* Added WebSocket endpoint for real-time chat communication
* Added frontend WebSocket client with auto-reconnect and connection status display
* Fixed WebSocket handler to gracefully handle malformed messages (null content, unknown types)
