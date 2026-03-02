"""Tests for health check endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint_returns_ok(client):
    """Health endpoint should return status ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_endpoint_is_get_only(client):
    """Health endpoint should only accept GET requests."""
    response = await client.post("/health")
    assert response.status_code == 405
