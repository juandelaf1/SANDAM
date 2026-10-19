"""Scoring canónico único de SANDAM (tarea T006).

Autoridad: `specs/001-sustainable-beach-recommendation/spec.md` (FR-002, FR-003,
FR-007, FR-008, FR-012, FR-014, FR-016), la constitución (Principios I, II, III,
IV, VI) y `specs/001-sustainable-beach-recommendation/research.md` (D1: modelo de
decisión en dos etapas; D2: scoring canónico único; D3: la baja ocupación no es un
mérito).

Propiedades que garantiza este módulo
-------------------------------------

1. **Una sola implementación** (FR-016, Principio IV). Toda puntuación de playa
   **del sistema canónico** se calcula aquí. Nota de alcance: la variante divergente
   `calculate_ideal_score` de `src/api/predictions.py` (y una copia en un notebook
   no versionado) todavía existe y se retira en T008.

2. **Condiciones no compensables** (FR-002, Principios I y III). Las condiciones de
   seguridad **no se ponderan**: se evalúan *antes* del score y lo anulan. Ninguna
   ventaja de comodidad puede compensarlas. (La etapa de elegibilidad completa
   —restricciones oficiales, incompatibilidad ambiental, datos insuficientes—
   pertenece a T012; aquí se cubren las condiciones de seguridad evidentes en la
   propia playa, en un único lugar, para no duplicar la regla.)

3. **Lo desconocido no es favorable ni desfavorable** (FR-003, Principio II). Un
   factor sin dato no aporta puntos ni se sustituye por un valor inventado: se
   omite y el peso se **renormaliza** entre los factores conocidos. La fracción de
   peso con dato se expone como ``coverage``; si no alcanza ``MIN_DATA_COVERAGE``,
   el score es ``None`` ("desconocido") y no un número fabricado (FR-012).

4. **La baja ocupación no es un mérito** (D3, FR-007). La ocupación se expone como
   **indicador de presión relativa** etiquetado (``relative_pressure``); nunca como
   capacidad oficial ni como umbral ecológico (FR-014).

5. **Determinismo** (FR-008, SC-004). Con la misma entrada, el mismo resultado: no
   se usa `random` ni la hora del sistema.

Los pesos y umbrales son **decisiones de producto explícitas** (Principio IV). No
son límites ecológicos ni pretenden precisión científica.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from src.models import FlagColor, WaterQuality

# --- Pesos del score canónico de comparación (etapa 2) ------------------------
# Suman 1.0. Decisión de producto explícita (Principio IV); no son umbrales
# ecológicos ni fijan capacidades. Justificación de cada peso:
#
#   water_quality      0.30  Única variable ambiental con fuente oficial
#                            verificable (calidad de aguas de baño) y la más
#                            relevante para decidir el baño.
#   sea_state          0.20  El oleaje condiciona la seguridad y la viabilidad de
#                            la actividad en el momento de uso.
#   relative_pressure  0.20  Entre playas elegibles, la comparación debe preferir
#                            la de menor presión relativa (spec US1 esc. 3). El
#                            indicador se etiqueta como relativo, nunca como
#                            capacidad oficial (FR-014).
#   solar_exposure     0.15  El calor y la exposición solar son una dimensión
#                            central de la decisión (blueprint §8); se usa el UV
#                            disponible como proxy. No es una valoración médica.
#   services           0.15  Accesibilidad y servicios verificados determinan el
#                            esfuerzo y la comodidad de la visita.
CANONICAL_WEIGHTS: Dict[str, float] = {
    "water_quality": 0.30,
    "sea_state": 0.20,
    "relative_pressure": 0.20,
    "solar_exposure": 0.15,
    "services": 0.15,
}

# Cobertura mínima de datos (fracción de peso con dato real) para emitir un score
# numérico. Decisión de producto explícita: por debajo de este valor el resultado
# combinaría más incógnitas que datos y aparentaría una confianza inexistente, de
# modo que se declara desconocido (FR-003, FR-012).
MIN_DATA_COVERAGE: float = 0.5

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

# Servicios/instalaciones verificados que contribuyen a la comodidad y al acceso.
_SERVICE_KEYS: Tuple[str, ...] = (
    "has_lifeguard",
    "has_shade",
    "has_accessibility",
    "has_parking",
    "has_showers",
    "has_kiosk",
)


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


def calculate_services_score(beach: dict) -> Optional[float]:
    """Cobertura de servicios verificados (0..100) o ``None`` si no consta ninguno.

    Limitación conocida (registrada en ``docs/OPEN_QUESTIONS.md``): el modelo guarda
    los servicios como booleanos con valor por defecto ``False``, así que no puede
    distinguir "no disponible" de "no documentado". Se trata ``False`` como "no
    disponible" mientras el modelo no exprese el desconocido (FR-003).
    """
    present = [bool(beach[key]) for key in _SERVICE_KEYS if key in beach]
    if not present:
        return None
    return round(100.0 * sum(present) / len(present), 1)


def relative_pressure(occupation) -> Optional[float]:
    """Indicador de presión **relativa** derivado de la ocupación (0..1).

    Devuelve ``None`` si la ocupación es desconocida: nunca ``0``, que afirmaría
    "sin presión". Es un indicador relativo, no una capacidad oficial (FR-014).
    """
    value = _as_float(occupation)
    if value is None:
        return None
    return min(1.0, max(0.0, value / 100.0))


def calculate_pressure_score(occupation) -> Optional[float]:
    """Idoneidad (0..100) derivada de la presión **relativa** o ``None`` si es desconocida."""
    pressure = relative_pressure(occupation)
    if pressure is None:
        return None
    return round((1.0 - pressure) * 100.0, 1)


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

    ``score`` es ``None`` cuando hay una condición no compensable o cuando la
    cobertura de datos es insuficiente: "desconocido" es un estado explícito
    (FR-003, FR-012), nunca un número inventado.
    """

    score: Optional[float]
    coverage: float
    factors: Dict[str, Optional[float]]
    exclusions: Tuple[str, ...]
    relative_pressure: Optional[float]


