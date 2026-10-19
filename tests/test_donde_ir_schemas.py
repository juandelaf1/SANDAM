"""Contract tests for the additive ``/donde-ir`` response schemas (task T005).

These tests check the Pydantic v2 schemas in ``src/schemas.py`` against
``specs/001-sustainable-beach-recommendation/contracts/donde-ir.openapi.yaml``
(the contract) and against the *current* response of ``/donde-ir/ahora``.

Every fixture in this file is **synthetic** and exists only to exercise the
schema shape. It is NOT real environmental, capacity or observation data and
must never be presented as such (principle of data veracity / FR-005).
"""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from src.schemas import (
    DataNature,
    DataQuality,
    DondeIrResponse,
    EligibilityCondition,
    Explanation,
    PlayStatus,
    Recommendation,
    ResponseStatus,
)

CONTRACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "specs"
    / "001-sustainable-beach-recommendation"
    / "contracts"
    / "donde-ir.openapi.yaml"
)


def _contract_schemas() -> dict:
    data = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    return data["components"]["schemas"]


def _synthetic_recommendation(**overrides) -> dict:
    """A recommendation dict with exactly the fields the contract preserves."""
    data = {
        "nombre": "Platja sintètica de prova",
        "latitude": 39.53,
        "longitude": 2.71,
        "distancia_km": 12.4,
        "tiempo_viaje_min": 18,
        "hora_llegada": "17:45",
        "score_original": 72.0,
        "score_final": 65.3,
        "status": "recomendada",
        "color": "verde",
        "sol_restante_min": 240,
        "flags": {"playa": "green", "ocupacion": 40},
    }
    data.update(overrides)
    return data


def _synthetic_response(**overrides) -> dict:
    data = {
        "ubicacion_usuario": {"lat": 39.57, "lon": 2.65},
        "hora_actual": "17:20",
        "atardecer": "20:30",
        "sol_restante": "3.2h",
        "total_playas": 20,
        "recomendaciones": [_synthetic_recommendation()],
    }
    data.update(overrides)
    return data


# --- DataQuality -----------------------------------------------------------


def test_data_quality_requires_nature():
    """A value without its nature cannot be classified (FR-004)."""
    with pytest.raises(ValidationError):
        DataQuality(source="font sintètica")


def test_data_quality_rejects_unknown_enum_value():
    with pytest.raises(ValidationError):
        DataQuality(nature="probablement-bona")


def test_data_quality_unknown_needs_no_source_and_is_not_favourable():
    """`unknown` is explicit: it is not invented and not made favourable (FR-003)."""
    dq = DataQuality(nature=DataNature.unknown)
    assert dq.nature is DataNature.unknown
    assert dq.source is None
    assert dq.observed_at is None
    assert dq.model_dump(mode="json")["nature"] == "unknown"


def test_data_quality_accepts_iso_timestamps_and_nulls():
    dq = DataQuality(
        nature="observation",
        source="font sintètica",
        observed_at="2026-08-01T10:30:00",
        fetched_at=None,
        valid_until="2026-08-01T12:00:00",
    )
    assert dq.nature is DataNature.observation
    assert dq.observed_at.year == 2026
    assert dq.fetched_at is None


# --- Explanation -----------------------------------------------------------


def test_explanation_requires_reason():
    with pytest.raises(ValidationError):
        Explanation(factors=["factor sintètic"])


def test_explanation_factors_default_to_empty_list():
    exp = Explanation(reason="motiu sintètic")
    assert exp.factors == []


# --- EligibilityCondition --------------------------------------------------


def test_eligibility_condition_requires_type_and_reason():
    with pytest.raises(ValidationError):
        EligibilityCondition(type="official_closure")


# --- Recommendation --------------------------------------------------------


def test_recommendation_preserves_existing_fields():
    rec = Recommendation(**_synthetic_recommendation())
    assert rec.nombre == "Platja sintètica de prova"
    assert rec.status is PlayStatus.recomendada
    # Additive fields stay absent until a later task computes them.
    assert rec.eligible is None
    assert rec.eligibility_conditions is None
    assert rec.explanation is None
    assert rec.data_quality is None


def test_recommendation_rejects_invalid_status():
    with pytest.raises(ValidationError):
        Recommendation(**_synthetic_recommendation(status="potser"))


