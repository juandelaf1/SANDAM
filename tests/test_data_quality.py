'''Tests for User Story 3 - data quality and uncertainty (T019).

Verifican que los datos ausentes/caducados no se tratan como favorables.
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
async def test_beach_with_missing_conditions_gets_insufficient_status(client, sample_beach):
    '''Una playa sin UV ni oleaje no produce score favorable por defecto.'''
    await _create(client, "Sin meteo", uv_index=None, wave_height=None)
    response = await client.get(
        "/api/v1/predictions/ideal-score/Sin meteo",
    )
    body = response.json()
    assert body["status"] == "insufficient_data"
    assert body["score"] is None
    assert body["coverage"] < 1.0


@pytest.mark.asyncio
async def test_unknown_quality_not_favourable(client, sample_beach):
    '''Calidad de agua desconocida no se presenta como excelente.'''
    await _create(client, "Calidad desconocida", water_quality="unknown")
    response = await client.get(
        "/api/v1/predictions/ideal-score/Calidad desconocida",
    )
    body = response.json()
    # score puede existir (otros factores presentes) pero quality factor es None
    assert body["factors"]["water_quality"] is None