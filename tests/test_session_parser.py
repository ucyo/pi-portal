"""Tests for session_parser module."""

import json
import tempfile
from pathlib import Path

import pytest

from backend.session_parser import (
    FeedbackEntry,
    ParsedSession,
    SessionHeader,
    get_session_metadata,
    parse_session_file,
)


@pytest.fixture
def simple_session_file():
    """Create a simple session file for testing."""
    entries = [
        {
            "type": "session",
            "version": 3,
            "id": "test-uuid-123",
            "timestamp": "2026-03-04T12:00:00.000Z",
            "cwd": "/workspace/test",
        },
        {
            "type": "model_change",
            "id": "entry1",
            "parentId": None,
            "timestamp": "2026-03-04T12:00:00.001Z",
            "provider": "anthropic",
            "modelId": "claude-sonnet",
        },
        {
            "type": "message",
            "id": "entry2",
            "parentId": "entry1",
            "timestamp": "2026-03-04T12:00:01.000Z",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "Hello, how are you?"}],
                "timestamp": 1772626800000,
            },
        },
        {
            "type": "message",
            "id": "entry3",
            "parentId": "entry2",
            "timestamp": "2026-03-04T12:00:02.000Z",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "User is greeting me"},
                    {"type": "text", "text": "I'm doing great, thanks for asking!"},
                ],
                "timestamp": 1772626801000,
            },
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink()


