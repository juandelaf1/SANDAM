"""Scoring canónico único de SANDAM (tarea T006 y su auditoría semántica).

Autoridad: `specs/001-sustainable-beach-recommendation/spec.md` (FR-002, FR-003,
FR-007, FR-008, FR-012, FR-014, FR-016), la constitución (Principios I, II, III,
IV, VI) y `specs/001-sustainable-beach-recommendation/research.md` (D1: modelo de
decisión en dos etapas; D2/D2-bis/D2-ter: scoring canónico; D3: la baja ocupación
no es un mérito).

Propiedades que garantiza este módulo
-------------------------------------

1. **Una sola implementación** (FR-016, Principio IV). Toda puntuación de playa
   **del sistema canónico** se calcula aquí. Nota de alcance: la variante
   divergente `calculate_ideal_score` de `src/api/predictions.py` se retira en
   T008.

2. **Condiciones no compensables** (FR-002, Principios I y III). Las condiciones de
   seguridad **no se ponderan**: se evalúan *antes* del score y lo anulan. Ninguna
   ventaja de comodidad puede compensarlas. (La etapa de elegibilidad completa
   —restricciones oficiales, incompatibilidad ambiental, datos insuficientes—
   pertenece a T012; aquí se cubren las condiciones de seguridad evidentes en la
   propia playa, en un único lugar, para no duplicar la regla.)

3. **Lo desconocido no es favorable ni desfavorable** (FR-003, Principio II). Un
   factor sin dato no aporta puntos, no se sustituye por un valor inventado y no
   se compensa renormalizando: un score numérico **solo existe si todos los
   factores puntuados están documentados**. Si falta alguno, el resultado es
   ``None`` = *información insuficiente* (FR-012). Así lo desconocido nunca se
   convierte en una ventaja por el mero hecho de faltar.

4. **La baja ocupación no es un mérito** (FR-007, D3). La ocupación **no se
   puntúa**: se expone como **indicador de presión relativa** etiquetado
   (``relative_pressure``, FR-014), nunca como capacidad oficial ni como umbral
   ecológico. Ponderarla premiaría automáticamente las playas menos ocupadas
   mientras el sistema todavía no puede comprobar vulnerabilidad, restricción ni
   capacidad (T012).

5. **Los servicios no se puntúan** (FR-003). El modelo guarda los servicios como
   booleanos con valor por defecto ``False``, así que no puede distinguir
   "ausencia confirmada" de "no documentado"; puntuarlos trataría un valor por
   defecto como una observación verificada. Bloqueo registrado en
   ``docs/OPEN_QUESTIONS.md`` (Q26).

6. **Determinismo** (FR-008, SC-004). Con la misma entrada, el mismo resultado: no
   se usa `random` ni la hora del sistema.

Los pesos y umbrales son **decisiones de producto explícitas** (Principio IV). No
son límites ecológicos ni pretenden precisión científica.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from src.models import FlagColor, WaterQuality

# --- Pesos del score canónico de comparación (etapa 2) ------------------------
# Pesos **relativos** entre los factores que sí se puntúan. El score es su media
# ponderada normalizada, de modo que no es necesario que sumen 1.0.
#
# Factores puntuados y justificación (decisión de producto explícita, Principio IV;
# no son umbrales ecológicos ni fijan capacidades):
#   water_quality    0.30  Única variable ambiental con fuente oficial verificable
#                          (calidad de aguas de baño) y la más relevante para
#                          decidir el baño.
#   sea_state        0.20  El estado de la mar condiciona la viabilidad y la
#                          seguridad de la actividad en el momento de uso.
#   solar_exposure   0.15  El calor y la exposición solar condicionan la estancia;
#                          se usa el UV disponible como proxy. No es una
#                          valoración médica.
#
# **No** son factores (auditoría semántica de T006, ver research.md §D2-ter):
#   * la ocupación (FR-007: premiaría la baja afluencia sin poder comprobar aún
#     vulnerabilidad, restricción ni capacidad); se expone solo como indicador;
#   * los servicios (FR-003: el modelo no distingue ausencia confirmada de dato no
#     documentado; ver Q26).
CANONICAL_WEIGHTS: Dict[str, float] = {
    "water_quality": 0.30,
    "sea_state": 0.20,
    "solar_exposure": 0.15,
}

# Etiqueta explícita del indicador de presión (FR-014): es relativo y no un
# límite ecológico oficial.
PRESSURE_LABEL: str = "presión relativa (indicador, no capacidad oficial)"

# --- Tablas de idoneidad ------------------------------------------------------
# Bandas de oleaje (m) -> idoneidad 0..100. Decisión de producto explícita; NO es
# un límite de seguridad: las prohibiciones y avisos oficiales mandan (Principio I).
_SEA_STATE_BANDS: Tuple[Tuple[float, float], ...] = (
    (0.3, 100.0),  # mar en calma
    (0.5, 90.0),
    (1.0, 70.0),
    (1.5, 40.0),
)
_SEA_STATE_BEYOND: float = 10.0

# Bandas de índice UV -> idoneidad 0..100. Decisión de producto explícita; refleja
# el confort/exposición para una actividad al aire libre, no un criterio médico.
_SOLAR_BANDS: Tuple[Tuple[float, float], ...] = (
    (2.0, 100.0),
    (5.0, 85.0),
    (7.0, 60.0),
    (10.0, 35.0),
)
_SOLAR_BEYOND: float = 15.0

# Calidad del agua (fuente oficial). Un valor no reconocido o `unknown` -> None.
_QUALITY_SCORES: Dict[WaterQuality, float] = {
    WaterQuality.excellent: 100.0,
    WaterQuality.good: 75.0,
    WaterQuality.sufficient: 50.0,
    WaterQuality.poor: 0.0,
}


def _as_float(value) -> Optional[float]:
    """Float de ``value`` o ``None`` si no es numérico (nunca lanza)."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _same_value(left, right) -> bool:
    """Compara enum/valor y cadena ignorando mayúsculas (p. ej. FlagColor.red / 'red')."""
    if left is None:
        return False
    return str(getattr(left, "value", left)).lower() == str(getattr(right, "value", right)).lower()


