"""Tests for health and metadata endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "SANDAM" in response.json()["message"]


@pytest.mark.asyncio
async def test_openapi_exposes_all_routers(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/beaches/" in paths
    assert "/api/v1/donde-ir/ahora" in paths
    assert "/api/v1/predictions/ideal-score/{beach_name}" in paths


@pytest.mark.asyncio
async def test_donde_ir_parameters_do_not_leak_db(client):
    response = await client.get("/openapi.json")
    params = response.json()["paths"]["/api/v1/donde-ir/ahora"]["get"]["parameters"]
    names = {param["name"] for param in params}
    assert "db" not in names
    assert {"lat", "lon"} <= names
