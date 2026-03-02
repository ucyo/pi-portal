"""Pytest configuration and fixtures."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
async def client():
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
