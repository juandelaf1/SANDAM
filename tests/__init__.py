import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "SANDAM" in response.json()["message"]


@pytest.mark.asyncio
async def test_list_beaches_empty(client):
    response = await client.get("/api/v1/beaches/")
    assert response.status_code == 200
    assert "total" in response.json()
    assert "beaches" in response.json()