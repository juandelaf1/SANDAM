"""Predicciones deterministas e indisponibilidad explícita (T008).

Reglas (constitución, Principios II y V; FR-003, FR-005, FR-009, FR-012):

* **Sin aleatoriedad.** Este módulo no genera valores al azar. Cuando no existe un
  método definido, o faltan los datos de partida, se declara la indisponibilidad
  (``status: "insufficient_data"``) en lugar de fabricar un resultado.
* **Naturaleza declarada.** Cada resultado declara ``nature`` ("prediction"),
  ``method`` y ``validated``. Mientras no exista una validación con datos reales,
  ``validated`` es ``False``: el método es determinista y explícito, pero **no**
  está contrastado, así que tampoco se emite un nivel de confianza (``confidence``
  es ``None``). No hay aquí ninguna afirmación de predicción sustentada.
* **Las entradas desconocidas no se inventan.** Si falta la base de la estimación,
  no se sustituye por un valor por defecto: la estimación no se emite.

Los valores observados que entran (ocupación actual, temperatura del agua,
presencia de medusas, especie) se usan tal cual; este módulo no los modifica ni los
completa. Distinción de capas: observación (lo que viene de la base de datos),
cálculo determinista (el método de este módulo) y predicción (su resultado
etiquetado).
"""

from datetime import datetime
from typing import Dict, Optional

STATUS_OK = "ok"
STATUS_INSUFFICIENT_DATA = "insufficient_data"
NATURE_PREDICTION = "prediction"
NATURE_UNKNOWN = "unknown"

# Identificadores de método (versionados: si el método cambia, cambia el id).
METHOD_OCCUPATION = "heuristic_hour_day_weather_v1"
METHOD_JELLYFISH = "heuristic_wind_tide_temperature_v1"

# Motivos de indisponibilidad cuando no existe un método definido ni datos.
REASON_NO_METHOD_FORECAST = (
    "no existe un método definido ni datos de pronóstico para días futuros; "
    "no se generan valores simulados (FR-005)"
)
REASON_NO_METHOD_NATURAL_SHADE = (
    "no existe fuente para la sombra natural (orientación, acantilados, vegetación) "
    "en el modelo; no se inventan condiciones físicas (FR-003, FR-005)"
)


def _unavailable(reason: str, method: Optional[str] = None) -> Dict:
    """Resultado explícito de indisponibilidad (FR-012)."""
    return {
        "status": STATUS_INSUFFICIENT_DATA,
        "reason": reason,
        "nature": NATURE_UNKNOWN,
        "method": method,
        "validated": False,
    }


def get_best_time_to_go(current_hour: int) -> str:
    """Franja horaria sugerida por el método heurístico (no es una observación)."""
    if 6 <= current_hour <= 9:
        return "Ahora mismo - Mañana temprano"
    elif 9 <= current_hour <= 12:
        return "Antes del mediodia"
    elif 12 <= current_hour <= 15:
        return "Mejor esperar - Hora punta"
    elif 15 <= current_hour <= 18:
        return "Tarde - Mejor momento"
    elif 18 <= current_hour <= 21:
        return "Ahora mismo - Atardecer"
    else:
        return "Mañana temprano"


def predict_occupation_advanced(beach: Dict, weather_data: Dict = None) -> Dict:
    """Estimación determinista de ocupación a partir de hora, día y meteo.

    Método heurístico **no validado** (``validated: False``). Si la ocupación
    actual es desconocida no hay base para estimar y se declara indisponible
    (FR-003, FR-012): no se parte de un valor inventado.
    """
    base_occupation = beach.get("current_occupation")
    if base_occupation is None:
        return _unavailable(
            "ocupación actual desconocida: no hay base para la estimación",
            METHOD_OCCUPATION,
        )

    hour = datetime.now().hour
    day_of_week = datetime.now().weekday()

    if 8 <= hour <= 10:
        hour_factor = -20
    elif 10 <= hour <= 13:
        hour_factor = 10
    elif 13 <= hour <= 17:
        hour_factor = 25
    elif 17 <= hour <= 20:
        hour_factor = 5
    elif 20 <= hour <= 22:
        hour_factor = -15
    else:
        hour_factor = -30

    if day_of_week >= 5:
        day_factor = 20
    elif day_of_week == 4:
        day_factor = 10
    else:
        day_factor = 0

    weather_factor = 0
    if weather_data:
        weather = weather_data.get("weather") or {}
        temp = weather.get("ta")
        wind = weather.get("vv")
        if temp is not None and wind is not None:
            if temp > 25 and wind < 5:
                weather_factor = 15
            elif temp < 18 or wind > 10:
                weather_factor = -10

    predicted = max(0, min(100, base_occupation + hour_factor + day_factor + weather_factor))

    return {
        "status": STATUS_OK,
        "current": base_occupation,
        "predicted": round(predicted),
        # El método no está validado con datos reales: no se declara confianza.
        "confidence": None,
        "nature": NATURE_PREDICTION,
        "method": METHOD_OCCUPATION,
        "validated": False,
        "factors": {
            "hour_impact": hour_factor,
            "day_impact": day_factor,
            "weather_impact": weather_factor,
        },
        "recommendation": "IR" if predicted < 65 else "EVITAR" if predicted > 85 else "PRECAUCIÓN",
        "best_time": get_best_time_to_go(hour),
    }


