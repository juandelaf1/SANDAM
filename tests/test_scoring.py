"""Unit tests for the single canonical scoring (T006 / T007 + semantic audit).

Covers determinism, bounds, missing data, data coverage, non-compensable
conditions, the labelled relative-pressure indicator, and the two business
properties revisited by the audit:

* **FR-007**: a lower occupation must not, by itself, give a beach an advantage.
* **FR-003**: services whose values come from model defaults must be neither a
  reward nor a penalty, and unknown data must not be replaced by a value.

All beach dictionaries here are **synthetic fixtures** that only exercise the
scoring rules. They are NOT real observations and must never be presented as
such (principle of data veracity).
"""

import pytest

from src.utils.scoring import (
    CANONICAL_WEIGHTS,
    PRESSURE_LABEL,
    calculate_overall_score,
    calculate_quality_score,
    calculate_sea_state_score,
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


def test_canonical_weights_are_relative_and_positive():
    assert all(weight > 0 for weight in CANONICAL_WEIGHTS.values())


def test_scored_factors_are_exactly_the_documented_ones():
    assert set(CANONICAL_WEIGHTS) == {"water_quality", "sea_state", "solar_exposure"}


def test_occupation_is_not_a_scored_factor():
    assert "current_occupation" not in CANONICAL_WEIGHTS
    assert "relative_pressure" not in CANONICAL_WEIGHTS


def test_services_are_not_a_scored_factor():
    assert not set(SERVICE_KEYS) & set(CANONICAL_WEIGHTS)
    assert "services" not in CANONICAL_WEIGHTS


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


# --- FR-007: la baja ocupación no da ventaja por sí sola ---------------------


def test_lower_occupation_gives_no_unjustified_advantage():
    """FR-007: two beaches identical except for occupation get the SAME score."""
    empty = _beach(current_occupation=5)
    crowded = _beach(current_occupation=95)

    assert calculate_overall_score(empty) == calculate_overall_score(crowded)
    assert calculate_overall_score(empty) is not None


def test_low_occupation_alone_does_not_override_an_exclusion():
    """D3/FR-007: an empty beach with a safety exclusion is not promoted."""
    result = evaluate_beach(_beach(current_occupation=0, flag_color="red"))
    assert result.score is None


def test_pressure_remains_available_as_an_indicator():
    """FR-014: occupation is still exposed, but only as a labelled indicator."""
    assert relative_pressure(5) < relative_pressure(95)
    assert "relativa" in PRESSURE_LABEL
    assert "no capacidad oficial" in PRESSURE_LABEL


# --- FR-003: los servicios por defecto no son observaciones ------------------


def test_services_do_not_affect_the_score():
    """FR-003: undocumented or False service flags are neither reward nor penalty."""
    all_true = _beach(**{key: True for key in SERVICE_KEYS})
    all_false = _beach(**{key: False for key in SERVICE_KEYS})
    none_stated = _beach()
    for key in SERVICE_KEYS:
        none_stated.pop(key)

    scores = {calculate_overall_score(beach) for beach in (all_true, all_false, none_stated)}
    assert len(scores) == 1
    assert scores.pop() is not None


def test_services_and_occupation_do_not_count_towards_coverage():
    """`coverage` must only account for what the system can actually attest."""
    no_services = _beach()
    for key in SERVICE_KEYS:
        no_services.pop(key)
    no_occupation = _beach()
    no_occupation.pop("current_occupation")

    assert evaluate_beach(_beach()).coverage == 1.0
    assert evaluate_beach(no_services).coverage == 1.0
    assert evaluate_beach(no_occupation).coverage == 1.0


# --- Datos ausentes (lo desconocido no es favorable) -------------------------


def test_unknown_quality_is_none_not_an_invented_value():
    assert calculate_quality_score("unknown") is None
    assert calculate_quality_score(None) is None
    assert calculate_quality_score("excellent") == 100.0


def test_unknown_sea_state_and_solar_are_none():
    assert calculate_sea_state_score(None) is None
    assert calculate_solar_exposure_score(None) is None


def test_missing_data_is_not_replaced_by_a_favourable_value():
    """FR-003: the old `uv_index=None -> 75.0` must never come back."""
    assert evaluate_beach(_beach(uv_index=None)).score is None
    assert evaluate_beach(_beach(wave_height=None)).score is None


def test_empty_beach_is_unknown_not_favourable():
    result = evaluate_beach({})
    assert result.score is None
    assert result.coverage == 0.0
    assert result.relative_pressure is None


def test_missing_factor_yields_insufficient_information():
    """FR-012: one missing factor is enough to declare insufficient information."""
    result = evaluate_beach(_beach(uv_index=None))
    assert result.score is None
    assert result.coverage < 1.0
    assert result.factors["solar_exposure"] is None


def test_evaluate_reports_factors_coverage_and_pressure():
    result = evaluate_beach(_beach())
    assert result.coverage == 1.0
    assert set(result.factors) == set(CANONICAL_WEIGHTS)
    assert result.relative_pressure == 0.5
    assert result.exclusions == ()
    assert result.score is not None and 0.0 <= result.score <= 100.0


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


# --- Presión relativa (D3, FR-014) -------------------------------------------


def test_unknown_occupation_does_not_assert_zero_pressure():
    """`None` is not `0`: unknown must never claim "no pressure"."""
    assert relative_pressure(None) is None


def test_relative_pressure_is_bounded_and_monotonic():
    assert relative_pressure(0) == 0.0
    assert relative_pressure(100) == 1.0
    assert relative_pressure(150) == 1.0
    assert relative_pressure(-10) == 0.0
    assert relative_pressure(20) < relative_pressure(80)
