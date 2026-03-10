# Pi Portal

A web-based chat interface for the Pi coding agent, designed for R&D researchers who want a simple way to interact with Pi without CLI knowledge.

## Features

- **Chat Interface**: Simple web UI to chat with Pi
- **Session Persistence**: Save and view past conversations
- **Feedback System**: Rate messages with optional comments

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- [Pi](https://github.com/mariozechner/pi-coding-agent) coding agent
- Node.js (for Pi)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd pi-portal

# Install dependencies
make install

# (Optional) Copy and customize configuration
cp .env.example .env

# Start all services
make start
```

### Development

```bash
# See all available commands
make help

# Start the web server (Pi is started automatically by the backend)
make start

# Or start directly
make start-web
```

### Configuration

Pi Portal uses Pydantic BaseSettings for configuration. All environment variables use the `PI_PORTAL_` prefix.

Copy `.env.example` to `.env` and customize:

```bash
# Pi Configuration
PI_PORTAL_PI_EXECUTABLE=pi                    # Path to Pi executable
PI_PORTAL_PI_SESSION_DIR=data/pi_sessions     # Session storage directory

# Server Configuration
PI_PORTAL_SERVER_HOST=0.0.0.0                 # Server bind address
PI_PORTAL_SERVER_PORT=8000                    # Server port
PI_PORTAL_SERVER_RELOAD=false                 # Enable auto-reload (development)
```

All settings have sensible defaults and are optional. Configuration is validated using Pydantic.

### Testing

```bash
# Run all tests
make test

# Run tests + format/lint
make check

# Format and lint code
make fmt
```

## Architecture

```
Browser (HTML/JS) <--WebSocket--> FastAPI Backend <--JSON-RPC--> Pi (subprocess)
                                                                        |
                                                                        v
                                                                 Pi Sessions (JSONL)
```

## Project Structure

```
pi-portal/
├── backend/          # FastAPI backend
├── frontend/         # HTML/CSS/JS frontend
├── data/             # Pi sessions (JSONL)
├── pyproject.toml    # Python dependencies
└── README.md
```

## Documentation

- [SPEC.md](SPEC.md) - Full project specification
- [AGENTS.md](AGENTS.md) - Implementation guidelines

## License

[Add license]
