"""Tests for the beach CRUD endpoints."""

import pytest


async def _create(client, name="Cala Major", **overrides):
    payload = {
        "name": name,
        "region": "Mallorca",
        "latitude": 39.5638,
        "longitude": 2.6272,
        "current_occupation": 45,
        "flag_color": "green",
        "water_quality": "excellent",
        "has_lifeguard": True,
    }
    payload.update(overrides)
    return await client.post("/api/v1/beaches/", json=payload)


@pytest.mark.asyncio
async def test_create_and_get_beach(client):
    created = await _create(client)
    assert created.status_code == 201
    beach = created.json()
    assert beach["name"] == "Cala Major"
    # Comportamiento corregido por spec 002 (FR-011): una playa creada sin
    # observación no debe nacer como "live"; el estado por defecto es unavailable.
    assert beach["data_status"] == "unavailable"

    fetched = await client.get(f"/api/v1/beaches/{beach['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == beach["id"]


@pytest.mark.asyncio
async def test_create_rejects_invalid_coordinates(client):
    response = await _create(client, latitude=123.0)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_unknown_beach_returns_404(client):
    response = await client.get("/api/v1/beaches/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_malformed_id_returns_422(client):
    response = await client.get("/api/v1/beaches/not-a-uuid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_beach(client):
    beach = (await _create(client)).json()
    response = await client.put(
        f"/api/v1/beaches/{beach['id']}",
        json={"current_occupation": 90, "flag_color": "yellow"},
    )
    assert response.status_code == 200
    assert response.json()["current_occupation"] == 90
    assert response.json()["flag_color"] == "yellow"


@pytest.mark.asyncio
async def test_delete_beach(client):
    beach = (await _create(client)).json()
    deleted = await client.delete(f"/api/v1/beaches/{beach['id']}")
    assert deleted.status_code == 204
    assert (await client.get(f"/api/v1/beaches/{beach['id']}")).status_code == 404


@pytest.mark.asyncio
async def test_list_total_matches_filters(client):
    await _create(client, name="A", has_lifeguard=True)
    await _create(client, name="B", has_lifeguard=False)

    response = await client.get("/api/v1/beaches/", params={"has_lifeguard": "true"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["beaches"]) == 1
