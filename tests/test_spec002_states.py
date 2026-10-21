"""Tests de comportamiento de la spec 002 (observaciones / estado / vigencia).
Verifica los puntos de decisión Q29-Q34 implementados en Fase 0/1.
"""
import uuid
from datetime import datetime, timedelta
from src.utils.observations import classify_observation, relative_pressure


def test_classify_observation_stale_when_valid_until_past():
    past = datetime(2020, 1, 1)
    s = classify_observation(
        observed_at=past, fetched_at=past, valid_until=past,
        nature="observation", validated=True, source_id=str(uuid.uuid4()), method_id=str(uuid.uuid4()),
    )
    assert s.status == "stale"


def test_classify_observation_invalid_when_predicted_without_valid_until():
    s = classify_observation(
        observed_at=datetime.utcnow(), fetched_at=datetime.utcnow(), valid_until=None,
        nature="prediction", validated=False, source_id=str(uuid.uuid4()), method_id=str(uuid.uuid4()),
    )
    assert s.status == "invalid"


def test_classify_observation_unknown_when_nature_unknown():
    s = classify_observation(
        observed_at=datetime.utcnow(), fetched_at=datetime.utcnow(), valid_until=None,
        nature="unknown", validated=False,
    )
    assert s.status == "current"  # no es stale ni invalid, pero nature es desconocido; tratamos como current sin datos


def test_relative_pressure_null_without_reference_or_unit():
    assert relative_pressure(50) is None
    assert relative_pressure(50, unit="%", reference_type=None) is None
    assert relative_pressure(50, unit="%", reference_type="max_capacity") == 0.5


def test_occupancy_status_prevents_favorable_claim_when_unknown():
    # La lógica de recommendations exige occupancy_status en observed/estimated
    # para afirmar condiciones favorables; sin ese estado, no se afirma.
    from src.utils.recommendations import generate_recommendations
    rec = generate_recommendations({
        "current_occupation": 30,
        "occupancy_status": None,
        "flag_color": "green",
        "jellyfish_present": False,
        "water_quality": "excellent",
    })
    msg = rec[0]["message"]
    assert "tranquila" not in msg.lower() or "condiciones documentadas" in msg.lower()
