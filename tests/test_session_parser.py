"""Tests for Pi session JSONL parser.

These tests verify the session_parser module can correctly parse Pi's JSONL session files.
They use fixture data and don't require Pi to be running.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

import pytest


# Sample session data for testing
SAMPLE_SESSION_HEADER = {
    "type": "session",
    "version": 3,
    "id": "test-session-uuid",
    "timestamp": "2024-12-03T14:00:00.000Z",
    "cwd": "/workspace"
}

SAMPLE_MODEL_CHANGE = {
    "type": "model_change",
    "id": "5bb16c4c",
    "parentId": None,
    "timestamp": "2024-12-03T14:00:00.000Z",
    "provider": "anthropic",
    "modelId": "claude-sonnet-4-20250514"
}

SAMPLE_USER_MESSAGE = {
    "type": "message",
    "id": "52fde5da",
    "parentId": "5bb16c4c",
    "timestamp": "2024-12-03T14:00:01.000Z",
    "message": {
        "role": "user",
        "content": [{"type": "text", "text": "Hello, how are you?"}],
        "timestamp": 1733234401000
    }
}

SAMPLE_ASSISTANT_MESSAGE = {
    "type": "message",
    "id": "a225ab91",
    "parentId": "52fde5da",
    "timestamp": "2024-12-03T14:00:02.000Z",
    "message": {
        "role": "assistant",
        "content": [
            {"type": "thinking", "thinking": "User is greeting me."},
            {"type": "text", "text": "Hello! I'm doing well, thank you for asking."}
        ],
        "api": "anthropic-messages",
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "usage": {
            "input": 100,
            "output": 50,
            "cacheRead": 0,
            "cacheWrite": 0,
            "totalTokens": 150,
            "cost": {"input": 0.001, "output": 0.002, "total": 0.003}
        },
        "stopReason": "stop",
        "timestamp": 1733234402000
    }
}

SAMPLE_FEEDBACK_ENTRY = {
    "type": "custom",
    "id": "f1e2d3c4",
    "parentId": "a225ab91",
    "timestamp": "2024-12-03T14:01:00.000Z",
    "customType": "pi-portal-feedback",
    "data": {
        "targetTimestamp": 1733234402000,
        "rating": 1,
        "comment": None,
        "timestamp": 1733234460000
    }
}

SAMPLE_SESSION_INFO = {
    "type": "session_info",
    "id": "info1234",
    "parentId": "f1e2d3c4",
    "timestamp": "2024-12-03T14:02:00.000Z",
    "name": "Test Conversation"
}


@pytest.fixture
def sample_session_file(tmp_path) -> Path:
    """Create a sample session JSONL file for testing."""
    session_file = tmp_path / "test_session.jsonl"
    
    entries = [
        SAMPLE_SESSION_HEADER,
        SAMPLE_MODEL_CHANGE,
        SAMPLE_USER_MESSAGE,
        SAMPLE_ASSISTANT_MESSAGE,
        SAMPLE_FEEDBACK_ENTRY,
        SAMPLE_SESSION_INFO,
    ]
    
    with open(session_file, 'w') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')
    
    return session_file


@pytest.fixture
def empty_session_file(tmp_path) -> Path:
    """Create an empty session file with just header."""
    session_file = tmp_path / "empty_session.jsonl"
    
    with open(session_file, 'w') as f:
        f.write(json.dumps(SAMPLE_SESSION_HEADER) + '\n')
    
    return session_file


@pytest.fixture
def session_without_name(tmp_path) -> Path:
    """Create a session without session_info (no custom name)."""
    session_file = tmp_path / "no_name_session.jsonl"
    
    entries = [
        SAMPLE_SESSION_HEADER,
        SAMPLE_MODEL_CHANGE,
        SAMPLE_USER_MESSAGE,
        SAMPLE_ASSISTANT_MESSAGE,
    ]
    
    with open(session_file, 'w') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')
    
    return session_file


@pytest.fixture
def sessions_directory(tmp_path) -> Path:
    """Create a directory with multiple session files."""
    sessions_dir = tmp_path / "sessions" / "--workspace--"
    sessions_dir.mkdir(parents=True)
    
    # Create multiple session files
    for i in range(3):
        session_file = sessions_dir / f"2024-12-0{i+1}T14-00-00-000Z_session-{i}.jsonl"
        
        header = {
            **SAMPLE_SESSION_HEADER,
            "id": f"session-{i}",
            "timestamp": f"2024-12-0{i+1}T14:00:00.000Z"
        }
        
        user_msg = {
            **SAMPLE_USER_MESSAGE,
            "message": {
                **SAMPLE_USER_MESSAGE["message"],
                "content": [{"type": "text", "text": f"Message {i}"}]
            }
        }
        
        with open(session_file, 'w') as f:
            f.write(json.dumps(header) + '\n')
            f.write(json.dumps(SAMPLE_MODEL_CHANGE) + '\n')
            f.write(json.dumps(user_msg) + '\n')
    
    return sessions_dir.parent


class TestSessionParserModule:
    """Test that the session_parser module exists and has required functions.
    
    Note: These tests will fail until M2.1 is implemented.
    """
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_module_exists(self):
        """Session parser module should exist."""
        from backend import session_parser
        assert session_parser is not None
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_has_parse_session_function(self):
        """Module should have parse_session function."""
        from backend.session_parser import parse_session
        assert callable(parse_session)
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_has_list_sessions_function(self):
        """Module should have list_sessions function."""
        from backend.session_parser import list_sessions
        assert callable(list_sessions)
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_has_get_session_messages_function(self):
        """Module should have get_session_messages function."""
        from backend.session_parser import get_session_messages
        assert callable(get_session_messages)
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_has_get_session_feedback_function(self):
        """Module should have get_session_feedback function."""
        from backend.session_parser import get_session_feedback
        assert callable(get_session_feedback)


class TestParseSessionHeader:
    """Test parsing session headers."""
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_parse_session_header(self, sample_session_file):
        """Should extract session header information."""
        from backend.session_parser import parse_session
        
        session = parse_session(sample_session_file)
        
        assert session["id"] == "test-session-uuid"
        assert session["cwd"] == "/workspace"
        assert session["version"] == 3
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_parse_session_timestamp(self, sample_session_file):
        """Should parse session timestamp correctly."""
        from backend.session_parser import parse_session
        
        session = parse_session(sample_session_file)
        
        assert "timestamp" in session
        # Should be parseable as datetime
        assert isinstance(session["timestamp"], (str, datetime))


class TestParseSessionMessages:
    """Test parsing messages from sessions."""
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_parse_messages(self, sample_session_file):
        """Should extract all messages from session."""
        from backend.session_parser import get_session_messages
        
        messages = get_session_messages(sample_session_file)
        
        assert len(messages) == 2  # 1 user + 1 assistant
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_parse_user_message(self, sample_session_file):
        """Should correctly parse user messages."""
        from backend.session_parser import get_session_messages
        
        messages = get_session_messages(sample_session_file)
        user_messages = [m for m in messages if m["role"] == "user"]
        
        assert len(user_messages) == 1
        assert user_messages[0]["content"] == "Hello, how are you?"
        assert user_messages[0]["timestamp"] == 1733234401000
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_parse_assistant_message(self, sample_session_file):
        """Should correctly parse assistant messages."""
        from backend.session_parser import get_session_messages
        
        messages = get_session_messages(sample_session_file)
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        
        assert len(assistant_messages) == 1
        assert "Hello!" in assistant_messages[0]["content"]
        assert assistant_messages[0]["timestamp"] == 1733234402000
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_parse_assistant_message_extracts_text_only(self, sample_session_file):
        """Should extract only text content, not thinking blocks."""
        from backend.session_parser import get_session_messages
        
        messages = get_session_messages(sample_session_file)
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        
        # Should not include thinking content in main content
        assert "User is greeting me" not in assistant_messages[0]["content"]
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_empty_session_returns_empty_list(self, empty_session_file):
        """Session with no messages should return empty list."""
        from backend.session_parser import get_session_messages
        
        messages = get_session_messages(empty_session_file)
        
        assert messages == []


class TestParseSessionFeedback:
    """Test parsing feedback from sessions."""
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_parse_feedback(self, sample_session_file):
        """Should extract feedback entries from session."""
        from backend.session_parser import get_session_feedback
        
        feedback = get_session_feedback(sample_session_file)
        
        assert len(feedback) == 1
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_feedback_has_required_fields(self, sample_session_file):
        """Feedback should have targetTimestamp, rating, comment."""
        from backend.session_parser import get_session_feedback
        
        feedback = get_session_feedback(sample_session_file)
        
        assert feedback[0]["targetTimestamp"] == 1733234402000
        assert feedback[0]["rating"] == 1
        assert feedback[0]["comment"] is None
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_session_without_feedback(self, session_without_name):
        """Session without feedback should return empty list."""
        from backend.session_parser import get_session_feedback
        
        feedback = get_session_feedback(session_without_name)
        
        assert feedback == []


class TestParseSessionName:
    """Test parsing session names."""
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_parse_session_name_from_session_info(self, sample_session_file):
        """Should extract session name from session_info entry."""
        from backend.session_parser import parse_session
        
        session = parse_session(sample_session_file)
        
        assert session["name"] == "Test Conversation"
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_generate_title_from_first_message(self, session_without_name):
        """Should generate title from first user message if no name."""
        from backend.session_parser import parse_session
        
        session = parse_session(session_without_name)
        
        # Should use first user message as title (truncated)
        assert "Hello" in session["title"]
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_empty_session_has_default_title(self, empty_session_file):
        """Empty session should have a default title."""
        from backend.session_parser import parse_session
        
        session = parse_session(empty_session_file)
        
        assert session["title"] is not None
        assert len(session["title"]) > 0


class TestListSessions:
    """Test listing sessions from directory."""
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_list_sessions(self, sessions_directory):
        """Should list all sessions in directory."""
        from backend.session_parser import list_sessions
        
        sessions = list_sessions(sessions_directory)
        
        assert len(sessions) == 3
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_list_sessions_ordered_by_date(self, sessions_directory):
        """Sessions should be ordered by most recent first."""
        from backend.session_parser import list_sessions
        
        sessions = list_sessions(sessions_directory)
        
        # Most recent should be first (session-2)
        assert sessions[0]["id"] == "session-2"
        assert sessions[-1]["id"] == "session-0"
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_list_sessions_includes_metadata(self, sessions_directory):
        """Listed sessions should include basic metadata."""
        from backend.session_parser import list_sessions
        
        sessions = list_sessions(sessions_directory)
        
        for session in sessions:
            assert "id" in session
            assert "timestamp" in session
            assert "title" in session
            assert "message_count" in session
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_empty_directory(self, tmp_path):
        """Empty directory should return empty list."""
        from backend.session_parser import list_sessions
        
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        sessions = list_sessions(empty_dir)
        
        assert sessions == []
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_nonexistent_directory(self, tmp_path):
        """Nonexistent directory should return empty list."""
        from backend.session_parser import list_sessions
        
        nonexistent = tmp_path / "nonexistent"
        
        sessions = list_sessions(nonexistent)
        
        assert sessions == []


class TestMatchFeedbackToMessages:
    """Test matching feedback entries to messages by timestamp."""
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_match_feedback_to_message(self, sample_session_file):
        """Should be able to match feedback to correct message."""
        from backend.session_parser import (
            get_session_messages,
            get_session_feedback,
            match_feedback_to_messages
        )
        
        messages = get_session_messages(sample_session_file)
        feedback = get_session_feedback(sample_session_file)
        
        matched = match_feedback_to_messages(messages, feedback)
        
        # The assistant message should have feedback
        assistant_msg = [m for m in matched if m["role"] == "assistant"][0]
        assert assistant_msg["feedback"]["rating"] == 1
    
    @pytest.mark.skip(reason="M2.1 not yet implemented")
    def test_message_without_feedback(self, sample_session_file):
        """Messages without feedback should have None or empty feedback."""
        from backend.session_parser import (
            get_session_messages,
            get_session_feedback,
            match_feedback_to_messages
        )
        
        messages = get_session_messages(sample_session_file)
        feedback = get_session_feedback(sample_session_file)
        
        matched = match_feedback_to_messages(messages, feedback)
        
        # User message should not have feedback
        user_msg = [m for m in matched if m["role"] == "user"][0]
        assert user_msg.get("feedback") is None or user_msg["feedback"]["rating"] == 0
