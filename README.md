# Pi Portal

A web-based chat interface for the Pi coding agent, designed for R&D researchers who want a simple way to interact with Pi without CLI knowledge.

## Features

- **Chat Interface**: Simple web UI to chat with Pi
- **Session Persistence**: Save and view past conversations
- **Feedback System**: Rate messages and sessions with optional comments
- **MLflow Tracing**: Trace conversations for analysis and improvement

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

# Start all services
make start
```

### Development

```bash
# See all available commands
make help

# Start all services (FastAPI, MLflow, Pi)
make start

# Start only the web server
make start-web

# Start only MLflow
make start-mlflow
```

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
                                    SQLite + MLflow
```

## Project Structure

```
pi-portal/
├── backend/          # FastAPI backend
├── frontend/         # HTML/CSS/JS frontend
├── data/             # SQLite database and Pi sessions
├── Procfile          # Honcho process definitions
├── pyproject.toml    # Python dependencies
└── README.md
```

## Documentation

- [SPEC.md](SPEC.md) - Full project specification
- [AGENTS.md](AGENTS.md) - Implementation guidelines

## License

[Add license]
