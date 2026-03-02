"""Tests for starter prompts API."""


async def test_starter_prompts_endpoint_returns_prompts(client):
    """Starter prompts endpoint should return prompts array."""
    response = await client.get("/api/config/starter-prompts")
    assert response.status_code == 200

    data = response.json()
    assert "prompts" in data
    assert isinstance(data["prompts"], list)
    assert len(data["prompts"]) > 0


async def test_starter_prompts_have_required_fields(client):
    """Each starter prompt should have icon and text fields."""
    response = await client.get("/api/config/starter-prompts")
    data = response.json()

    for prompt in data["prompts"]:
        assert "icon" in prompt
        assert "text" in prompt
        assert isinstance(prompt["text"], str)
        assert len(prompt["text"]) > 0