@pytest.fixture
def session_with_feedback():
    """Create a session file with feedback entries."""
    entries = [
        {
            "type": "session",
            "version": 3,
            "id": "feedback-test-uuid",
            "timestamp": "2026-03-04T12:00:00.000Z",
            "cwd": "/workspace",
        },
        {
            "type": "message",
            "id": "entry1",
            "parentId": None,
            "timestamp": "2026-03-04T12:00:01.000Z",
            "message": {
                "role": "user",
                "content": "What is 2+2?",
                "timestamp": 1772626800000,
            },
        },
        {
            "type": "message",
            "id": "entry2",
            "parentId": "entry1",
            "timestamp": "2026-03-04T12:00:02.000Z",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "4"}],
                "timestamp": 1772626801000,
            },
        },
        {
            "type": "custom",
            "customType": "pi-portal-feedback",
            "id": "entry3",
            "parentId": "entry2",
            "timestamp": "2026-03-04T12:00:03.000Z",
            "data": {
                "targetTimestamp": 1772626801000,
                "rating": 1,
                "comment": None,
                "timestamp": 1772626802000,
            },
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink()


@pytest.fixture
def session_with_name():
    """Create a session file with a session_info name entry."""
    entries = [
        {
            "type": "session",
            "version": 3,
            "id": "named-session-uuid",
            "timestamp": "2026-03-04T12:00:00.000Z",
            "cwd": "/workspace",
        },
        {
            "type": "message",
            "id": "entry1",
            "parentId": None,
            "timestamp": "2026-03-04T12:00:01.000Z",
            "message": {
                "role": "user",
                "content": "Help me refactor the auth module",
                "timestamp": 1772626800000,
            },
        },
        {
            "type": "session_info",
            "id": "entry2",
            "parentId": "entry1",
            "timestamp": "2026-03-04T12:00:02.000Z",
            "name": "Auth Module Refactor",
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink()


class TestParseSessionFile:
    """Tests for parse_session_file function."""

    def test_parse_simple_session(self, simple_session_file):
        """Test parsing a basic session file."""
        session = parse_session_file(simple_session_file)

        assert isinstance(session, ParsedSession)
        assert isinstance(session.header, SessionHeader)
        assert session.header.id == "test-uuid-123"
        assert session.header.cwd == "/workspace/test"
        assert session.header.version == 3

    def test_parse_messages(self, simple_session_file):
        """Test that messages are correctly extracted."""
        session = parse_session_file(simple_session_file)

        assert len(session.messages) == 2
        assert session.messages[0].role == "user"
        assert session.messages[0].content == "Hello, how are you?"
        assert session.messages[1].role == "assistant"
        assert "doing great" in session.messages[1].content

    def test_message_timestamps(self, simple_session_file):
        """Test that message timestamps are extracted."""
        session = parse_session_file(simple_session_file)

        assert session.messages[0].message_timestamp == 1772626800000
        assert session.messages[1].message_timestamp == 1772626801000

    def test_generates_title_from_first_user_message(self, simple_session_file):
        """Test that title is generated from first user message."""
        session = parse_session_file(simple_session_file)

        assert session.title == "Hello, how are you?"

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError):
            parse_session_file(Path("/nonexistent/path.jsonl"))

    def test_empty_file(self, tmp_path):
        """Test that ValueError is raised for empty files."""
        empty_file = tmp_path / "empty.jsonl"
        empty_file.write_text("")

        with pytest.raises(ValueError, match="Empty session file"):
            parse_session_file(empty_file)

    def test_invalid_header(self, tmp_path):
        """Test that ValueError is raised if first entry is not session header."""
        bad_file = tmp_path / "bad.jsonl"
        bad_file.write_text('{"type":"message","id":"123"}\n')

        with pytest.raises(ValueError, match="First entry must be session header"):
            parse_session_file(bad_file)


class TestFeedbackParsing:
    """Tests for feedback extraction."""

    def test_parse_feedback_entries(self, session_with_feedback):
        """Test that feedback entries are correctly extracted."""
        session = parse_session_file(session_with_feedback)

        assert len(session.feedback) == 1
        feedback = session.feedback[0]
        assert isinstance(feedback, FeedbackEntry)
        assert feedback.target_timestamp == 1772626801000
        assert feedback.rating == 1
        assert feedback.comment is None

    def test_feedback_with_comment(self, tmp_path):
        """Test feedback with negative rating and comment."""
        entries = [
            {
                "type": "session",
                "version": 3,
                "id": "test",
                "timestamp": "2026-03-04T12:00:00.000Z",
                "cwd": "/workspace",
            },
            {
                "type": "custom",
                "customType": "pi-portal-feedback",
                "id": "entry1",
                "parentId": None,
                "timestamp": "2026-03-04T12:00:01.000Z",
                "data": {
                    "targetTimestamp": 12345,
                    "rating": -1,
                    "comment": "This answer was incorrect",
                    "timestamp": 12346,
                },
            },
        ]

        session_file = tmp_path / "feedback.jsonl"
        with open(session_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        session = parse_session_file(session_file)

        assert len(session.feedback) == 1
        assert session.feedback[0].rating == -1
        assert session.feedback[0].comment == "This answer was incorrect"


class TestSessionName:
    """Tests for session name handling."""

    def test_session_with_name(self, session_with_name):
        """Test that session name is extracted from session_info."""
        session = parse_session_file(session_with_name)

        assert session.name == "Auth Module Refactor"
        assert session.display_name == "Auth Module Refactor"

    def test_display_name_falls_back_to_title(self, simple_session_file):
        """Test that display_name uses title when name is not set."""
        session = parse_session_file(simple_session_file)

        assert session.name is None
        assert session.display_name == "Hello, how are you?"


class TestGetSessionMetadata:
    """Tests for get_session_metadata function."""

    def test_get_metadata(self, simple_session_file):
        """Test lightweight metadata extraction."""
        metadata = get_session_metadata(simple_session_file)

        assert metadata["id"] == "test-uuid-123"
        assert metadata["cwd"] == "/workspace/test"
        assert metadata["message_count"] == 2
        assert metadata["title"] == "Hello, how are you?"
        assert metadata["display_name"] == "Hello, how are you?"

    def test_metadata_with_session_name(self, session_with_name):
        """Test metadata includes session name."""
        metadata = get_session_metadata(session_with_name)

        assert metadata["name"] == "Auth Module Refactor"
        assert metadata["display_name"] == "Auth Module Refactor"

    def test_metadata_file_not_found(self):
        """Test FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            get_session_metadata(Path("/nonexistent/file.jsonl"))


class TestContentExtraction:
    """Tests for content extraction from different message types."""

    def test_user_string_content(self, tmp_path):
        """Test extracting content from user message with string content."""
        entries = [
            {
                "type": "session",
                "version": 3,
                "id": "test",
                "timestamp": "2026-03-04T12:00:00.000Z",
                "cwd": "/workspace",
            },
            {
                "type": "message",
                "id": "entry1",
                "parentId": None,
                "timestamp": "2026-03-04T12:00:01.000Z",
                "message": {
                    "role": "user",
                    "content": "Simple string content",
                    "timestamp": 12345,
                },
            },
        ]

        session_file = tmp_path / "string_content.jsonl"
        with open(session_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        session = parse_session_file(session_file)
        assert session.messages[0].content == "Simple string content"

    def test_tool_result_content(self, tmp_path):
        """Test extracting content from toolResult message."""
        entries = [
            {
                "type": "session",
                "version": 3,
                "id": "test",
                "timestamp": "2026-03-04T12:00:00.000Z",
                "cwd": "/workspace",
            },
            {
                "type": "message",
                "id": "entry1",
                "parentId": None,
                "timestamp": "2026-03-04T12:00:01.000Z",
                "message": {
                    "role": "toolResult",
                    "toolCallId": "call_123",
                    "toolName": "bash",
                    "content": [{"type": "text", "text": "file1.txt\nfile2.txt"}],
                    "isError": False,
                    "timestamp": 12345,
                },
            },
        ]

        session_file = tmp_path / "tool_result.jsonl"
        with open(session_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        session = parse_session_file(session_file)
        assert session.messages[0].role == "toolResult"
        assert "file1.txt" in session.messages[0].content

    def test_thinking_content_excluded(self, simple_session_file):
        """Test that thinking content is excluded from text extraction."""
        session = parse_session_file(simple_session_file)

        # The assistant message has thinking block that should not appear
        assistant_msg = session.messages[1]
        assert "User is greeting me" not in assistant_msg.content
        assert "doing great" in assistant_msg.content


class TestTitleGeneration:
    """Tests for session title generation."""

    def test_truncate_long_title(self, tmp_path):
        """Test that long titles are truncated."""
        long_message = "This is a very long message that should be truncated because it exceeds the maximum length"
        entries = [
            {
                "type": "session",
                "version": 3,
                "id": "test",
                "timestamp": "2026-03-04T12:00:00.000Z",
                "cwd": "/workspace",
            },
            {
                "type": "message",
                "id": "entry1",
                "parentId": None,
                "timestamp": "2026-03-04T12:00:01.000Z",
                "message": {
                    "role": "user",
                    "content": long_message,
                    "timestamp": 12345,
                },
            },
        ]

        session_file = tmp_path / "long_title.jsonl"
        with open(session_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        session = parse_session_file(session_file)
        assert len(session.title) <= 53  # 50 + "..."
        assert session.title.endswith("...")

    def test_empty_title_for_no_user_messages(self, tmp_path):
        """Test that title is empty when no user messages exist."""
        entries = [
            {
                "type": "session",
                "version": 3,
                "id": "test",
                "timestamp": "2026-03-04T12:00:00.000Z",
                "cwd": "/workspace",
            },
        ]

        session_file = tmp_path / "no_messages.jsonl"
        with open(session_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        session = parse_session_file(session_file)
        assert session.title == ""
        assert session.display_name == "Untitled Session"


class TestRealSessionFiles:
    """Tests using real session files from data/pi_sessions/."""

    def test_parse_real_session(self):
        """Test parsing a real session file if available."""
        sessions_dir = Path("data/pi_sessions")
        if not sessions_dir.exists():
            pytest.skip("No pi_sessions directory found")

        session_files = list(sessions_dir.glob("*.jsonl"))
        if not session_files:
            pytest.skip("No session files found")

        # Parse first available session
        session_file = session_files[0]
        session = parse_session_file(session_file)

        assert session.header.id
        assert session.header.timestamp
        # May or may not have messages depending on session

    def test_get_metadata_real_session(self):
        """Test getting metadata from a real session file."""
        sessions_dir = Path("data/pi_sessions")
        if not sessions_dir.exists():
            pytest.skip("No pi_sessions directory found")

        session_files = list(sessions_dir.glob("*.jsonl"))
        if not session_files:
            pytest.skip("No session files found")

        # Get metadata for first available session
        session_file = session_files[0]
        metadata = get_session_metadata(session_file)

        assert "id" in metadata
        assert "timestamp" in metadata
        assert "message_count" in metadata
        assert "file_path" in metadata