def evaluate_beach(beach: dict) -> BeachScore:
    """Evalúa una playa con el scoring canónico y devuelve el resultado completo."""
    exclusions = non_compensable_exclusions(beach)
    pressure = relative_pressure(beach.get("current_occupation"))

    factors: Dict[str, Optional[float]] = {
        "water_quality": calculate_quality_score(beach.get("water_quality")),
        "sea_state": calculate_sea_state_score(beach.get("wave_height")),
        "relative_pressure": calculate_pressure_score(beach.get("current_occupation")),
        "solar_exposure": calculate_solar_exposure_score(beach.get("uv_index")),
        "services": calculate_services_score(beach),
    }

    total_weight = sum(CANONICAL_WEIGHTS.values())
    known_weight = sum(
        weight for name, weight in CANONICAL_WEIGHTS.items() if factors.get(name) is not None
    )
    coverage = round(known_weight / total_weight, 3)

    if exclusions or coverage < MIN_DATA_COVERAGE:
        return BeachScore(
            score=None,
            coverage=coverage,
            factors=factors,
            exclusions=exclusions,
            relative_pressure=pressure,
        )

    weighted = sum(
        CANONICAL_WEIGHTS[name] * value
        for name, value in factors.items()
        if value is not None
    )
    score = round(weighted / known_weight, 1)
    return BeachScore(
        score=score,
        coverage=coverage,
        factors=factors,
        exclusions=exclusions,
        relative_pressure=pressure,
    )


def calculate_overall_score(beach: dict) -> Optional[float]:
    """Score canónico de comparación (0..100) o ``None`` si es desconocido.

    Punto de entrada único (FR-016). Devuelve un número **solo** cuando la playa
    no tiene condiciones no compensables y hay cobertura de datos suficiente.
    """
    return evaluate_beach(beach).score
