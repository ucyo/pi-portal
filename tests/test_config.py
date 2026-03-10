"""Tests for configuration module."""

from pathlib import Path

import pytest

from backend.config import Config


def test_config_defaults():
    """Configuration should have sensible defaults."""
    config = Config()

    assert config.pi_executable == "pi"
    assert config.pi_session_dir == Path("data/pi_sessions")
    assert config.server_host == "0.0.0.0"
    assert config.server_port == 8000
    assert config.server_reload is False


def test_config_from_environment(monkeypatch):
    """Configuration should load from environment variables with PI_PORTAL_ prefix."""
    monkeypatch.setenv("PI_PORTAL_PI_EXECUTABLE", "/usr/local/bin/pi")
    monkeypatch.setenv("PI_PORTAL_PI_SESSION_DIR", "/tmp/sessions")
    monkeypatch.setenv("PI_PORTAL_SERVER_HOST", "127.0.0.1")
    monkeypatch.setenv("PI_PORTAL_SERVER_PORT", "3000")
    monkeypatch.setenv("PI_PORTAL_SERVER_RELOAD", "true")

    # Create a new config instance to pick up env vars
    config = Config()

    assert config.pi_executable == "/usr/local/bin/pi"
    assert config.pi_session_dir == Path("/tmp/sessions")
    assert config.server_host == "127.0.0.1"
    assert config.server_port == 3000
    assert config.server_reload is True


def test_config_case_insensitive(monkeypatch):
    """Environment variables should be case-insensitive."""
    monkeypatch.setenv("pi_portal_server_port", "9000")

    config = Config()

    assert config.server_port == 9000


def test_get_absolute_session_dir_relative(tmp_path, monkeypatch):
    """Relative session dir should be resolved relative to project root."""
    monkeypatch.setenv("PI_PORTAL_PI_SESSION_DIR", "data/custom_sessions")

    config = Config()

    session_dir = config.get_absolute_session_dir()
    assert session_dir.is_absolute()
    assert session_dir.name == "custom_sessions"


def test_get_absolute_session_dir_absolute(tmp_path, monkeypatch):
    """Absolute session dir should be used as-is."""
    abs_path = tmp_path / "sessions"
    monkeypatch.setenv("PI_PORTAL_PI_SESSION_DIR", str(abs_path))

    config = Config()

    session_dir = config.get_absolute_session_dir()
    assert session_dir == abs_path
    assert session_dir.exists()  # Should be created


def test_get_absolute_session_dir_creates_directory(tmp_path, monkeypatch):
    """Session directory should be created if it doesn't exist."""
    new_dir = tmp_path / "new_sessions"
    monkeypatch.setenv("PI_PORTAL_PI_SESSION_DIR", str(new_dir))

    config = Config()

    assert not new_dir.exists()
    session_dir = config.get_absolute_session_dir()
    assert session_dir.exists()
    assert session_dir.is_dir()


def test_config_paths_exist():
    """Static configuration paths should be set correctly."""
    config = Config()

    assert config.config_path.exists()
    assert config.frontend_path.exists()
    assert (config.config_path / "starter_prompts.json").exists()


def test_config_loads_from_env_file(tmp_path, monkeypatch):
    """Configuration should load from .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "PI_PORTAL_SERVER_PORT=5000\nPI_PORTAL_PI_EXECUTABLE=/custom/pi\n"
    )

    # Change to temp directory so .env is found
    monkeypatch.chdir(tmp_path)

    config = Config()

    assert config.server_port == 5000
    assert config.pi_executable == "/custom/pi"


def test_pydantic_validation():
    """Pydantic should validate field types."""
    from pydantic import ValidationError

    # Invalid port (not an integer)
    with pytest.raises(ValidationError):
        Config(server_port="not-a-number")  # type: ignore