def test_recommendation_accepts_additive_fields():
    rec = Recommendation(
        **_synthetic_recommendation(
            eligible=False,
            eligibility_conditions=[
                {
                    "type": "official_closure",
                    "reason": "tancament sintètic",
                    "source": "font sintètica",
                }
            ],
            pressure_relative=0.8,
            explanation={"reason": "motiu sintètic", "factors": ["factor sintètic"]},
            data_quality={
                "occupation": {"nature": "estimate", "source": "font sintètica"},
                "water_temp": {"nature": "unknown"},
            },
        )
    )
    assert rec.eligible is False
    assert rec.eligibility_conditions[0].type == "official_closure"
    assert rec.data_quality["water_temp"].nature is DataNature.unknown
    assert rec.explanation.factors == ["factor sintètic"]


def test_recommendation_additive_defaults_are_not_favourable():
    """Missing optional data must not be coerced into a favourable value."""
    rec = Recommendation(**_synthetic_recommendation())
    assert rec.eligible is None  # not `True`
    assert rec.pressure_relative is None  # not `0`
    assert rec.data_quality is None  # not an empty "everything is fine" map


# --- DondeIrResponse -------------------------------------------------------


def test_donde_ir_response_preserves_existing_shape():
    resp = DondeIrResponse(**_synthetic_response())
    assert resp.total_playas == 20
    assert resp.recomendaciones[0].nombre == "Platja sintètica de prova"
    assert resp.status is None


def test_donde_ir_response_status_enum():
    resp = DondeIrResponse(**_synthetic_response(status="insufficient_data"))
    assert resp.status is ResponseStatus.insufficient_data
    with pytest.raises(ValidationError):
        DondeIrResponse(**_synthetic_response(status="tot-bé"))


def test_travel_time_defaults_to_estimate():
    """No route provider yet: the ETA is an estimate and must not claim precision."""
    resp = DondeIrResponse(**_synthetic_response())
    assert resp.travel_time_is_estimate is True


def test_serialization_omits_absent_additive_fields():
    resp = DondeIrResponse(**_synthetic_response())
    payload = resp.model_dump(mode="json", exclude_none=True)
    assert set(payload["recomendaciones"][0]) == {
        "nombre",
        "latitude",
        "longitude",
        "distancia_km",
        "tiempo_viaje_min",
        "hora_llegada",
        "score_original",
        "score_final",
        "status",
        "color",
        "sol_restante_min",
        "flags",
    }
    assert "status" not in payload  # None values are omitted
    assert payload["travel_time_is_estimate"] is True


# --- Contract / code parity ------------------------------------------------


@pytest.mark.parametrize(
    "model_name, model",
    [
        ("DataQuality", DataQuality),
        ("Explanation", Explanation),
        ("EligibilityCondition", EligibilityCondition),
        ("Recommendation", Recommendation),
        ("DondeIrResponse", DondeIrResponse),
    ],
)
def test_model_fields_match_contract_properties(model_name, model):
    """The Pydantic models declare exactly the contract properties."""
    schemas = _contract_schemas()
    assert set(model.model_fields) == set(schemas[model_name]["properties"])


def test_contract_declares_preserved_fields_as_required():
    schemas = _contract_schemas()
    assert "nature" in schemas["DataQuality"]["required"]
    assert "reason" in schemas["Explanation"]["required"]
    assert {"type", "reason"} <= set(schemas["EligibilityCondition"]["required"])
    assert "nombre" in schemas["Recommendation"]["required"]
    assert "recomendaciones" in schemas["DondeIrResponse"]["required"]


def test_contract_keeps_additive_fields_optional():
    """Additive fields must NOT be required, so current clients keep working."""
    schemas = _contract_schemas()
    assert "eligible" not in schemas["Recommendation"]["required"]
    assert "explanation" not in schemas["Recommendation"]["required"]
    assert "status" not in schemas["DondeIrResponse"]["required"]
    assert (
        schemas["Recommendation"]["properties"]["eligibility_conditions"]["items"]["$ref"]
        == "#/components/schemas/EligibilityCondition"
    )


# --- Backward compatibility with the current endpoint ----------------------


@pytest.mark.asyncio
async def test_current_endpoint_output_validates_against_contract(client, sample_beach):
    """The current ``/donde-ir/ahora`` response already satisfies the preserved part.

    T005 only *defines* the schemas; this proves the existing response shape is a
    subset of the contract (additive fields absent) without changing the endpoint.
    """
    response = await client.get(
        "/api/v1/donde-ir/ahora", params={"lat": 39.57, "lon": 2.65}
    )
    assert response.status_code == 200

    parsed = DondeIrResponse.model_validate(response.json())
    assert parsed.total_playas == 1
    # Tras T014 los campos aditivos se rellenan (ya no son None por defecto).
    assert parsed.status is not None
    assert parsed.travel_time_is_estimate is True
    for rec in parsed.recomendaciones:
        assert rec.nombre
        assert rec.eligible is not None
        assert rec.pressure_relative is not None
