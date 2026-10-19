'''Integration tests for User Story 1 (T011).

Verifican la etapa de elegibilidad, la no-compensacion por comodidad y la
no-promocion de la baja afluencia (FR-001, FR-002, FR-007, FR-014).

Las playas creadas son fixtures sinteticas, no observaciones reales.
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
async def test_ineligible_beach_is_not_recommended(client, sample_beach):
    '''Una playa con bandera roja no se propone como alternativa (FR-001).'''
    await _create(client, "Bandera roja", flag_color="red")

    response = await client.get(
        "/api/v1/donde-ir/ahora",
        params={"lat": 39.57, "lon": 2.65, "incluir_marginales": True},
    )
    assert response.status_code == 200
    names = [r["nombre"] for r in response.json()["recomendaciones"]]
    assert "Bandera roja" not in names


@pytest.mark.asyncio
async def test_perfect_but_excluded_beach_is_not_promoted(client, sample_beach):
    '''FR-002: comodidad perfecta no neutraliza una exclusion (bandera roja).'''
    await _create(
        client,
        "Perfecta pero cerrada",
        flag_color="red",
        current_occupation=0,
        water_quality="excellent",
        uv_index=2,
        wave_height=0.1,
    )

    response = await client.get(
        "/api/v1/donde-ir/ahora",
        params={"lat": 39.57, "lon": 2.65, "incluir_marginales": True},
    )
    names = [r["nombre"] for r in response.json()["recomendaciones"]]
    assert "Perfecta pero cerrada" not in names


@pytest.mark.asyncio
async def test_low_occupation_does_not_promote_a_beach(client, sample_beach):
    '''FR-007: dos playas identicas salvo ocupacion obtienen el mismo score.

    La ocupacion no entra en el score ni en la ordenacion: solo se expone como
    indicador de presion relativa.
    '''
    await _create(client, "Vacia", current_occupation=5)
    await _create(client, "Llena", current_occupation=95)

    response = await client.get(
        "/api/v1/donde-ir/ahora",
        params={"lat": 39.57, "lon": 2.65, "incluir_marginales": True},
    )
    recs = {r["nombre"]: r for r in response.json()["recomendaciones"]}
    assert "Vacia" in recs and "Llena" in recs
    assert recs["Vacia"]["score_original"] == recs["Llena"]["score_original"]

    # La presion relativa refleja la diferencia, pero como indicador etiquetado.
    assert recs["Vacia"]["pressure_relative"] < recs["Llena"]["pressure_relative"]


@pytest.mark.asyncio
async def test_eligible_beach_exposes_eligibility_fields(client, sample_beach):
    '''Los campos aditivos de T005 se exponen en cada recomendacion (T014).'''
    response = await client.get(
        "/api/v1/donde-ir/ahora",
        params={"lat": 39.57, "lon": 2.65, "incluir_marginales": True},
    )
    for rec in response.json()["recomendaciones"]:
        assert rec["eligible"] is True
        assert rec["eligibility_conditions"] == []
        assert rec["pressure_relative"] is not None
        assert rec["travel_time_is_estimate"] is True