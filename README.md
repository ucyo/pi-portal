# Pi Portal

A web-based chat interface for the [Pi coding agent](https://github.com/mariozechner/pi-coding-agent), designed for R&D researchers who want a simple, accessible way to interact with Pi without requiring CLI knowledge.

## Overview

Pi Portal provides a clean, modern web interface to chat with Pi while automatically capturing session data and feedback for analysis and improvement. It's designed to run locally on a researcher's laptop and requires no complex setup or infrastructure.

### Key Features

- **💬 Real-time Chat**: WebSocket-based streaming chat with Pi
- **📚 Session Management**: Automatic session persistence and history viewing
- **👍👎 Feedback System**: Rate individual messages to improve Pi's responses
- **🎨 Modern UI**: Clean, responsive interface with dark theme
- **🔧 Simple Setup**: Single command to start, no database required
- **📱 Mobile Friendly**: Works on desktop, tablet, and mobile devices

### Use Cases

- **R&D Research**: Collect conversational data and feedback from researchers
- **Pi Testing**: Test Pi's capabilities in a user-friendly environment
- **Code Assistance**: Get help with coding tasks through a web interface
- **Data Collection**: Gather structured feedback for Pi improvement

---

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Development](#development)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Quick Start

### Prerequisites

- **Python 3.12+** - [Download Python](https://www.python.org/downloads/)
- **uv** - Fast Python package manager ([Installation guide](https://github.com/astral-sh/uv))
- **Pi** - The Pi coding agent ([Installation guide](https://github.com/mariozechner/pi-coding-agent))
- **Node.js 18+** - Required for Pi ([Download Node.js](https://nodejs.org/))

### Installation

**Option 1: Local Installation (Recommended for Development)**

```bash
# Clone the repository
git clone https://github.com/yourusername/pi-portal.git
cd pi-portal

# Install dependencies
make install

# Start the server
make start
```

**Option 2: Docker (Recommended for Production)**

```bash
# Clone the repository
git clone https://github.com/yourusername/pi-portal.git
cd pi-portal

# Start with Docker Compose
make docker-up

# View logs
make docker-logs
```

The web interface will be available at **http://localhost:8000**

See [Docker Deployment Guide](docs/DOCKER.md) for detailed Docker instructions.

### First Run

1. Open **http://localhost:8000** in your browser
2. Click a starter prompt or type your question
3. Chat with Pi in real-time
4. Rate responses with 👍 or 👎
5. View past sessions in the sidebar

---

## Installation

### 1. Install Prerequisites

**Install uv (Python package manager):**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Install Pi:**
```bash
npm install -g @mariozechner/pi-coding-agent

# Verify installation
pi --version
```

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/pi-portal.git
cd pi-portal

# Install Python dependencies
make install

# Or manually with uv
uv sync
```

### 3. Configuration (Optional)

Copy the example configuration file:
```bash
cp .env.example .env
```

Edit `.env` to customize settings (see [Configuration](#configuration) section).

### 4. Start the Server

```bash
# Start the web server (Pi is managed automatically)
make start

# Or start directly
uv run python -m backend.server
```

The server will:
- Start FastAPI on `http://localhost:8000`
- Serve the web interface at the root URL
- Start Pi subprocess when first client connects
- Save sessions to `data/pi_sessions/`

---

## Configuration

Pi Portal uses environment variables for configuration. All variables use the `PI_PORTAL_` prefix.

### Configuration File

Create a `.env` file in the project root:

```bash
# Pi Configuration
PI_PORTAL_PI_EXECUTABLE=pi
PI_PORTAL_PI_SESSION_DIR=data/pi_sessions

# Server Configuration
PI_PORTAL_SERVER_HOST=0.0.0.0
PI_PORTAL_SERVER_PORT=8000
PI_PORTAL_SERVER_RELOAD=false
```

### Configuration Options

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `PI_PORTAL_PI_EXECUTABLE` | Path to Pi executable | `pi` | `/usr/local/bin/pi` |
| `PI_PORTAL_PI_SESSION_DIR` | Directory for session storage | `data/pi_sessions` | `/var/lib/pi-portal/sessions` |
| `PI_PORTAL_SERVER_HOST` | Server bind address | `0.0.0.0` | `127.0.0.1` |
| `PI_PORTAL_SERVER_PORT` | Server port | `8000` | `3000` |
| `PI_PORTAL_SERVER_RELOAD` | Auto-reload on code changes | `false` | `true` (dev only) |

### Starter Prompts

Customize starter prompts by editing `config/starter_prompts.json`:

```json
{
  "prompts": [
    {
      "icon": "🐛",
      "text": "Help me debug this error"
    },
    {
      "icon": "📝",
      "text": "Explain this code snippet"
    }
  ]
}
```

---

## Usage Guide

### Starting a Conversation

1. **Open the web interface** at http://localhost:8000
2. **Click a starter prompt** or type your own question
3. **Send your message** by clicking the send button or pressing Enter
4. **Watch Pi respond** in real-time with streaming text

### Session Management

**Create a New Session:**
- Click the **"+ New"** button in the sidebar
- This starts a fresh conversation with Pi

**View Past Sessions:**
- Click any session in the sidebar to view its history
- Past sessions are **read-only** (indicated by a 📖 banner)
- You can still rate messages in past sessions

**Active Session Indicator:**
- The current active session shows a **green dot** and border
- This is the session you can currently send messages to

### Providing Feedback

**Rate Individual Messages:**
1. Hover over any Pi response
2. Click **👍** for helpful responses
3. Click **👎** for unhelpful responses
4. For negative feedback, optionally add a comment explaining the issue

**Change Your Rating:**
- Click the opposite thumb to change your rating
- Click the same thumb again to remove your rating

**Feedback is Saved:**
- All feedback is stored in Pi's session files
- Feedback persists even after closing the browser
- Researchers can analyze feedback data later

### Understanding the Interface

**Sidebar (Left):**
- **Logo & Title**: Pi Portal branding
- **New Session Button**: Start fresh conversation
- **Session List**: View all past sessions
- **Connection Status**: WebSocket connection indicator

**Main Chat Area:**
- **Welcome Screen**: Starter prompts for new users
- **Messages**: Conversation history
- **Thinking Section**: Collapsible Pi reasoning (when available)
- **Tool Indicators**: Shows when Pi uses tools (Read, Bash, etc.)
- **Input Field**: Type your messages here

### Keyboard Shortcuts

- **Enter**: Send message
- **Shift + Enter**: New line in input
- **Tab**: Navigate between UI elements
- **Esc**: Close modal (feedback comment)

---

## Development

### Setup Development Environment

```bash
# Install all dependencies including dev tools
make install

# Enable auto-reload in .env
echo "PI_PORTAL_SERVER_RELOAD=true" >> .env

# Start with auto-reload
make start
```

### Available Commands

View all commands:
```bash
make help
```

Common development tasks:

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies |
| `make start` | Start the web server |
| `make test` | Run all tests |
| `make test-v` | Run tests with verbose output |
| `make fmt` | Format and lint code |
| `make check` | Run tests + format check |
| `make clean` | Remove generated files |

### Running Tests

```bash
# Run all tests
make test

# Run with verbose output
make test-v

# Run specific test file
uv run pytest tests/test_websocket.py -v

# Run with coverage
uv run pytest --cov=backend --cov-report=html
```

### Code Style

**Python:**
- Use `ruff` for formatting and linting
- Type hints required for function signatures
- Follow PEP 8 naming conventions
- Run `make fmt` before committing

**JavaScript:**
- Use vanilla JS (no frameworks)
- Use `const`/`let`, not `var`
- Use template literals for HTML
- Keep functions small and focused

**CSS:**
- Use CSS custom properties (variables)
- Mobile-first responsive design
- Organize by component

### Project Structure

```
pi-portal/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── server.py            # Server entry point
│   ├── config.py            # Configuration (Pydantic)
│   ├── websocket.py         # WebSocket handlers
│   ├── pi_client.py         # Pi subprocess management
│   └── session_parser.py    # Parse Pi JSONL sessions
├── frontend/
│   ├── index.html           # Main HTML page
│   ├── styles.css           # Styling
│   ├── app.js               # WebSocket + UI logic
│   └── error-handler.js     # Error notifications
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   └── test_*.py            # Test files
├── config/
│   └── starter_prompts.json # Starter prompt configuration
├── data/
│   └── pi_sessions/         # Pi's JSONL session files
├── .env.example             # Example configuration
├── pyproject.toml           # Python project config
├── Makefile                 # Build commands
└── README.md                # This file
```

---

## Architecture

### System Overview

```
┌─────────────┐                      ┌─────────────────┐                    ┌─────────┐
│   Browser   │  ◄── WebSocket ──►   │  Python Backend │  ◄── JSON-RPC ──►  │   Pi    │
│  (HTML/JS)  │                      │    (FastAPI)    │    (subprocess)    │  (RPC)  │
└─────────────┘                      └─────────────────┘                    └─────────┘
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

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | HTML/CSS/JavaScript | User interface, WebSocket client |
| **Backend** | Python/FastAPI | WebSocket server, Pi lifecycle, session parsing |
| **Pi Agent** | Node.js (subprocess) | AI coding agent, session storage |
| **Storage** | JSONL files | Single source of truth for all data |

### Data Flow

**User sends message:**
1. User types message in browser
2. Frontend sends via WebSocket to backend
3. Backend forwards to Pi subprocess (JSON-RPC)
4. Pi processes and streams response
5. Backend streams chunks to frontend via WebSocket
6. Frontend displays message in real-time
7. Pi saves to session JSONL file

**User provides feedback:**
1. User clicks 👍 or 👎 on a message
2. Frontend sends feedback via WebSocket
3. Backend appends feedback to session JSONL
4. Feedback persists with message timestamp reference

### Session Storage

Pi Portal uses **Pi's native JSONL session format** as the single source of truth:

- **No database required** - all data in JSONL files
- **Messages**: Stored by Pi automatically
- **Feedback**: Appended as `CustomEntry` by backend
- **Session metadata**: Extracted from JSONL headers
- **Message matching**: Uses timestamp field for feedback correlation

### WebSocket Protocol

**Client → Server:**
```json
{"type": "message", "content": "Hello Pi"}
{"type": "ping"}
{"type": "new_session"}
{"type": "feedback", "timestamp": 1234567890, "rating": 1, "comment": null, "session_id": "uuid"}
```

**Server → Client:**
```json
{"type": "status", "status": "connected"}
{"type": "message", "role": "user", "content": "..."}
{"type": "text_delta", "delta": "Hello"}
{"type": "thinking_delta", "delta": "Let me think..."}
{"type": "tool_start", "tool_use_id": "123", "name": "Read"}
{"type": "tool_end", "tool_use_id": "123", "success": true}
{"type": "error", "message": "Something went wrong"}
```

---

## API Reference

### REST Endpoints

#### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

#### `GET /api/sessions`

List all sessions with metadata.

**Response:**
```json
{
  "sessions": [
    {
      "id": "uuid",
      "display_name": "Debugging Python error",
      "created_at": "2024-12-03T14:00:00Z",
      "updated_at": "2024-12-03T14:30:00Z",
      "message_count": 10,
      "is_active": true
    }
  ]
}
```

#### `GET /api/sessions/{id}`

Get full session with messages and feedback.

**Response:**
```json
{
  "id": "uuid",
  "display_name": "Debugging Python error",
  "created_at": "2024-12-03T14:00:00Z",
  "messages": [
    {
      "role": "user",
      "content": "Help me debug this error",
      "message_timestamp": 1733234567890,
      "content_blocks": null
    },
    {
      "role": "assistant",
      "content": "I'll help you debug...",
      "message_timestamp": 1733234568123,
      "content_blocks": [
        {"type": "text", "text": "..."},
        {"type": "thinking", "thinking": "..."}
      ]
    }
  ],
  "feedback": [
    {
      "target_timestamp": 1733234568123,
      "rating": 1,
      "comment": null,
      "timestamp": 1733234600000
    }
  ]
}
```

**Error Responses:**
- `404` - Session not found
- `400` - Invalid session ID
- `500` - Failed to parse session file

#### `GET /api/config/starter-prompts`

Get configured starter prompts.

**Response:**
```json
{
  "prompts": [
    {"icon": "🐛", "text": "Help me debug this error"},
    {"icon": "📝", "text": "Explain this code snippet"}
  ]
}
```

### WebSocket Endpoint

#### `WS /ws`

WebSocket connection for real-time chat.

See [WebSocket Protocol](#websocket-protocol) section for message formats.

---

## Troubleshooting

### Server won't start

**Error: "Pi executable not found"**
```bash
# Check Pi is installed
which pi

# If not found, install Pi
npm install -g @mariozechner/pi-coding-agent

# Or set custom path in .env
echo "PI_PORTAL_PI_EXECUTABLE=/path/to/pi" >> .env
```

**Error: "Port 8000 already in use"**
```bash
# Use a different port
echo "PI_PORTAL_SERVER_PORT=3000" >> .env
make start
```

### WebSocket won't connect

**Check browser console:**
- Look for connection errors
- Verify server is running on correct port
- Check firewall settings

**Test WebSocket manually:**
```bash
# Install wscat
npm install -g wscat

# Connect to server
wscat -c ws://localhost:8000/ws
```

### Sessions not persisting

**Check session directory:**
```bash
# Verify directory exists
ls -la data/pi_sessions/

# Check permissions
chmod 755 data/pi_sessions/
```

**Check Pi configuration:**
```bash
# Pi should save sessions
# Verify PI_PORTAL_PI_SESSION_DIR is set correctly
```

### Pi crashes or hangs

**Check Pi logs:**
- Backend logs show Pi stdout/stderr
- Look for Pi subprocess errors

**Restart Pi:**
- WebSocket will auto-restart Pi on crash
- Or restart the backend server

**Common causes:**
- Out of memory (large files)
- Invalid tool execution
- Network issues (API calls)

### Browser issues

**Clear cache and reload:**
```bash
# Hard refresh
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (macOS)
```

**Check browser compatibility:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Contributing

### Reporting Issues

Please include:
- Browser and version
- Operating system
- Steps to reproduce
- Error messages (browser console + server logs)
- Screenshots (if applicable)

### Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make check`
5. Update documentation
6. Submit pull request

### Code Guidelines

- Follow existing code style
- Add tests for new features
- Update CHANGELOG.md
- Keep commits focused and atomic
- Write clear commit messages (Conventional Commits)

---

## License

[Add license information]

---

## Acknowledgments

- Built for the [Pi coding agent](https://github.com/mariozechner/pi-coding-agent)
- Uses [FastAPI](https://fastapi.tiangolo.com/) for backend
- Styled with custom CSS (no frameworks)

---

## Support

- **Documentation**: See [SPEC.md](SPEC.md) for detailed specification
- **Issues**: [GitHub Issues](https://github.com/yourusername/pi-portal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pi-portal/discussions)
