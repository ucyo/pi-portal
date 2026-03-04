"""Tests for Pi feedback extension.

These tests verify the feedback extension (.pi/extensions/feedback.ts) works correctly.
They are marked with @pytest.mark.integration and require Pi to be installed.
"""

import json
import shutil
from pathlib import Path

import pytest

from backend.pi_client import PiClient

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
    if client.is_running:
        await client.stop()


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_feedback_command_exists(pi_client):
    """The /feedback command should be registered by the extension."""
    await pi_client.start()

    data = await pi_client.get_commands()
    commands = data.get("commands", [])
    command_names = [cmd["name"] for cmd in commands]

    assert "feedback" in command_names, "feedback command not found"


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_feedback_list_command_exists(pi_client):
    """The /feedback-list command should be registered by the extension."""
    await pi_client.start()

    data = await pi_client.get_commands()
    commands = data.get("commands", [])
    command_names = [cmd["name"] for cmd in commands]

    assert "feedback-list" in command_names, "feedback-list command not found"


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_feedback_positive_rating(pi_client):
    """Positive feedback should be saved successfully."""
    await pi_client.start()

    events = []

    def on_event(event):
        events.append(event)

    # Submit positive feedback
    feedback_data = json.dumps({"targetTimestamp": 1234567890, "rating": 1})
    await pi_client.prompt(f"/feedback {feedback_data}", on_event=on_event)

    # Should receive a notify event confirming save
    notify_events = [
        e
        for e in events
        if e.get("type") == "extension_ui_request" and e.get("method") == "notify"
    ]
    assert len(notify_events) > 0

    # Check the notification message
    notify = notify_events[0]
    assert "Feedback saved" in notify.get("message", "")
    assert "👍" in notify.get("message", "")


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_feedback_negative_rating_with_comment(pi_client):
    """Negative feedback with comment should be saved successfully."""
    await pi_client.start()

    events = []

    def on_event(event):
        events.append(event)

    # Submit negative feedback with comment
    feedback_data = json.dumps(
        {
            "targetTimestamp": 1234567890,
            "rating": -1,
            "comment": "This response was incorrect",
        }
    )
    await pi_client.prompt(f"/feedback {feedback_data}", on_event=on_event)

    # Should receive a notify event confirming save
    notify_events = [
        e
        for e in events
        if e.get("type") == "extension_ui_request" and e.get("method") == "notify"
    ]
    assert len(notify_events) > 0

    # Check the notification message
    notify = notify_events[0]
    assert "Feedback saved" in notify.get("message", "")
    assert "👎" in notify.get("message", "")


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_feedback_clear_rating(pi_client):
    """Rating of 0 should clear feedback."""
    await pi_client.start()

    events = []

    def on_event(event):
        events.append(event)

    # Submit cleared feedback
    feedback_data = json.dumps({"targetTimestamp": 1234567890, "rating": 0})
    await pi_client.prompt(f"/feedback {feedback_data}", on_event=on_event)

    # Should receive a notify event
    notify_events = [
        e
        for e in events
        if e.get("type") == "extension_ui_request" and e.get("method") == "notify"
    ]
    assert len(notify_events) > 0

    notify = notify_events[0]
    assert "cleared" in notify.get("message", "")


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_feedback_invalid_json_error(pi_client):
    """Invalid JSON should return an error notification."""
    await pi_client.start()

    events = []

    def on_event(event):
        events.append(event)

    # Submit invalid JSON
    await pi_client.prompt("/feedback not-valid-json", on_event=on_event)

    # Should receive an error notification
    notify_events = [
        e
        for e in events
        if e.get("type") == "extension_ui_request" and e.get("method") == "notify"
    ]
    assert len(notify_events) > 0

    notify = notify_events[0]
    assert notify.get("notifyType") == "error"


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_feedback_missing_timestamp_error(pi_client):
    """Missing targetTimestamp should return an error."""
    await pi_client.start()

    events = []

    def on_event(event):
        events.append(event)

    # Submit feedback without targetTimestamp
    feedback_data = json.dumps({"rating": 1})
    await pi_client.prompt(f"/feedback {feedback_data}", on_event=on_event)

    # Should receive an error notification
    notify_events = [
        e
        for e in events
        if e.get("type") == "extension_ui_request" and e.get("method") == "notify"
    ]
    assert len(notify_events) > 0

    notify = notify_events[0]
    assert notify.get("notifyType") == "error"
    assert "targetTimestamp" in notify.get("message", "")


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_feedback_invalid_rating_error(pi_client):
    """Invalid rating value should return an error."""
    await pi_client.start()

    events = []

    def on_event(event):
        events.append(event)

    # Submit feedback with invalid rating
    feedback_data = json.dumps(
        {
            "targetTimestamp": 1234567890,
            "rating": 5,  # Invalid: must be -1, 0, or 1
        }
    )
    await pi_client.prompt(f"/feedback {feedback_data}", on_event=on_event)

    # Should receive an error notification
    notify_events = [
        e
        for e in events
        if e.get("type") == "extension_ui_request" and e.get("method") == "notify"
    ]
    assert len(notify_events) > 0

    notify = notify_events[0]
    assert notify.get("notifyType") == "error"


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_feedback_list_empty_session(pi_client):
    """Feedback list on new session should show no feedback."""
    await pi_client.start()

    events = []

    def on_event(event):
        events.append(event)

    await pi_client.prompt("/feedback-list", on_event=on_event)

    # Should receive a notification
    notify_events = [
        e
        for e in events
        if e.get("type") == "extension_ui_request" and e.get("method") == "notify"
    ]
    assert len(notify_events) > 0

    notify = notify_events[0]
    assert "No feedback" in notify.get("message", "")


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_feedback_persists_in_session(pi_client, tmp_path):
    """Feedback should be persisted in the session JSONL file."""
    await pi_client.start()

    # Get session file path
    state = await pi_client.get_state()
    session_file = state.get("sessionFile")
    assert session_file is not None

    # Submit feedback
    target_ts = 9876543210
    feedback_data = json.dumps({"targetTimestamp": target_ts, "rating": 1})
    await pi_client.prompt(f"/feedback {feedback_data}")

    # Stop to ensure file is flushed
    await pi_client.stop()

    # Read session file and find feedback entry
    session_path = Path(session_file)
    assert session_path.exists()

    content = session_path.read_text()
    lines = content.strip().split("\n")

    feedback_entries = []
    for line in lines:
        entry = json.loads(line)
        if (
            entry.get("type") == "custom"
            and entry.get("customType") == "pi-portal-feedback"
        ):
            feedback_entries.append(entry)

    assert len(feedback_entries) > 0

    # Check the feedback data
    feedback = feedback_entries[0]
    assert feedback["data"]["targetTimestamp"] == target_ts
    assert feedback["data"]["rating"] == 1


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_feedback_list_shows_saved_feedback(pi_client):
    """Feedback list should show previously saved feedback."""
    await pi_client.start()

    # Submit some feedback
    for i, (rating, icon) in enumerate([(1, "👍"), (-1, "👎")]):
        feedback_data = json.dumps(
            {
                "targetTimestamp": 1000000000 + i,
                "rating": rating,
                "comment": "test comment" if rating == -1 else None,
            }
        )
        await pi_client.prompt(f"/feedback {feedback_data}")

    # Now list feedback
    events = []

    def on_event(event):
        events.append(event)

    await pi_client.prompt("/feedback-list", on_event=on_event)

    # Should receive a notification with feedback entries
    notify_events = [
        e
        for e in events
        if e.get("type") == "extension_ui_request" and e.get("method") == "notify"
    ]
    assert len(notify_events) > 0

    notify = notify_events[0]
    message = notify.get("message", "")

    assert "2 feedback entries" in message
    assert "👍" in message
    assert "👎" in message


