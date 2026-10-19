'''Etapa de elegibilidad (T012) - clasificacion elegible / no elegible.

Autoridad: specs/001-sustainable-beach-recommendation/spec.md (FR-001, FR-002,
FR-003, FR-006, FR-012), data-model.md seccion 5 (EligibilityCondition) y
research.md D1 (modelo en dos etapas) y D2-ter (ocupacion no es merito).

Principios aplicados:
- FR-001: toda playa se clasifica como elegible o no elegible ANTES de
  compararla con otras, aplicando condiciones de exclusion.
- FR-002: las condiciones aqui son NO compensables: ningun factor de comodidad
  (distancia, tiempo de viaje, baja ocupacion, servicios) las neutraliza. Por eso
  viven en esta etapa, separada del scoring.
- FR-003: la ausencia de datos no es favorable ni desfavorable; se representa
  como condicion insufficient_data que LIMITA en lugar de excluir.
- Principio IV: una sola implementacion de la regla de exclusion. Esta etapa es
  la DUENA de la deteccion de condiciones; src/utils/scoring.py mantiene
  non_compensable_exclusions como puente (delega aqui) para no duplicarla.

Alcance honesto: solo se emiten condiciones que se puedan DERIVAR de datos
documentados. La incompatibilidad ambiental que requiere un catalogo validado
(Q14) y la vulnerabilidad (Q11) NO se fabrican: si no hay regla validada, no
hay condicion. La ocupacion NO es condicion de elegibilidad (FR-007/FR-014):
es un indicador de presion, no un criterio de exclusion.
'''

from dataclasses import dataclass
from typing import Optional, Tuple

from src.models import FlagColor

# Tipos de condicion (data-model.md seccion 5). Son literales de dominio, no un
# enum de BD; el esquema Pydantic (T005) los acepta como str.
TYPE_OFFICIAL_CLOSURE = "official_closure"
TYPE_OFFICIAL_RESTRICTION = "official_restriction"
TYPE_SAFETY_RISK = "safety_risk"
TYPE_ENVIRONMENTAL_INCOMPATIBILITY = "environmental_incompatibility"
TYPE_INSUFFICIENT_DATA = "insufficient_data"


@dataclass(frozen=True)
class EligibilityCondition:
    '''Condicion de exclusion detectada (elemento de eligibility_conditions).

    Misma forma que src.schemas.EligibilityCondition (T005); el mapeo a
    Pydantic lo hace la capa de API (T014).
    '''

    type: str
    reason: str
    source: Optional[str] = None


@dataclass(frozen=True)
class EligibilityResult:
    '''Resultado de la etapa de elegibilidad para una playa.

    eligible es False si existe al menos una condicion de exclusion (todo tipo
    salvo insufficient_data, que LIMITA en lugar de excluir).

    has_insufficient_data indica si alguna condicion limita por falta de dato;
    la playa puede seguir siendo elegible, pero la recomendacion debe reflejar
    esa limitacion (FR-012).
    '''

    eligible: bool
    conditions: Tuple[EligibilityCondition, ...]
    has_insufficient_data: bool


def _same_value(left, right) -> bool:
    '''Compara enum/valor y cadena ignorando mayusculas.'''
    if left is None:
        return False
    return str(getattr(left, "value", left)).lower() == str(getattr(right, "value", right)).lower()


def _non_empty(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def evaluate_eligibility(beach: dict) -> EligibilityResult:
    '''Clasifica una playa como elegible o no elegible (FR-001).

    beach es un diccionario de observaciones (como el que construyen
    _beach_to_dict y crud). Los campos de metadatos de T004 se leen de forma
    defensiva: si no estan presentes, se tratan como desconocidos (no se fabrica
    ninguna condicion a partir de su ausencia).
    '''
    conditions = []

    # --- Condiciones de seguridad (no compensables) ---------------------------
    # Puente con el scoring: mismas reglas, mismo texto de motivo.
    if _same_value(beach.get("flag_color"), FlagColor.red):
        conditions.append(
            EligibilityCondition(
                type=TYPE_SAFETY_RISK,
                reason="bandera roja: baño no permitido (prohibición oficial)",
                source=None,
            )
        )
    if beach.get("jellyfish_present") is True:
        conditions.append(
            EligibilityCondition(
                type=TYPE_SAFETY_RISK,
                reason="presencia de medusas: riesgo sanitario",
                source=None,
            )
        )

    # --- Restricciones oficiales documentadas ---------------------------------
    restrictions = beach.get("access_restrictions")
    if _non_empty(restrictions):
        conditions.append(
            EligibilityCondition(
                type=TYPE_OFFICIAL_RESTRICTION,
                reason=str(restrictions).strip(),
                source=None,
            )
        )

    # --- Datos insuficientes (limitan, no excluyen) ---------------------------
    if _same_value(beach.get("flag_color"), FlagColor.unknown):
        conditions.append(
            EligibilityCondition(
                type=TYPE_INSUFFICIENT_DATA,
                reason="bandera de seguridad desconocida",
                source=None,
            )
        )

    # Capacidad reclamada sin procedencia documentada (T004 / ADR 0005).
    if beach.get("max_capacity") is not None and not (
        _non_empty(beach.get("capacity_reference")) and _non_empty(beach.get("capacity_method"))
    ):
        conditions.append(
            EligibilityCondition(
                type=TYPE_INSUFFICIENT_DATA,
                reason="capacidad sin procedencia documentada",
                source=None,
            )
        )

    has_insufficient = any(c.type == TYPE_INSUFFICIENT_DATA for c in conditions)
    excluding = [c for c in conditions if c.type != TYPE_INSUFFICIENT_DATA]
    eligible = len(excluding) == 0

    return EligibilityResult(
        eligible=eligible,
        conditions=tuple(conditions),
        has_insufficient_data=has_insufficient,
    )


def is_eligible(beach: dict) -> bool:
    '''Atajo: es la playa elegible?'''
    return evaluate_eligibility(beach).eligible


# --- Puente para src/utils/scoring.py (no duplicar la regla) ------------------

def non_compensable_exclusions(beach: dict) -> Tuple[str, ...]:
    '''Motivos de seguridad no compensables, como texto (compatibilidad).

    Es la misma deteccion que evaluate_eligibility, proyectada a cadenas para
    mantener el contrato de src/utils/scoring.py y sus tests. La fuente de
    verdad es evaluate_eligibility.
    '''
    result = evaluate_eligibility(beach)
    return tuple(
        c.reason
        for c in result.conditions
        if c.type == TYPE_SAFETY_RISK
    )