import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, suffix: str = "") -> str:
    await client.post("/api/v1/auth/register", json={
        "email": f"agent{suffix}@example.com",
        "username": f"agentuser{suffix}",
        "password": "securepass123",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": f"agent{suffix}@example.com",
        "password": "securepass123",
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_agent(client: AsyncClient):
    token = await _register_and_login(client, "1")
    resp = await client.post(
        "/api/v1/agents",
        json={"display_name": "My Agent", "bio": "A test agent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["display_name"] == "My Agent"
    assert data["status"] == "offline"
    assert data["permission_level"] == 1


@pytest.mark.asyncio
async def test_list_agents(client: AsyncClient):
    token = await _register_and_login(client, "2")
    await client.post(
        "/api/v1/agents",
        json={"display_name": "Agent A"},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get("/api/v1/agents", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_update_agent(client: AsyncClient):
    token = await _register_and_login(client, "3")
    create_resp = await client.post(
        "/api/v1/agents",
        json={"display_name": "Original Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    agent_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/v1/agents/{agent_id}",
        json={"display_name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_agent(client: AsyncClient):
    token = await _register_and_login(client, "4")
    create_resp = await client.post(
        "/api/v1/agents",
        json={"display_name": "To Delete"},
        headers={"Authorization": f"Bearer {token}"},
    )
    agent_id = create_resp.json()["id"]
    resp = await client.delete(
        f"/api/v1/agents/{agent_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204
