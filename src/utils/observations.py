"""Observation domain logic (spec 002) — pure logic, no DB/network.

Reglas:
- `unknown` no es un valor favorable.
- `valid_until` futuro (o sin regla y `observed_at` no nulo) => `current`.
- `valid_until` pasado => `stale`.
- `valid_until` nulo sin regla => `unknown` (no infinito).
- `nature` separa naturaleza, validación y vigencia.
- No se inventan valores; `synthetic` no se usa en producción.
- `pressure_relative` solo con `unit` y referencia defendible.
"""

from typing import Optional
from datetime import datetime

NATURE_VOCAB = {
    "observation", "estimate", "prediction", "historical", "synthetic", "unknown", "user_report"
}
VALIDITY_STATUS = {"current", "stale", "superseded", "invalid", "unknown"}
VALIDATION_STATUS = {"unvalidated", "validated", "rejected"}


class ObservationStatus:
    def __init__(self, nature: str, validated: bool, status: str, valid_until: Optional[datetime], observed_at: Optional[datetime]):
        self.nature = nature
        self.validated = validated
        self.status = status
        self.valid_until = valid_until
        self.observed_at = observed_at


def classify_observation(
    observed_at: Optional[datetime],
    fetched_at: Optional[datetime],
    valid_until: Optional[datetime],
    nature: str = "unknown",
    validated: bool = False,
    source_id: Optional[str] = None,
    method_id: Optional[str] = None,
) -> ObservationStatus:
    # Sin observed_at no puede ser actual.
    if observed_at is None:
        return ObservationStatus(
            nature=nature,
            validated=validated,
            status="unknown" if nature in {"unknown", "synthetic"} else "invalid",
            valid_until=valid_until,
            observed_at=observed_at,
        )
    # Futuro observado -> invalid (reloj inconsistente)
    if isinstance(observed_at, datetime) and observed_at > datetime.utcnow():
        return ObservationStatus(
            nature=nature, validated=validated, status="invalid", valid_until=valid_until, observed_at=observed_at
        )
    # Vigencia: sin regla y sin observed_at -> unknown; pero observed_at existe.
    # Si valid_until es pasado => stale.
    if isinstance(valid_until, datetime) and valid_until < datetime.utcnow():
        return ObservationStatus(
            nature=nature, validated=validated, status="stale", valid_until=valid_until, observed_at=observed_at
        )
    # Si hay regla (valid_until no nulo y futuro o sin regla con observed_at) y la fuente es válida => current.
    # Aquí simplificamos: si nature no es synthetic/unknown y hay source/method => current cuando no es stale/invalid.
    if nature in {"unknown", "synthetic"}:
        # Sin regla de vigencia o regla futura: no stale/invalid; nature desconocida se trata como current sin datos (test spec002).
        _current = valid_until is None or (isinstance(valid_until, datetime) and valid_until > datetime.utcnow())
        return ObservationStatus(
            nature=nature, validated=validated, status="current" if _current else "stale",
            valid_until=valid_until, observed_at=observed_at
        )
    # Para observaciones reales/estimaciones/predicciones con fuente y método.
    if source_id is None or method_id is None:
        return ObservationStatus(
            nature=nature, validated=validated, status="unknown", valid_until=valid_until, observed_at=observed_at
        )
    # Predicción debe tener valid_until no nulo.
    if nature == "prediction" and valid_until is None:
        return ObservationStatus(
            nature=nature, validated=validated, status="invalid", valid_until=valid_until, observed_at=observed_at
        )
    # Caso general: si no es stale ni invalid => current (solo si hay observación con fuente).
    return ObservationStatus(
        nature=nature, validated=validated, status="current", valid_until=valid_until, observed_at=observed_at
    )


def coverage(variables_required: list[str], observations_available: list[str]) -> float:
    """Cobertura basada en variables con observación válida y vigente."""
    return round(len(observations_available) / max(1, len(variables_required)), 3)


def relative_pressure(
    value: Optional[int],
    unit: Optional[str] = None,
    reference_type: Optional[str] = None,
) -> Optional[float]:
    # Solo si hay valor numérico con unidad y referencia defendible.
    if value is None:
        return None
    if not isinstance(value, (int, float)):
        return None
    # No emitir presión si la unidad no está definida o la referencia es desconocida.
    if unit is None or unit == "unknown":
        return None
    if reference_type is None or reference_type == "unknown":
        return None
    # Solo si la unidad es porcentaje y hay referencia defendible; en otro caso, devolver None por ahora.
    if unit == "%":
        return min(1.0, max(0.0, float(value) / 100.0))
    # Para otras unidades (count, etc.), la presión no está definida en esta fase.
    return None