@pytest.mark.skipif(not pi_available(), reason="Pi not installed")
async def test_negative_feedback_clears_comment_on_positive(pi_client, tmp_path):
    """Changing from negative to positive should clear the comment."""
    await pi_client.start()

    target_ts = 5555555555

    # First submit negative feedback with comment
    feedback_data = json.dumps(
        {"targetTimestamp": target_ts, "rating": -1, "comment": "This is a complaint"}
    )
    await pi_client.prompt(f"/feedback {feedback_data}")

    # Then change to positive (comment should be cleared)
    feedback_data = json.dumps(
        {
            "targetTimestamp": target_ts,
            "rating": 1,
            "comment": "This should be ignored",  # Should be cleared
        }
    )
    await pi_client.prompt(f"/feedback {feedback_data}")

    # Get session file and check
    state = await pi_client.get_state()
    await pi_client.stop()

    session_path = Path(state.get("sessionFile"))
    content = session_path.read_text()
    lines = content.strip().split("\n")

    # Find the last feedback entry for this timestamp
    feedback_entries = []
    for line in lines:
        entry = json.loads(line)
        if (
            entry.get("type") == "custom"
            and entry.get("customType") == "pi-portal-feedback"
            and entry.get("data", {}).get("targetTimestamp") == target_ts
        ):
            feedback_entries.append(entry)

    # Should have 2 entries
    assert len(feedback_entries) == 2

    # Last entry should have rating=1 and no comment
    last_feedback = feedback_entries[-1]
    assert last_feedback["data"]["rating"] == 1
    assert last_feedback["data"]["comment"] is None
