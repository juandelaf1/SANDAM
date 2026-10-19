'''Tests for User Story 2 - explanations (T016).

Verifican que cada recomendacion incluye un motivo legible (FR-006).
'''

import pytest


async def _create(client, name, **overrides):
    payload = {
        "name": name,
        "region": "Mallorca",
        "latitude": 39.5345,
        "longitude": 2.7175,
        "current_occupation": 50,
        "uv_index": 4,
        "wave_height": 0.4,
        "flag_color": "green",
        "water_quality": "excellent",
    }
    payload.update(overrides)
    return (await client.post("/api/v1/beaches/", json=payload)).json()


@pytest.mark.asyncio
async def test_recommendation_includes_explanation(client, sample_beach):
    response = await client.get(
        "/api/v1/donde-ir/ahora",
        params={"lat": 39.57, "lon": 2.65, "incluir_marginales": True},
    )
    assert response.status_code == 200
    for rec in response.json()["recomendaciones"]:
        assert "explanation" in rec
        if rec["explanation"] is not None:
            assert "reason" in rec["explanation"]
            assert isinstance(rec["explanation"]["factors"], list)


@pytest.mark.asyncio
async def test_excluded_beach_not_in_recommendations(client, sample_beach):
    await _create(client, "Cerrada", flag_color="red")
    response = await client.get(
        "/api/v1/donde-ir/ahora",
        params={"lat": 39.57, "lon": 2.65, "incluir_marginales": True},
    )
    names = [r["nombre"] for r in response.json()["recomendaciones"]]
    assert "Cerrada" not in names