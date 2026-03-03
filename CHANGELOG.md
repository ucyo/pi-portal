# Changelog

## Unreleased

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
