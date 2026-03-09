"""Tests for Procfile configuration."""

from pathlib import Path


def test_procfile_exists():
    """Procfile should exist in project root."""
    procfile = Path(__file__).parent.parent / "Procfile"
    assert procfile.exists(), "Procfile not found"


def test_procfile_has_required_services():
    """Procfile should define web and pi services."""
    procfile = Path(__file__).parent.parent / "Procfile"
    content = procfile.read_text()

    assert "web:" in content, "web service not defined"
    assert "pi:" in content, "pi service not defined"


def test_procfile_web_uses_uvicorn():
    """Web service should use uvicorn."""
    procfile = Path(__file__).parent.parent / "Procfile"
    content = procfile.read_text()

    for line in content.splitlines():
        if line.startswith("web:"):
            assert "uvicorn" in line
            assert "backend.main:app" in line
            break


def test_procfile_pi_uses_rpc_mode():
    """Pi service should run in RPC mode."""
    procfile = Path(__file__).parent.parent / "Procfile"
    content = procfile.read_text()

    for line in content.splitlines():
        if line.startswith("pi:"):
            assert "--mode rpc" in line or "--mode=rpc" in line
            break
