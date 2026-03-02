# Agent Instructions

You are building **pi-portal**, a web-based chat interface for the Pi coding agent, designed for R&D researchers. Follow the specification in `SPEC.md`.

## Build System

Use `make` for common tasks (run `make help` for all options):

```bash
make install     # Install dependencies
make start       # Start all services (web, mlflow, pi)
make start-web   # Start only the web server
make test        # Run all tests
make fmt         # Format and lint code (ruff)
make check       # Run tests + fmt
make clean       # Remove generated files
```

For adding dependencies:
- `uv add <package>` - add a dependency
- `uv add --dev <package>` - add a dev dependency

## Before Starting Work

1. **Always read `PROGRESS.md` first** to understand current status
2. Review the execution plan in `SPEC.md`
3. Check which milestone to work on next
4. Read the specific milestone section for detailed tasks

## Working on the Project

- Follow milestones sequentially (M0 → M1 → M2 → ...)
- Complete sub-milestones in order (M1.1 → M1.2 → M1.3)
- Check off tasks in `SPEC.md` as you complete them
- Validate each sub-milestone before moving on
- Keep code simple - no over-engineering

### Code Style

**Python (Backend):**
- Use type hints for function parameters and return values
- Use async/await for database and I/O operations
- Follow PEP 8 naming conventions
- Keep functions small and focused
- Use Pydantic models for request/response validation

**JavaScript (Frontend):**
- Use vanilla JS (no frameworks)
- Use `const` and `let`, not `var`
- Use template literals for HTML generation
- Keep functions small and focused
- Comment complex logic

**HTML/CSS:**
- Use semantic HTML elements
- Use CSS custom properties for colors/theming
- Mobile-first responsive design
- Keep CSS organized by component

### Testing Approach

**Automated tests** with pytest:
```bash
make test              # Run all tests
make test-v            # Verbose output
make check             # Run tests + lint
```

**When adding new features:**
- Add tests for new endpoints in `tests/test_*.py`
- Use the `client` fixture from `conftest.py` for async HTTP tests
- Run `make check` before marking milestone complete

**Manual testing** for UI and integration:
- Test each feature in the browser after implementation
- Test WebSocket connection and reconnection
- Test Pi communication end-to-end
- Test error scenarios (Pi crash, disconnect)
- Verify data persists in SQLite
- Check MLflow UI for traces

## After Completing Work

Before finishing a session:
```bash
# Run tests and linter
make check

# Verify server starts
make start-web

# Check all services run together
make start
```

## Git Workflow

### Changelog

Update `CHANGELOG.md` before committing notable changes:

- Add entries to the `## Unreleased` section
- Focus on user-facing changes (features, fixes, breaking changes)
- Start each entry with a past-tense verb
- Keep entries concise but descriptive
- Ignore insignificant changes (typos, internal refactoring)

Example:
```markdown
## Unreleased

* Added WebSocket support for real-time chat
* Fixed session persistence when browser refreshes
```

### Commit Messages

Use Conventional Commits format:

```
<type>(<scope>): <summary>
```

- **type**: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `perf`
- **scope**: optional, short noun for affected area (e.g., `api`, `ui`, `setup`)
- **summary**: imperative mood, <= 72 chars, no trailing period

Examples:
```
feat(chat): add WebSocket message streaming
fix(db): resolve session persistence on reconnect
docs: update README with deployment instructions
```

## Pacing and Natural Stop Points

**Important:** Do NOT blindly continue through the entire execution plan in one session.

### Stop Points

- **Stop after completing a sub-milestone** (e.g., M1.1, M1.2) to let the user review
- **Stop after completing a major milestone** (e.g., all of M1) for user testing and commit
- **Stop after introducing new components** for verification
- **Stop when work-in-progress** - note what's left in PROGRESS.md

### Why Pacing Matters

- The user needs opportunities to review code and test manually
- Changes should be committed in logical chunks
- Issues are easier to debug in smaller increments
- The user may want to adjust direction based on results

### When Stopping

Summarize:
1. What was completed
2. What was tested and how
3. What the next steps would be

## Progress Tracking

Update `PROGRESS.md` as you work:

- Keep entries **very short** (one line per update)
- Format: `- [x] M0.1: done` or `- [ ] M0.2: in progress - notes`
- Only add new lines when starting or completing a sub-milestone
- Note any blockers or issues discovered

Example:
```markdown
# Progress

## Current: M1 - Basic Chat

- [x] M0.1: completed
- [x] M0.2: completed
- [ ] M1.1: in progress - basic structure done, need styling

## Notes
- Pi RPC connection verified working
```

## Key Files

| File | Purpose |
|------|---------|
| `SPEC.md` | Full specification with milestones and tasks |
| `PROGRESS.md` | Current progress and status |
| `CHANGELOG.md` | Notable changes (update before commits) |
| `AGENTS.md` | This file - agent instructions |
| `README.md` | User-facing documentation |
| `Makefile` | Build commands (`make help` for options) |
| `Procfile` | Honcho process definitions |
| `pyproject.toml` | Python project config (uv) |

## Project Structure

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
├── tests/
│   ├── conftest.py       # Pytest fixtures
│   ├── test_app.py       # App configuration tests
│   ├── test_health.py    # Health endpoint tests
│   └── test_procfile.py  # Procfile tests
├── data/
│   ├── app.db            # SQLite database (generated)
│   └── pi_sessions/      # Pi's JSONL sessions
├── Procfile              # Honcho process definitions
├── pyproject.toml        # Python project config
├── README.md
├── SPEC.md
├── AGENTS.md
└── .gitignore
```

## Technology Reminders

### uv (Package Manager)
```bash
uv init                  # Initialize project
uv add fastapi uvicorn   # Add dependencies
uv add --dev honcho      # Add dev dependency
uv sync                  # Install all deps
uv run <command>         # Run command in venv
```

### FastAPI
```python
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/", StaticFiles(directory="frontend", html=True))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # ...
```

### Pi RPC
```bash
# Start Pi in RPC mode (keeps sessions)
pi --mode rpc

# Communication via stdin/stdout JSON
```

### Honcho
```bash
# Procfile format:
web: uv run uvicorn backend.main:app --port 8000
mlflow: uv run mlflow server --port 5000
pi: pi --mode rpc
```

### SQLite with aiosqlite
```python
import aiosqlite

async with aiosqlite.connect("data/app.db") as db:
    await db.execute("INSERT INTO ...")
    await db.commit()
```

### MLflow Tracing
```python
import mlflow

with mlflow.start_span(name="user_prompt") as span:
    span.set_inputs({"prompt": message})
    # ... process ...
    span.set_outputs({"response": response})
```

## Validation Checklist

Before marking a milestone complete:

- [ ] All tasks in SPEC.md checked off
- [ ] All checks pass (`make check`)
- [ ] Server starts without errors (`make start-web`)
- [ ] Manual testing done in browser
- [ ] WebSocket connection works
- [ ] Data persists correctly
- [ ] PROGRESS.md updated

## Pi Integration Notes

- Pi runs as subprocess, communicate via stdin/stdout
- Use `pi --mode rpc` (keeps session saving enabled)
- Configure Pi session directory to `data/pi_sessions/`
- Parse JSON-RPC responses from Pi
- Handle Pi process crashes gracefully
- Don't modify Pi's JSONL session files directly

## Feedback System Notes

- Ratings are integers: -1 (negative), 0 (none), 1 (positive)
- Comments only relevant for negative feedback
- Clear comments when rating changes from -1 to 0 or 1
- Store in SQLite (for UI) and sync to MLflow (for analysis)
