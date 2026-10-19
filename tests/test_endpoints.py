"""Integration tests for DB-backed endpoints using the SQLite test database."""

import pytest


@pytest.mark.asyncio
async def test_donde_ir_ahora_uses_database(client, sample_beach, monkeypatch):
    '''Caso A: el escenario requiere recomendaciones; se controla el instante
    para no depender de la hora del reloj (FR-012 no se rebaja).'''
    import src.api.donde_ir as donde_ir_module

    def _sol_controlado():
        return {
            "hora_actual": "12:00",
            "hora_atardecer": "20:30",
            "horas_restantes": 8.5,
            "minutos_restantes": 510,
        }

    monkeypatch.setattr(donde_ir_module, "calcular_sol_restante", _sol_controlado)
    # El motor importa la funcion por nombre al cargar el modulo; se parchea tambien alli.
    import src.utils.recommendation_engine as engine_module
    monkeypatch.setattr(engine_module, "calcular_sol_restante", _sol_controlado)

    response = await client.get(
        "/api/v1/donde-ir/ahora", params={"lat": 39.57, "lon": 2.65}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_playas"] == 1
    assert body["recomendaciones"]
    assert body["recomendaciones"][0]["nombre"] == sample_beach.name


@pytest.mark.asyncio
async def test_donde_ir_ahora_sin_alternativas_no_inventa(client, sample_beach, monkeypatch):
    '''Caso B: sin alternativas adecuadas para el momento, el endpoint declara el
    estado previsto por el contrato sin inventar recomendaciones (FR-012).'''
    import src.api.donde_ir as donde_ir_module
    import src.utils.recommendation_engine as engine_module

    def _sol_noche():
        return {
            "hora_actual": "23:30",
            "hora_atardecer": "20:30",
            "horas_restantes": 0.0,
            "minutos_restantes": 0,
        }

    monkeypatch.setattr(donde_ir_module, "calcular_sol_restante", _sol_noche)
    monkeypatch.setattr(engine_module, "calcular_sol_restante", _sol_noche)

    response = await client.get(
        "/api/v1/donde-ir/ahora", params={"lat": 39.57, "lon": 2.65}
    )
    assert response.status_code == 200
    body = response.json()
    # No se inventan recomendaciones: la playa queda "no_merece" y se filtra.
    assert body["recomendaciones"] == []
    assert body["status"] in ("no_suitable_alternatives", "insufficient_data")
    assert body["total_playas"] == 1
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
