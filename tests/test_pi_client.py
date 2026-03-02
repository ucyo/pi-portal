"""Tests for Pi RPC client."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.pi_client import PiClient, get_pi_client


def test_pi_client_initialization():
    """PiClient should initialize with default values."""
    client = PiClient()
    assert client.session_dir == Path("data/pi_sessions")
    assert client.pi_executable == "pi"
    assert not client.is_running


def test_pi_client_custom_session_dir():
    """PiClient should accept custom session directory."""
    custom_dir = Path("/tmp/custom_sessions")
    client = PiClient(session_dir=custom_dir)
    assert client.session_dir == custom_dir


def test_pi_client_custom_executable():
    """PiClient should accept custom Pi executable path."""
    client = PiClient(pi_executable="/usr/local/bin/pi")
    assert client.pi_executable == "/usr/local/bin/pi"


def test_get_pi_client_returns_singleton():
    """get_pi_client should return the same instance."""
    client1 = get_pi_client()
    client2 = get_pi_client()
    assert client1 is client2


async def test_is_running_false_when_not_started():
    """is_running should be False when process not started."""
    client = PiClient()
    assert not client.is_running


async def test_stop_when_not_running():
    """stop() should handle case when process not running."""
    client = PiClient()
    # Should not raise
    await client.stop()


async def test_send_command_raises_when_not_running():
    """send_command should raise RuntimeError when not running."""
    client = PiClient()
    with pytest.raises(RuntimeError, match="not running"):
        await client.send_command({"type": "prompt", "message": "test"})


async def test_start_creates_session_directory(tmp_path):
    """start() should create session directory if it doesn't exist."""
    session_dir = tmp_path / "sessions"
    client = PiClient(session_dir=session_dir)

    # Mock the subprocess creation to avoid actually starting Pi
    mock_process = MagicMock()
    mock_process.returncode = None
    mock_process.pid = 12345

    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_process
        await client.start()

    assert session_dir.exists()


async def test_start_builds_correct_command(tmp_path):
    """start() should build correct Pi command with arguments."""
    session_dir = tmp_path / "sessions"
    client = PiClient(session_dir=session_dir, pi_executable="/custom/pi")

    mock_process = MagicMock()
    mock_process.returncode = None
    mock_process.pid = 12345

    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_process
        await client.start()

        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert call_args[0] == "/custom/pi"
        assert "--mode" in call_args
        assert "rpc" in call_args
        assert "--session-dir" in call_args
        assert str(session_dir) in call_args
