"""Integration tests for configuration with actual Pi client usage."""

import pytest

from backend.config import Config
from backend.pi_client import PiClient


@pytest.mark.integration
async def test_custom_session_directory_creates_sessions(tmp_path, monkeypatch):
    """Pi client should create sessions in configured directory."""
    custom_dir = tmp_path / "custom_sessions"
    monkeypatch.setenv("PI_PORTAL_PI_SESSION_DIR", str(custom_dir))

    # Create new config with custom session dir
    config = Config()
    session_dir = config.get_absolute_session_dir()

    # Verify the custom directory was created
    assert session_dir == custom_dir
    assert session_dir.exists()

    # Create Pi client with custom session directory
    pi_client = PiClient(session_dir=session_dir)

    # Start Pi (this should initialize with the custom session dir)
    await pi_client.start()

    try:
        # Send a test prompt to create a session
        events = []

        def on_event(event):
            events.append(event)

        await pi_client.prompt("Say hello", on_event=on_event)

        # Give it a moment to write the session
        import asyncio

        await asyncio.sleep(0.5)

        # Check if session files were created in custom directory
        session_files = list(custom_dir.glob("*.jsonl"))
        assert len(session_files) > 0, f"No session files found in {custom_dir}"

        # Verify the session file is in the correct location
        for session_file in session_files:
            assert session_file.parent == custom_dir
            # Verify the file has content
            assert session_file.stat().st_size > 0

    finally:
        await pi_client.stop()


def test_relative_path_resolution(tmp_path, monkeypatch):
    """Relative session paths should resolve correctly from project root."""
    # Set a relative path
    monkeypatch.setenv("PI_PORTAL_PI_SESSION_DIR", "my_custom_sessions")

    config = Config()
    session_dir = config.get_absolute_session_dir()

    # Should be absolute and end with our custom directory name
    assert session_dir.is_absolute()
    assert session_dir.name == "my_custom_sessions"
    assert session_dir.exists()


def test_absolute_path_used_directly(tmp_path, monkeypatch):
    """Absolute session paths should be used as-is."""
    custom_dir = tmp_path / "absolute_sessions"
    monkeypatch.setenv("PI_PORTAL_PI_SESSION_DIR", str(custom_dir))

    config = Config()
    session_dir = config.get_absolute_session_dir()

    # Should match exactly
    assert session_dir == custom_dir
    assert session_dir.exists()


async def test_pi_client_uses_config_session_dir(tmp_path, monkeypatch):
    """Default Pi client should use config's session directory."""
    custom_dir = tmp_path / "from_config"
    monkeypatch.setenv("PI_PORTAL_PI_SESSION_DIR", str(custom_dir))

    # Import after setting env var to pick up new config
    from importlib import reload
    from backend import config as config_module
    from backend import pi_client as pi_client_module

    reload(config_module)
    reload(pi_client_module)

    # Get the default client (should use config)
    from backend.pi_client import get_pi_client

    client = get_pi_client()

    # Verify it's using the custom directory
    assert client.session_dir == custom_dir
