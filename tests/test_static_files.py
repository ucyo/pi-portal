"""Tests for static file serving."""


async def test_index_html_served(client):
    """Root path should serve index.html."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>Pi Portal</title>" in response.text


async def test_styles_css_served(client):
    """CSS file should be served."""
    response = await client.get("/styles.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert ":root" in response.text


async def test_app_js_served(client):
    """JavaScript file should be served."""
    response = await client.get("/app.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert "Pi Portal" in response.text


async def test_nonexistent_file_returns_404(client):
    """Nonexistent files should return 404."""
    response = await client.get("/nonexistent.xyz")
    assert response.status_code == 404
