"""Tests for T009: no randomness and no unsupported prediction claims.

These tests guard two properties:

* the data paths of ``src/`` do not use randomness at all (a fabricated value can
  never be presented as a real observation or prediction, FR-005);
* when there is no defined method or the base observation is unknown, the system
  returns an explicit ``insufficient_data`` result instead of a made-up number
  (FR-003, FR-012); and every estimate is labelled with its ``nature``, ``method``
  and ``validated`` flags (FR-004).

All beaches created here are **synthetic fixtures**, not real observations.
"""

import re
from pathlib import Path

import pytest

from src.utils.predictions import (
    predict_jellyfish_presence,
    predict_occupation_advanced,
)
from src.utils.scoring import CANONICAL_WEIGHTS

SRC = Path(__file__).resolve().parents[1] / "src"

FABRICATED_FORECAST_FIELDS = (
    "predicted_occupation",
    "water_temperature",
    "weather",
    "jellyfish_risk",
    "wind_speed",
)

FABRICATED_SHADE_FIELDS = (
    "has_natural_shade",
    "shade_type",
    "shade_available_now",
    "shade_hours",
)


async def _create(client, name, **overrides):
    payload = {
        "name": name,
        "region": "Mallorca",
        "latitude": 39.5345,
        "longitude": 2.7175,
        "current_occupation": 30,
        "uv_index": 4,
        "wave_height": 0.4,
        "flag_color": "green",
        "water_quality": "excellent",
    }
    payload.update(overrides)
    return (await client.post("/api/v1/beaches/", json=payload)).json()


# --- Ausencia de aleatoriedad en el código -----------------------------------


