'''Contract tests for /donde-ir/ahora against contracts/donde-ir.openapi.yaml (T010).

Verifica la forma de la respuesta (campos preservados + aditivos opcionales) y la
compatibilidad con clientes existentes. Las playas creadas son fixtures sinteticas.
'''

import pytest

from src.schemas import DondeIrResponse, Recommendation, ResponseStatus


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
async def test_response_validates_against_contract(client, sample_beach):
    response = await client.get(
        "/api/v1/donde-ir/ahora", params={"lat": 39.57, "lon": 2.65, "incluir_marginales": True}
    )
    assert response.status_code == 200
    parsed = DondeIrResponse.model_validate(response.json())
    assert parsed.ubicacion_usuario.lat == 39.57
    assert parsed.total_playas >= 1
    # Campos preservados (FR-010)
    for rec in parsed.recomendaciones:
        assert isinstance(rec, Recommendation)
        assert rec.nombre and rec.latitude and rec.longitude
        assert rec.score_original is not None
        assert rec.score_final is not None
        assert rec.status.value in ("recomendada", "marginal", "no_merece")
        # Aditivos (opcionales pero ahora cableados)
        assert rec.eligible is not None
    assert parsed.travel_time_is_estimate is True
    # Status global valido
    if parsed.status is not None:
        assert parsed.status in (ResponseStatus.ok, ResponseStatus.no_suitable_alternatives, ResponseStatus.insufficient_data)


@pytest.mark.asyncio
async def test_ineligible_beach_omitted_from_recommendations(client, sample_beach):
    await _create(client, "Excluida", flag_color="red")
    response = await client.get(
        "/api/v1/donde-ir/ahora", params={"lat": 39.57, "lon": 2.65, "incluir_marginales": True}
    )
    parsed = DondeIrResponse.model_validate(response.json())
    names = [r.nombre for r in parsed.recomendaciones]
    assert "Excluida" not in names