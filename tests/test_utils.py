"""Unit tests for scoring, distance and recommendation helpers."""

from src.models import FlagColor, WaterQuality
from src.utils.distance import haversine_distance
from src.utils.recommendation_engine import (
    calcular_sol_restante,
    calcular_tiempo_viaje,
    predecir_medusas,
)
from src.utils.recommendations import generate_recommendations
from src.utils.scoring import (
    calculate_overall_score,
    calculate_quality_score,
    non_compensable_exclusions,
)


def test_quality_score_accepts_enum_and_string():
    assert calculate_quality_score(WaterQuality.excellent) == 100.0
    assert calculate_quality_score("poor") == 0.0
    assert calculate_quality_score("unknown") is None


def test_red_flag_is_a_non_compensable_exclusion():
    assert non_compensable_exclusions({"flag_color": FlagColor.red})
    assert non_compensable_exclusions({"flag_color": "red"})
    assert non_compensable_exclusions({"flag_color": "green"}) == ()


def test_jellyfish_is_a_non_compensable_exclusion():
    assert non_compensable_exclusions({"jellyfish_present": True})
    assert non_compensable_exclusions({"jellyfish_present": False}) == ()


def test_overall_score_is_bounded():
    good = {
        "flag_color": "green",
        "current_occupation": 10,
        "water_quality": "excellent",
        "jellyfish_present": False,
        "uv_index": 2,
        "wave_height": 0.2,
    }
    score = calculate_overall_score(good)
    assert score is not None
    assert 0.0 <= score <= 100.0


def test_haversine_zero_for_same_point():
    assert haversine_distance(39.5, 2.6, 39.5, 2.6) == 0.0


def test_haversine_known_distance():
    # Palma -> Cala Rajada is roughly 70 km straight line.
    distance = haversine_distance(39.5345, 2.7175, 39.7406, 3.4652)
    assert 55 < distance < 70


def test_travel_time_increases_with_distance():
    assert calcular_tiempo_viaje(10) < calcular_tiempo_viaje(50)


def test_jellyfish_high_risk_rule():
    result = predecir_medusas("NE", 26.0, "sur")
    assert result["riesgo"] == "ALTO"


def test_jellyfish_low_risk_rule():
    assert predecir_medusas("SW", 20.0, None)["riesgo"] == "BAJO"


def test_sun_remaining_is_never_negative():
    assert calcular_sol_restante()["minutos_restantes"] >= 0


def test_generate_recommendations_red_flag_is_danger():
    recs = generate_recommendations({"flag_color": "red", "current_occupation": 10})
    assert recs[0]["level"] == "danger"
