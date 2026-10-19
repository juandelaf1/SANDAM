"""Unit tests for the single canonical scoring (T006 / T007).

Covers determinism, bounds, missing data, data coverage, non-compensable
conditions and the labelled relative-pressure indicator.

All beach dictionaries here are **synthetic fixtures** that only exercise the
scoring rules. They are NOT real observations and must never be presented as
such (principle of data veracity).
"""

import pytest

from src.utils.scoring import (
    CANONICAL_WEIGHTS,
    MIN_DATA_COVERAGE,
    PRESSURE_LABEL,
    calculate_overall_score,
    calculate_pressure_score,
    calculate_quality_score,
    calculate_sea_state_score,
    calculate_services_score,
    calculate_solar_exposure_score,
    evaluate_beach,
    non_compensable_exclusions,
    relative_pressure,
)

SERVICE_KEYS = (
    "has_lifeguard",
    "has_shade",
    "has_accessibility",
    "has_parking",
    "has_showers",
    "has_kiosk",
)


def _beach(**overrides) -> dict:
    """A fully specified synthetic beach, overridable per test."""
    beach = {
        "name": "Platja sintètica de prova",
        "flag_color": "green",
        "jellyfish_present": False,
        "current_occupation": 50,
        "water_quality": "excellent",
        "wave_height": 0.2,
        "uv_index": 3,
    }
    beach.update({key: True for key in SERVICE_KEYS})
    beach.update(overrides)
    return beach


# --- Configuración y determinismo --------------------------------------------


def test_canonical_weights_sum_to_one():
    assert sum(CANONICAL_WEIGHTS.values()) == pytest.approx(1.0)


def test_scoring_is_deterministic():
    beach = _beach()
    assert len({calculate_overall_score(beach) for _ in range(50)}) == 1


def test_score_is_always_within_bounds():
    for occupation in (None, 0, 50, 100):
        for wave in (None, 0.1, 2.0):
            for uv in (None, 1, 11):
                for quality in ("excellent", "poor", "unknown", None):
                    beach = _beach(
                        current_occupation=occupation,
                        wave_height=wave,
                        uv_index=uv,
                        water_quality=quality,
                    )
                    score = calculate_overall_score(beach)
                    assert score is None or 0.0 <= score <= 100.0


# --- Datos ausentes (lo desconocido no es favorable) --------------------------


def test_unknown_quality_is_none_not_an_invented_value():
    assert calculate_quality_score("unknown") is None
    assert calculate_quality_score(None) is None
    assert calculate_quality_score("excellent") == 100.0


def test_unknown_sea_state_and_solar_are_none():
    assert calculate_sea_state_score(None) is None
    assert calculate_solar_exposure_score(None) is None


def test_empty_beach_is_unknown_not_favourable():
    result = evaluate_beach({})
    assert result.score is None
    assert result.coverage == 0.0
    assert result.relative_pressure is None


def test_unknown_factor_is_omitted_and_lowers_coverage():
    result = evaluate_beach(_beach(uv_index=None))
    assert result.factors["solar_exposure"] is None
    assert result.coverage < 1.0
    assert result.score is not None


def test_insufficient_coverage_declares_unknown():
    # Only the occupation is known -> coverage 0.2 < MIN_DATA_COVERAGE.
    result = evaluate_beach({"current_occupation": 10})
    assert result.coverage < MIN_DATA_COVERAGE
    assert result.score is None


def test_evaluate_reports_factors_coverage_and_pressure():
    result = evaluate_beach(_beach())
    assert result.coverage == 1.0
    assert set(result.factors) == set(CANONICAL_WEIGHTS)
    assert result.relative_pressure == 0.5
    assert result.exclusions == ()


# --- Condiciones no compensables (FR-002) ------------------------------------


def test_red_flag_is_not_compensated_by_a_perfect_beach():
    perfect_but_red = _beach(
        flag_color="red",
        current_occupation=0,
        water_quality="excellent",
        wave_height=0.1,
        uv_index=1,
    )
    result = evaluate_beach(perfect_but_red)
    assert result.score is None
    assert result.exclusions
    # The very same beach without the prohibition does score.
    assert evaluate_beach({**perfect_but_red, "flag_color": "green"}).score is not None


def test_low_occupation_alone_does_not_override_an_exclusion():
    """D3/FR-007: an empty beach with a safety exclusion is not promoted."""
    result = evaluate_beach(_beach(current_occupation=0, flag_color="red"))
    assert result.score is None


def test_jellyfish_is_a_non_compensable_condition():
    assert evaluate_beach(_beach(jellyfish_present=True)).score is None
    assert non_compensable_exclusions(_beach()) == ()


def test_exclusions_accept_enum_and_string():
    assert non_compensable_exclusions({"flag_color": "red"})
    assert non_compensable_exclusions({"flag_color": "RED"})
    assert non_compensable_exclusions({"flag_color": "green"}) == ()


# --- Bandas (límites) ---------------------------------------------------------


@pytest.mark.parametrize(
    "wave,expected",
    [
        (0.0, 100.0),
        (0.3, 100.0),
        (0.31, 90.0),
        (0.5, 90.0),
        (0.51, 70.0),
        (1.0, 70.0),
        (1.01, 40.0),
        (1.5, 40.0),
        (1.51, 10.0),
        (5.0, 10.0),
    ],
)
def test_sea_state_bands(wave, expected):
    assert calculate_sea_state_score(wave) == expected


@pytest.mark.parametrize(
    "uv,expected",
    [
        (0, 100.0),
        (2, 100.0),
        (2.1, 85.0),
        (5, 85.0),
        (5.1, 60.0),
        (7, 60.0),
        (7.1, 35.0),
        (10, 35.0),
        (10.1, 15.0),
        (12, 15.0),
    ],
)
def test_solar_bands(uv, expected):
    assert calculate_solar_exposure_score(uv) == expected


# --- Servicios ----------------------------------------------------------------


def test_services_score_none_when_absent():
    assert calculate_services_score({}) is None


def test_services_score_bounds():
    assert calculate_services_score({key: True for key in SERVICE_KEYS}) == 100.0
    assert calculate_services_score({key: False for key in SERVICE_KEYS}) == 0.0


# --- Presión relativa (D3, FR-014) -------------------------------------------


def test_unknown_occupation_does_not_assert_zero_pressure():
    """`None` is not `0`: unknown must never claim "no pressure"."""
    assert relative_pressure(None) is None
    assert calculate_pressure_score(None) is None


def test_relative_pressure_is_bounded_and_monotonic():
    assert relative_pressure(0) == 0.0
    assert relative_pressure(100) == 1.0
    assert relative_pressure(150) == 1.0
    assert relative_pressure(-10) == 0.0
    assert relative_pressure(20) < relative_pressure(80)


def test_pressure_is_labelled_relative_not_official():
    assert "relativa" in PRESSURE_LABEL
    assert "no capacidad oficial" in PRESSURE_LABEL
