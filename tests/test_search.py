"""Tests for search / nearby / recommendations (regression: enum `.value` crash)."""

import pytest


async def _create(client, name, **overrides):
    payload = {
        "name": name,
        "region": "Mallorca",
        "latitude": 39.5345,
        "longitude": 2.7175,
        "current_occupation": 30,
        "flag_color": "green",
        "water_quality": "excellent",
        "has_lifeguard": True,
    }
    payload.update(overrides)
    return (await client.post("/api/v1/beaches/", json=payload)).json()


@pytest.mark.asyncio
async def test_nearby_returns_sorted_by_distance(client):
    await _create(client, "Far", latitude=39.9, longitude=3.1)
    await _create(client, "Near", latitude=39.54, longitude=2.72)

    response = await client.get(
        "/api/v1/beaches/nearby", params={"lat": 39.54, "lon": 2.72, "radius_km": 50}
    )
    assert response.status_code == 200
    names = [b["name"] for b in response.json()["beaches"]]
    assert names[0] == "Near"


@pytest.mark.asyncio
async def test_search_flags_problem_beach_and_suggests_alternatives(client):
    await _create(client, "Problema", flag_color="yellow", water_quality="sufficient")
    await _create(client, "Buena", flag_color="green", water_quality="excellent")

    response = await client.get("/api/v1/beaches/search", params={"name": "Problema"})
    assert response.status_code == 200
    body = response.json()
    assert body["requested_beach"]["name"] == "Problema"
    assert body["recommendation"] is not None
    assert "Bandera" in body["recommendation"]["reason"]


@pytest.mark.asyncio
async def test_search_healthy_beach_has_no_recommendation(client):
    await _create(client, "Perfecta")
    response = await client.get("/api/v1/beaches/search", params={"name": "Perfecta"})
    assert response.status_code == 200
    assert response.json()["recommendation"] is None


@pytest.mark.asyncio
async def test_recommendations_endpoint(client):
    beach = await _create(client, "Con medusas", jellyfish_present=True)
    response = await client.get(f"/api/v1/beaches/{beach['id']}/recommendations")
    assert response.status_code == 200
    body = response.json()
    assert body["beach_name"] == "Con medusas"
    assert body["alerts"]
