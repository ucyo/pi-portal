"""Tests for CORS configuration."""


async def test_cors_allows_any_origin(client):
    """CORS should allow any origin for local development."""
    response = await client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    # With allow_credentials=True, the middleware reflects the origin back
    assert (
        response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    )


async def test_cors_allows_credentials(client):
    """CORS should allow credentials."""
    response = await client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-credentials") == "true"


async def test_cors_headers_on_get_request(client):
    """CORS headers should be present on regular GET requests."""
    response = await client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    # CORS header should be present (either "*" or the reflected origin)
    assert response.headers.get("access-control-allow-origin") is not None
