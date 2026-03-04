"""Tests for the sessions API endpoint."""

import json
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
async def client():
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def mock_sessions_dir(tmp_path):
    """Create a temporary sessions directory with test session files."""
    sessions_dir = tmp_path / "pi_sessions"
    sessions_dir.mkdir()

    # Create test session files
    session1_entries = [
        {
            "type": "session",
            "version": 3,
            "id": "session-1-uuid",
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
                "content": "Hello, first session",
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
                "content": [{"type": "text", "text": "Hi there!"}],
                "timestamp": 1772626801000,
            },
        },
    ]

    session2_entries = [
        {
            "type": "session",
            "version": 3,
            "id": "session-2-uuid",
            "timestamp": "2026-03-04T14:00:00.000Z",  # Later than session 1
            "cwd": "/workspace",
        },
        {
            "type": "message",
            "id": "entry1",
            "parentId": None,
            "timestamp": "2026-03-04T14:00:01.000Z",
            "message": {
                "role": "user",
                "content": "Second session here",
                "timestamp": 1772634000000,
            },
        },
    ]

    # Write session files
    session1_file = sessions_dir / "2026-03-04T12-00-00-000Z_session-1-uuid.jsonl"
    with open(session1_file, "w") as f:
        for entry in session1_entries:
            f.write(json.dumps(entry) + "\n")

    session2_file = sessions_dir / "2026-03-04T14-00-00-000Z_session-2-uuid.jsonl"
    with open(session2_file, "w") as f:
        for entry in session2_entries:
            f.write(json.dumps(entry) + "\n")

    return sessions_dir


class TestListSessions:
    """Tests for GET /api/sessions endpoint."""

    @pytest.mark.asyncio
    async def test_list_sessions_returns_sessions(self, client, mock_sessions_dir):
        """Test that sessions are returned."""
        with patch("backend.main.SESSIONS_PATH", mock_sessions_dir):
            response = await client.get("/api/sessions")

        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert len(data["sessions"]) == 2

    @pytest.mark.asyncio
    async def test_sessions_ordered_by_most_recent(self, client, mock_sessions_dir):
        """Test that sessions are ordered most recent first."""
        with patch("backend.main.SESSIONS_PATH", mock_sessions_dir):
            response = await client.get("/api/sessions")

        data = response.json()
        sessions = data["sessions"]

        # Session 2 (14:00) should come before Session 1 (12:00)
        assert sessions[0]["id"] == "session-2-uuid"
        assert sessions[1]["id"] == "session-1-uuid"

    @pytest.mark.asyncio
    async def test_session_metadata_fields(self, client, mock_sessions_dir):
        """Test that sessions include required metadata fields."""
        with patch("backend.main.SESSIONS_PATH", mock_sessions_dir):
            response = await client.get("/api/sessions")

        data = response.json()
        session = data["sessions"][0]

        assert "id" in session
        assert "timestamp" in session
        assert "cwd" in session
        assert "display_name" in session
        assert "message_count" in session
        assert "file_path" in session

    @pytest.mark.asyncio
    async def test_session_message_count(self, client, mock_sessions_dir):
        """Test that message count is correct."""
        with patch("backend.main.SESSIONS_PATH", mock_sessions_dir):
            response = await client.get("/api/sessions")

        data = response.json()
        sessions = data["sessions"]

        # Find sessions by ID
        session1 = next(s for s in sessions if s["id"] == "session-1-uuid")
        session2 = next(s for s in sessions if s["id"] == "session-2-uuid")

        assert session1["message_count"] == 2  # user + assistant
        assert session2["message_count"] == 1  # user only

    @pytest.mark.asyncio
    async def test_session_display_name_from_first_message(
        self, client, mock_sessions_dir
    ):
        """Test that display name is generated from first user message."""
        with patch("backend.main.SESSIONS_PATH", mock_sessions_dir):
            response = await client.get("/api/sessions")

        data = response.json()
        sessions = data["sessions"]

        session1 = next(s for s in sessions if s["id"] == "session-1-uuid")
        session2 = next(s for s in sessions if s["id"] == "session-2-uuid")

        assert session1["display_name"] == "Hello, first session"
        assert session2["display_name"] == "Second session here"

    @pytest.mark.asyncio
    async def test_empty_sessions_directory(self, client, tmp_path):
        """Test response when sessions directory is empty."""
        empty_dir = tmp_path / "empty_sessions"
        empty_dir.mkdir()

        with patch("backend.main.SESSIONS_PATH", empty_dir):
            response = await client.get("/api/sessions")

        assert response.status_code == 200
        data = response.json()
        assert data["sessions"] == []

    @pytest.mark.asyncio
    async def test_nonexistent_sessions_directory(self, client, tmp_path):
        """Test response when sessions directory doesn't exist."""
        nonexistent = tmp_path / "nonexistent"

        with patch("backend.main.SESSIONS_PATH", nonexistent):
            response = await client.get("/api/sessions")

        assert response.status_code == 200
        data = response.json()
        assert data["sessions"] == []

    @pytest.mark.asyncio
    async def test_invalid_session_file_skipped(self, client, tmp_path):
        """Test that invalid session files are skipped gracefully."""
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()

        # Create a valid session
        valid_session = [
            {
                "type": "session",
                "version": 3,
                "id": "valid-uuid",
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
                    "content": "Valid session",
                    "timestamp": 123,
                },
            },
        ]

        valid_file = sessions_dir / "valid.jsonl"
        with open(valid_file, "w") as f:
            for entry in valid_session:
                f.write(json.dumps(entry) + "\n")

        # Create an invalid session file
        invalid_file = sessions_dir / "invalid.jsonl"
        invalid_file.write_text("not valid json\n")

        with patch("backend.main.SESSIONS_PATH", sessions_dir):
            response = await client.get("/api/sessions")

        assert response.status_code == 200
        data = response.json()
        # Only the valid session should be returned
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["id"] == "valid-uuid"


class TestListSessionsWithRealData:
    """Tests using real session files if available."""

    @pytest.mark.asyncio
    async def test_list_real_sessions(self, client):
        """Test listing real sessions from data/pi_sessions/."""
        response = await client.get("/api/sessions")

        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data

        # If we have real sessions, verify structure
        if data["sessions"]:
            session = data["sessions"][0]
            assert "id" in session
            assert "timestamp" in session
            assert "display_name" in session
            assert "message_count" in session