# --- Factores del score canónico ----------------------------------------------


def calculate_quality_score(quality) -> Optional[float]:
    """Idoneidad por calidad del agua de baño (0..100) o ``None`` si es desconocida."""
    if quality is None:
        return None
    return _QUALITY_SCORES.get(quality)


def calculate_sea_state_score(wave_height) -> Optional[float]:
    """Idoneidad por estado de la mar (0..100) o ``None`` si no hay dato de oleaje."""
    height = _as_float(wave_height)
    if height is None:
        return None
    for upper, value in _SEA_STATE_BANDS:
        if height <= upper:
            return value
    return _SEA_STATE_BEYOND


def calculate_solar_exposure_score(uv_index) -> Optional[float]:
    """Idoneidad por exposición solar (0..100) o ``None`` si no hay dato de UV."""
    uv = _as_float(uv_index)
    if uv is None:
        return None
    for upper, value in _SOLAR_BANDS:
        if uv <= upper:
            return value
    return _SOLAR_BEYOND


# --- Indicador de presión relativa (no es un factor del score) ----------------


def relative_pressure(occupation) -> Optional[float]:
    """Indicador de presión **relativa** derivado de la ocupación (0..1).

    Devuelve ``None`` si la ocupación es desconocida: nunca ``0``, que afirmaría
    "sin presión". Es un indicador relativo, no una capacidad oficial (FR-014) y
    **no** participa en el score (FR-007).
    """
    value = _as_float(occupation)
    if value is None:
        return None
    return min(1.0, max(0.0, value / 100.0))


# --- Condiciones no compensables ----------------------------------------------


def non_compensable_exclusions(beach: dict) -> Tuple[str, ...]:
    """Condiciones de seguridad que **no** se compensan con comodidad (FR-002).

    Son reglas de exclusión, no factores de puntuación: se aplican *antes* del
    score. Se mantienen aquí, en un único lugar (Principio IV), como puente
    explícito hacia la etapa de elegibilidad completa (T012, ``eligibility.py``),
    que leerá además restricciones oficiales, incompatibilidad ambiental y datos
    insuficientes desde las observaciones y las expondrá en
    ``eligibility_conditions``.
    """
    reasons = []
    if _same_value(beach.get("flag_color"), FlagColor.red):
        reasons.append("bandera roja: baño no permitido (prohibición oficial)")
    if beach.get("jellyfish_present") is True:
        reasons.append("presencia de medusas: riesgo sanitario")
    return tuple(reasons)


# --- Resultado canónico -------------------------------------------------------


@dataclass(frozen=True)
class BeachScore:
    """Resultado canónico para una playa.

    ``score`` es ``None`` cuando hay una condición no compensable o cuando no
    están documentados **todos** los factores puntuados: "desconocido" es un
    estado explícito (FR-003, FR-012), nunca un número fabricado ni un valor por
    defecto.

    ``coverage`` es la fracción del peso puntuado que tiene dato; un score
    numérico exige ``coverage == 1.0``. Sirve de diagnóstico (qué falta lo
    detalla ``factors``) y para que un consumidor no trate una puntuación parcial
    como si tuviera la fiabilidad de una completa.

    ``relative_pressure`` es un **indicador** etiquetado (FR-014); no es un factor
    del score (FR-007).
    """

    score: Optional[float]
    coverage: float
    factors: Dict[str, Optional[float]]
    exclusions: Tuple[str, ...]
    relative_pressure: Optional[float]


def evaluate_beach(beach: dict) -> BeachScore:
    """Evalúa una playa con el scoring canónico y devuelve el resultado completo."""
    exclusions = non_compensable_exclusions(beach)

    factors: Dict[str, Optional[float]] = {
        "water_quality": calculate_quality_score(beach.get("water_quality")),
        "sea_state": calculate_sea_state_score(beach.get("wave_height")),
        "solar_exposure": calculate_solar_exposure_score(beach.get("uv_index")),
    }

    total_weight = sum(CANONICAL_WEIGHTS.values())
    known_weight = sum(
        weight for name, weight in CANONICAL_WEIGHTS.items() if factors.get(name) is not None
    )
    coverage = round(known_weight / total_weight, 3)

    score: Optional[float] = None
    if not exclusions and all(value is not None for value in factors.values()):
        weighted = sum(CANONICAL_WEIGHTS[name] * value for name, value in factors.items())
        score = round(weighted / total_weight, 1)

    return BeachScore(
        score=score,
        coverage=coverage,
        factors=factors,
        exclusions=exclusions,
        relative_pressure=relative_pressure(beach.get("current_occupation")),
    )


def calculate_overall_score(beach: dict) -> Optional[float]:
    """Score canónico de comparación (0..100) o ``None`` si es desconocido.

    Punto de entrada único (FR-016). Devuelve un número **solo** cuando la playa
    no tiene condiciones no compensables y están documentados todos los factores
    puntuados; en otro caso declara información insuficiente (FR-012).
    """
    return evaluate_beach(beach).score