def test_no_randomness_in_src_data_paths():
    import_re = re.compile(r"^\s*(?:import\s+random\b|from\s+random\s+import)", re.M)
    call_re = re.compile(r"\brandom\.")

    offenders = []
    for path in sorted(SRC.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if import_re.search(text) or call_re.search(text):
            offenders.append(str(path.relative_to(SRC)))

    assert offenders == [], f"randomness found in src/: {offenders}"


# --- Determinismo ------------------------------------------------------------


def test_occupation_estimation_is_deterministic():
    beach = {"current_occupation": 40, "water_temp": 25.0}
    assert len({predict_occupation_advanced(beach)["predicted"] for _ in range(20)}) == 1


def test_jellyfish_estimation_is_deterministic():
    beach = {"jellyfish_present": False, "water_temp": 25.0}
    risks = {predict_jellyfish_presence(beach)["risk_level"] for _ in range(20)}
    assert len(risks) == 1


# --- Sin base observada no hay estimación (FR-003) ---------------------------


def test_occupation_estimation_without_a_base_is_unavailable():
    """No ``current_occupation`` -> no invented default; explicit unavailability."""
    result = predict_occupation_advanced({})
    assert result["status"] == "insufficient_data"
    assert result["nature"] == "unknown"
    assert result["validated"] is False
    assert "predicted" not in result


def test_jellyfish_estimation_without_an_observed_presence_is_unavailable():
    result = predict_jellyfish_presence({"water_temp": 25.0})
    assert result["status"] == "insufficient_data"
    assert "risk_level" not in result


def test_jellyfish_estimation_does_not_assume_a_species():
    documented = predict_jellyfish_presence(
        {"jellyfish_present": True, "jellyfish_species": "Pelagia noctiluca"}
    )
    undocumented = predict_jellyfish_presence({"jellyfish_present": True})

    assert documented["expected_species"] == "Pelagia noctiluca"
    assert undocumented["expected_species"] is None


def test_estimations_do_not_claim_an_unvalidated_confidence():
    occupation = predict_occupation_advanced({"current_occupation": 40})
    jellyfish = predict_jellyfish_presence({"jellyfish_present": False})

    for estimation in (occupation, jellyfish):
        assert estimation["nature"] == "prediction"
        assert estimation["validated"] is False
        assert estimation["confidence"] is None
        assert estimation["method"]


# --- Rutas sin método: indisponibilidad explícita (FR-005, FR-012) -----------


@pytest.mark.asyncio
async def test_forecast_declares_unavailability_instead_of_fabricating(client, sample_beach):
    response = await client.get("/api/v1/predictions/forecast/Platja de Palma")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "insufficient_data"
    assert body["nature"] == "unknown"
    assert body["forecast"] is None
    for field in FABRICATED_FORECAST_FIELDS:
        assert field not in body


@pytest.mark.asyncio
async def test_shade_declares_unavailability_instead_of_fabricating(client, sample_beach):
    response = await client.get("/api/v1/predictions/shade/Platja de Palma")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "insufficient_data"
    for field in FABRICATED_SHADE_FIELDS:
        assert field not in body


@pytest.mark.asyncio
async def test_forecast_response_is_stable_between_calls(client, sample_beach):
    first = (await client.get("/api/v1/predictions/forecast/Palma")).json()
    second = (await client.get("/api/v1/predictions/forecast/Palma")).json()

    assert first["status"] == second["status"] == "insufficient_data"
    assert first["reason"] == second["reason"]


# --- Estimaciones expuestas: etiquetadas, nunca como observación --------------


@pytest.mark.asyncio
async def test_occupation_endpoint_labels_an_unvalidated_prediction(client, sample_beach):
    body = (await client.get("/api/v1/predictions/occupation/Palma")).json()

    assert body["status"] == "ok"
    assert body["nature"] == "prediction"
    assert body["validated"] is False
    assert body["confidence"] is None
    assert body["method"]
    assert body["predicted_occupation"] is not None


@pytest.mark.asyncio
async def test_jellyfish_endpoint_does_not_invent_a_species(client, sample_beach):
    body = (await client.get("/api/v1/predictions/jellyfish/Platja de Palma")).json()

    assert body["status"] == "ok"
    assert body["nature"] == "prediction"
    # sample_beach has no documented species: null, never a made-up one.
    assert body["expected_species"] is None


@pytest.mark.asyncio
async def test_occupation_endpoint_validates_missing_base_at_unit_level(client, sample_beach):
    """The unknown-base path is a unit-level property (see above); the endpoint
    always receives an observed ``current_occupation`` from the model."""
    body = (await client.get("/api/v1/predictions/occupation/Platja de Palma")).json()
    assert body["status"] == "ok"
    assert body["current_occupation"] == sample_beach.current_occupation


# --- El scoring divergente se ha retirado (FR-016) ---------------------------


@pytest.mark.asyncio
async def test_ideal_score_uses_the_canonical_scoring(client, sample_beach):
    body = (await client.get("/api/v1/predictions/ideal-score/Platja de Palma")).json()

    assert body["status"] == "ok"
    assert body["eligible"] is True
    assert body["eligibility_conditions"] == []
    assert body["coverage"] == 1.0
    assert set(body["factors"]) == set(CANONICAL_WEIGHTS)
    # Keys of the retired divergent formula must be gone.
    for removed in ("ocupacion", "bandera", "medusas", "calidad", "sostenibilidad"):
        assert removed not in body["factors"]
    # water_quality=excellent(100), wave=0.3(100), uv=8(35) -> (30+20+5.25)/0.65
    assert body["score"] == 85.0
    assert body["relative_pressure"]["value"] == 0.72
    assert "no capacidad oficial" in body["relative_pressure"]["label"]


@pytest.mark.asyncio
async def test_ideal_score_reports_an_exclusion_instead_of_a_score(client, sample_beach):
    await _create(client, "Bandera roja", flag_color="red")

    body = (await client.get("/api/v1/predictions/ideal-score/Bandera roja")).json()

    assert body["status"] == "no_suitable_alternatives"
    assert body["eligible"] is False
    assert body["score"] is None
    assert body["rating"] is None
    assert body["eligibility_conditions"]
    assert body["eligibility_conditions"][0]["type"] == "safety_risk"


@pytest.mark.asyncio
async def test_ideal_score_is_unavailable_when_conditions_are_missing(client, sample_beach):
    await _create(client, "Sin meteo", uv_index=None, wave_height=None)

    body = (await client.get("/api/v1/predictions/ideal-score/Sin meteo")).json()

    assert body["status"] == "insufficient_data"
    assert body["eligible"] is True
    assert body["score"] is None
    assert body["coverage"] < 1.0
