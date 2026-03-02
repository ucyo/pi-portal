"""Tests for FastAPI application setup."""

from backend.main import app


def test_app_title():
    """App should have correct title."""
    assert app.title == "Pi Portal"


def test_app_has_health_route():
    """App should have health check route registered."""
    routes = [route.path for route in app.routes]
    assert "/health" in routes