def predict_jellyfish_presence(
    beach: Dict,
    wind_data: Dict = None,
    tide_data: Dict = None,
    historical_data: Dict = None,
) -> Dict:
    """Estimación determinista del riesgo de medusas (viento, marea, temperatura).

    Método heurístico **no validado**. La presencia observada
    (``jellyfish_present``) es la base: si es desconocida, no hay base y se declara
    indisponible (FR-003). La especie solo se informa si está documentada; nunca se
    asume una especie.
    """
    present = beach.get("jellyfish_present")
    if present is None:
        return _unavailable(
            "presencia de medusas desconocida: no hay base para estimar el riesgo",
            METHOD_JELLYFISH,
        )

    base_risk = 0.7 if present else 0.1

    wind_factor = 0
    if wind_data:
        wind_speed = wind_data.get("vv")
        wind_dir = wind_data.get("dv")
        if wind_dir is not None:
            if 90 <= wind_dir <= 180:
                wind_factor = 0.3
            elif 180 <= wind_dir <= 270:
                wind_factor = -0.2
        if wind_speed is not None and wind_speed > 8:
            wind_factor += 0.1

    tide_factor = 0
    if tide_data and tide_data.get("tide") == "baja":
        tide_factor = 0.15

    temp_factor = 0
    water_temp = beach.get("water_temp")
    if water_temp is not None:
        if water_temp > 26:
            temp_factor = 0.2
        elif water_temp < 22:
            temp_factor = -0.1

    total_risk = max(0.0, min(1.0, base_risk + wind_factor + tide_factor + temp_factor))
    level = "BAJO" if total_risk < 0.25 else "MEDIO" if total_risk < 0.5 else "ALTO"

    return {
        "status": STATUS_OK,
        "risk_level": total_risk,
        "level": level,
        # El método no está validado con datos reales: no se declara confianza.
        "confidence": None,
        "nature": NATURE_PREDICTION,
        "method": METHOD_JELLYFISH,
        "validated": False,
        "factors": {
            "base_presence": base_risk,
            "wind_impact": wind_factor,
            "tide_impact": tide_factor,
            "temperature_impact": temp_factor,
        },
        "prediction": "PROBABLE" if total_risk > 0.4 else "IMPROBABLE",
        "recommendation": "EVITAR" if total_risk > 0.6 else "PRECAUCIÓN" if total_risk > 0.3 else "SEGURO",
        # Solo la especie documentada; ``None`` si no consta (no se asume ninguna).
        "expected_species": beach.get("jellyfish_species"),
    }


if __name__ == "__main__":
    test_beach = {
        "name": "Cala Major",
        "latitude": 39.56,
        "longitude": 2.62,
        "current_occupation": 45,
        "water_temp": 24.5,
        "flag_color": "green",
        "water_quality": "excellent",
        "jellyfish_present": False,
    }

    print("=== Estimación de ocupación (método no validado) ===")
    occ_pred = predict_occupation_advanced(test_beach)
    print(f"Predicción: {occ_pred['predicted']}% (Recomendación: {occ_pred['recommendation']})")
    print(f"Mejor momento: {occ_pred['best_time']}")

    print("\n=== Estimación de medusas (método no validado) ===")
    jelly_pred = predict_jellyfish_presence(test_beach)
    print(f"Riesgo: {jelly_pred['level']} ({jelly_pred['risk_level']:.2f})")
    print(f"Recomendación: {jelly_pred['recommendation']}")
