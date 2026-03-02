"""Integration tests for Pi RPC client.

These tests require Pi to be installed and available in PATH.
They are marked with @pytest.mark.integration and can be skipped with:
    pytest -m "not integration"
"""

import shutil

import pytest

from backend.pi_client import PiClient

# Skip all tests in this module if Pi is not available
pytestmark = pytest.mark.integration


def pi_available() -> bool:
    """Check if Pi executable is available."""
    return shutil.which("pi") is not None


@pytest.fixture
async def pi_client(tmp_path):
    """Create a Pi client with a temporary session directory."""
    session_dir = tmp_path / "pi_sessions"
    client = PiClient(session_dir=session_dir)
    yield client
    # Cleanup: stop client if still running
    if client.is_running:
        await client.stop()


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_pi_start_and_stop(pi_client):
    """Pi process should start and stop correctly."""
    assert not pi_client.is_running

    await pi_client.start()
    assert pi_client.is_running

    await pi_client.stop()
    assert not pi_client.is_running


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_pi_get_state(pi_client):
    """Pi should return state with model information."""
    await pi_client.start()

    state = await pi_client.get_state()

    assert state is not None
    assert "model" in state
    assert "thinkingLevel" in state
    assert "sessionFile" in state

    model = state["model"]
    assert "provider" in model
    assert "id" in model
    assert "name" in model
    assert "reasoning" in model


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_pi_prompt_simple_math(pi_client):
    """Pi should respond correctly to a simple math prompt."""
    await pi_client.start()

    events = []

    def on_event(event):
        events.append(event)

    result = await pi_client.prompt(
        "What is 2+2? Reply with just the number.", on_event=on_event
    )

    # Should have received events
    assert len(events) > 0

    # Should have agent lifecycle events
    event_types = [e.get("type") for e in events]
    assert "agent_start" in event_types
    assert "agent_end" in event_types

    # Result should contain messages
    assert result is not None
    assert "messages" in result

    # Should have assistant response with "4"
    messages = result["messages"]
    assistant_messages = [m for m in messages if m.get("role") == "assistant"]
    assert len(assistant_messages) > 0

    # Extract text content
    assistant_text = ""
    for msg in assistant_messages:
        for content in msg.get("content", []):
            if content.get("type") == "text":
                assistant_text += content.get("text", "")

    assert "4" in assistant_text


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_pi_prompt_with_thinking(pi_client):
    """Pi should stream thinking deltas for reasoning models."""
    await pi_client.start()

    # Check if model supports thinking
    state = await pi_client.get_state()
    if not state or not state.get("model", {}).get("reasoning"):
        pytest.skip("Model does not support reasoning/thinking")

    thinking_deltas = []
    text_deltas = []

    def on_event(event):
        if event.get("type") == "message_update":
            assistant_event = event.get("assistantMessageEvent", {})
            if assistant_event.get("type") == "thinking_delta":
                thinking_deltas.append(assistant_event.get("delta", ""))
            elif assistant_event.get("type") == "text_delta":
                text_deltas.append(assistant_event.get("delta", ""))

    result = await pi_client.prompt(
        "What is one higher than 4? Reply with just the number.", on_event=on_event
    )

    # Should have received text deltas
    assert len(text_deltas) > 0

    # Final response should contain "5"
    assert result is not None
    messages = result.get("messages", [])
    assistant_messages = [m for m in messages if m.get("role") == "assistant"]

    assistant_text = ""
    for msg in assistant_messages:
        for content in msg.get("content", []):
            if content.get("type") == "text":
                assistant_text += content.get("text", "")

    assert "5" in assistant_text


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_pi_session_directory_created(pi_client, tmp_path):
    """Pi should create session files in the configured directory."""
    session_dir = tmp_path / "pi_sessions"
    assert not session_dir.exists() or not any(session_dir.iterdir())

    await pi_client.start()

    # Get state to confirm session file location
    state = await pi_client.get_state()
    assert state is not None

    session_file = state.get("sessionFile")
    assert session_file is not None
    assert str(session_dir) in session_file

    await pi_client.stop()

    # Session directory should exist with session file
    assert session_dir.exists()


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_pi_get_commands(pi_client):
    """Pi should return available commands."""
    await pi_client.start()

    data = await pi_client.get_commands()

    assert data is not None
    assert "commands" in data
    assert isinstance(data["commands"], list)

    # Each command should have required fields
    for cmd in data["commands"]:
        assert "name" in cmd
        assert "source" in cmd
        # source should be one of: extension, prompt, skill
        assert cmd["source"] in ("extension", "prompt", "skill")


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_pi_get_skills(pi_client):
    """Pi should return skills list (may be empty depending on environment)."""
    await pi_client.start()

    skills = await pi_client.get_skills()

    # Should return a list (may be empty)
    assert isinstance(skills, list)

    # If skills exist, verify structure
    for skill in skills:
        assert "name" in skill
        assert skill.get("source") == "skill"
        # Skill names are prefixed with "skill:"
        assert skill["name"].startswith("skill:")
        # Should have description
        assert "description" in skill
