"""Integration tests for DB-backed endpoints using the SQLite test database."""

import pytest


@pytest.mark.asyncio
async def test_donde_ir_ahora_uses_database(client, sample_beach):
    response = await client.get(
        "/api/v1/donde-ir/ahora", params={"lat": 39.57, "lon": 2.65}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_playas"] == 1
    assert body["recomendaciones"]
    assert body["recomendaciones"][0]["nombre"] == sample_beach.name


@pytest.mark.asyncio
async def test_evaluar_playa(client, sample_beach):
    response = await client.get(
        "/api/v1/donde-ir/evaluar-playa/Palma",
        params={"lat": 39.57, "lon": 2.65},
    )
    assert response.status_code == 200
    assert response.json()["playa"] == sample_beach.name


@pytest.mark.asyncio
async def test_ideal_score(client, sample_beach):
    response = await client.get("/api/v1/predictions/ideal-score/Platja de Palma")
    assert response.status_code == 200
    body = response.json()
    assert body["beach"] == "Platja de Palma"
    assert 0 <= body["score"] <= 100


@pytest.mark.asyncio
async def test_occupation_prediction(client, sample_beach):
    response = await client.get("/api/v1/predictions/occupation/Palma")
    assert response.status_code == 200
    assert "predicted_occupation" in response.json()


@pytest.mark.asyncio
async def test_external_compare(client, sample_beach):
    response = await client.get(f"/api/v1/external/compare/{sample_beach.id}")
    assert response.status_code == 200
    assert response.json()["current_beach"]["name"] == sample_beach.name


@pytest.mark.asyncio
async def test_external_compare_bad_id(client):
    response = await client.get("/api/v1/external/compare/not-a-uuid")
    assert response.status_code == 422
