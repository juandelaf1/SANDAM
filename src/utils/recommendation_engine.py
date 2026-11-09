'''SANDAM 2026 - Motor de Recomendaciones Inteligentes

Contiene:
1. Algoritmo "Donde voy ahora" (GPS + tiempo + sol) - dos etapas (T012/T013)
2. Prediccion medusas basada en reglas
3. Score Playa Ideal mejorado con distancia
4. Calculo de atardecer por fecha/ubicacion
5. Explicaciones estructuradas (FR-006, T017)
'''

from datetime import datetime, timedelta
from typing import List, Dict

from src.utils.distance import haversine_distance
from src.utils.eligibility import evaluate_eligibility
from src.utils.scoring import relative_pressure


# Constantes Mallorca
LATITUD_MALLORCA = 39.5
LONGITUD_MALLORCA = 2.9

# Factor tiempo viaje Mallorca (minutos por km)
FACTOR_CARRETERA = {
    "autopista": 1.0,
    "comarcal": 1.3,
    "montana": 1.5,
}

# Horas aproximadas atardecer Mallorca (mes a mes)
ATARDECER_MALLORCA = {
    1: 17, 2: 18, 3: 18, 4: 19, 5: 20, 6: 21,
    7: 21, 8: 20, 9: 19, 10: 18, 11: 17, 12: 17,
}


def obtener_hora_atardecer(mes: int = None) -> datetime:
    '''Obtiene la hora aproximada de atardecer en Mallorca'''
    if mes is None:
        mes = datetime.now().month

    hora_atardecer = ATARDECER_MALLORCA.get(mes, 20)
    hora_minutos = {
        17: (17, 30), 18: (18, 0), 19: (19, 30), 20: (20, 30), 21: (21, 0),
    }
    h, m = hora_minutos.get(hora_atardecer, (20, 30))
    hoy = datetime.now()

    return hoy.replace(hour=h, minute=m, second=0, microsecond=0)


def calcular_tiempo_viaje(distancia_km: float, tipo_carretera: str = "comarcal") -> int:
    '''Calcula tiempo de viaje estimado en minutos'''
    factor = FACTOR_CARRETERA.get(tipo_carretera, 1.3)
    return int((distancia_km / 60) * factor * 60)


def determinar_tipo_carretera(distancia_km: float) -> str:
    '''Determina el tipo de carretera basado en distancia'''
    if distancia_km < 20:
        return "autopista"
    elif distancia_km < 50:
        return "comarcal"
    else:
        return "montana"


def predecir_medusas(viento_direccion: str = None, temperatura_agua: float = None,
                     corrientes: str = None) -> Dict:
    '''Predice riesgo de medusas basado en reglas'''
    riesgo = "BAJO"
    nivel = 0
    factores = []

    if viento_direccion:
        viento_upper = viento_direccion.upper()
        if "NE" in viento_upper:
            riesgo = "ALTO"
            nivel += 3
            factores.append("Viento {} arrastra medusas".format(viento_direccion))
        elif "SW" in viento_upper or "W" in viento_upper:
            riesgo = "BAJO"
            nivel -= 1
            factores.append("Viento {} aleja medusas".format(viento_direccion))

    if temperatura_agua and temperatura_agua > 24:
        nivel += 2
        factores.append("Temp agua {}C favorable".format(temperatura_agua))

    if corrientes and corrientes.lower() == "sur":
        nivel += 2
        factores.append("Corrientes desde sur traen medusas")

    if nivel >= 3:
        riesgo = "ALTO"
    elif nivel >= 1:
        riesgo = "MEDIO"
    else:
        riesgo = "BAJO"

    return {
        "nivel": nivel,
        "riesgo": riesgo,
        "factores": factores,
        "recomendacion": "Evitar baño" if riesgo == "ALTO" else "Precaución" if riesgo == "MEDIO" else "Seguro",
    }


def calcular_sol_restante() -> Dict:
    '''Calcula horas de sol restantes hasta atardecer'''
    ahora = datetime.now()
    atardecer = obtener_hora_atardecer()

    diferencia = atardecer - ahora
    horas = diferencia.total_seconds() / 3600

    return {
        "hora_actual": ahora.strftime("%H:%M"),
        "hora_atardecer": atardecer.strftime("%H:%M"),
        "horas_restantes": max(0, horas),
        "minutos_restantes": max(0, int(diferencia.total_seconds() / 60)),
    }


def generar_explicacion(playa: Dict, status: str, sol_restante_min: int,
                       distancia: float, score: float) -> Dict:
    '''Genera una explicacion estructurada (reason + factors) para una recomendacion (FR-006).

    No inventa datos: los factores se derivan de los valores documentados de la playa.
    '''
    factors = []

    quality = playa.get("water_quality")
    if quality is not None:
        factors.append("calidad del agua: {}".format(quality))

    wave = playa.get("wave_height")
    if wave is not None:
        factors.append("oleaje: {}m".format(wave))

    uv = playa.get("uv_index")
    if uv is not None:
        factors.append("UV: {}".format(uv))

    factors.append("distancia: {:.1f} km".format(distancia))

    occupation = playa.get("current_occupation")
    if occupation is not None:
        factors.append("ocupacion documentada: {}%".format(occupation))

    if playa.get("has_lifeguard"):
        factors.append("socorrista presente")

    if status == "recomendada":
        reason = "Playa recomendada: condiciones favorables y tiempo de viaje adecuado para el sol restante."
    elif status == "marginal":
        reason = "Playa marginal: tiempo de viaje ajustado al sol restante."
    else:
        reason = "Playa no merece la pena: tiempo de viaje superior al sol restante."

    return {"reason": reason, "factors": factors}


def donde_ir_ahora(playas: List[Dict], lat_usuario: float, lon_usuario: float,
                  incluye_marginales: bool = False) -> List[Dict]:
    '''ALGORITMO PRINCIPAL: Donde voy ahora (dos etapas, T012/T013).

    Etapa 1 - Elegibilidad (FR-001, FR-002): cada playa se clasifica como
    elegible o no elegible ANTES de compararla. Las condiciones de exclusion
    (seguridad, restricciones oficiales, datos insuficientes) son NO
    compensables: ningun factor de comodidad las neutraliza. Las playas no
    elegibles no se proponen como alternativas.

    Etapa 2 - Comparacion: solo entre elegibles, orden por score canonico
    (calidad/oleaje/UV) ajustado por distancia (confort, no exclusion). La baja
    ocupacion NO es un merito: se expone solo como indicador de presion
    relativa etiquetado (FR-007, FR-014).
    '''
    sol = calcular_sol_restante()
    sol_restante_min = sol["minutos_restantes"]
    buffer_min = 60

    recomendaciones = []

    for playa in playas:
        # --- Etapa 1: elegibilidad (FR-001) ---
        elig = evaluate_eligibility(playa)
        if not elig.eligible:
            continue

        # Score canonico (T006). None = desconocido: no se ordena ni se recomienda.
        score = playa.get("score")
        if score is None:
            continue

        distancia = haversine_distance(
            lat_usuario, lon_usuario,
            playa.get("latitude", 0),
            playa.get("longitude", 0),
        )

        tipo_carretera = determinar_tipo_carretera(distancia)
        tiempo_viaje = calcular_tiempo_viaje(distancia, tipo_carretera)

        if tiempo_viaje < (sol_restante_min - buffer_min):
            status = "recomendada"
            color = "verde"
        elif tiempo_viaje < sol_restante_min:
            status = "marginal"
            color = "amarillo"
        else:
            status = "no_merece"
            color = "rojo"

        factor_distancia = max(0.5, 1 - (distancia / 100))
        score_final = score * factor_distancia

        hora_llegada = datetime.now() + timedelta(minutes=tiempo_viaje)

        # Calidad del dato (FR-004/FR-015, T021, Modo B spec 003) - etiquetado minimo
        _occ_status = playa.get("occupancy_status")
        # Modo B: sin estado verificado, no afirmar "observation"; enum contrato usa "estimate"
        _occ_nature = "unknown" if playa.get("current_occupation") is None else (_occ_status or "estimate")

        recomendaciones.append({
            "nombre": playa.get("name"),
            "latitude": playa.get("latitude"),
            "longitude": playa.get("longitude"),
            "distancia_km": round(distancia, 1),
            "tiempo_viaje_min": tiempo_viaje,
            "hora_llegada": hora_llegada.strftime("%H:%M"),
            "score_original": score,
            "score_final": round(score_final, 1),
            "status": status,
            "color": color,
            "sol_restante_min": sol_restante_min,
            "flags": {
                "playa": playa.get("flag_color"),
                "calidad": playa.get("water_quality"),
                "ocupacion": playa.get("current_occupation"),
                "medusas": playa.get("jellyfish_present"),
                "servicios": {
                    "socorrista": playa.get("has_lifeguard"),
                    "parking": playa.get("has_parking"),
                    "duchas": playa.get("has_showers"),
                    "accesible": playa.get("has_accessibility"),
                },
            },
            # Aditivos (T005/T014)
            "eligible": elig.eligible,
            "eligibility_conditions": [
                {"type": c.type, "reason": c.reason, "source": c.source}
                for c in elig.conditions
            ],
            "pressure_relative": relative_pressure(playa.get("current_occupation")),
            "travel_time_is_estimate": True,
            # Explicacion estructurada (FR-006, T017/T018)
            "explanation": generar_explicacion(playa, status, sol_restante_min, distancia, score),
            "data_quality": {
                "water_quality": {"nature": "unknown" if playa.get("water_quality") is None else "observation", "source": None},
                "sea_state": {"nature": "unknown" if playa.get("wave_height") is None else "observation", "source": None},
                "solar_exposure": {"nature": "unknown" if playa.get("uv_index") is None else "observation", "source": None},
                "occupation": {"nature": _occ_nature, "source": None},
            },
        })

    if not incluye_marginales:
        recomendaciones = [r for r in recomendaciones if r["status"] != "no_merece"]

    return sorted(recomendaciones, key=lambda x: x["score_final"], reverse=True)


def generar_recomendacion_completa(playa: Dict, lat_usuario: float, lon_usuario: float) -> Dict:
    '''Genera recomendacion completa para una playa especifica'''

    distancia = haversine_distance(
        lat_usuario, lon_usuario,
        playa.get("latitude", 0),
        playa.get("longitude", 0),
    )

    tipo_carretera = determinar_tipo_carretera(distancia)
    tiempo_viaje = calcular_tiempo_viaje(distancia, tipo_carretera)
    sol = calcular_sol_restante()

    medusas = predecir_medusas(
        viento_direccion=playa.get("wind_direction"),
        temperatura_agua=playa.get("water_temp"),
        corrientes=playa.get("current_direction"),
    )

    merece_ir = tiempo_viaje < (sol["minutos_restantes"] - 60)

    mensaje = ""
    if not merece_ir:
        mensaje = "Te quedan {}min de sol. El viaje dura {}min + tiempo en playa. Considera una playa mas cercana.".format(
            sol["minutos_restantes"], tiempo_viaje,
        )

    return {
        "playa": playa.get("name"),
        "distancia": "{} km".format(distancia),
        "tiempo_viaje": "{} min".format(tiempo_viaje),
        "llegada": "{} + {}min = {}".format(
            datetime.now().strftime("%H:%M"), tiempo_viaje,
            (datetime.now() + timedelta(minutes=tiempo_viaje)).strftime("%H:%M"),
        ),
        "score": playa.get("score", 0),
        "sol_restante": "{}h ({}min)".format(sol["horas_restantes"], sol["minutos_restantes"]),
        "merrece_ir": merece_ir,
        "mensaje": mensaje,
        "medusas": medusas,
        "flags": {
            "playa": playa.get("flag_color"),
            "calidad": playa.get("water_quality"),
            "ocupacion": "{}%".format(playa.get("current_occupation", 0)),
        },
    }


if __name__ == "__main__":
    print("=" * 60)
    print("SANDAM - Algoritmo Donde Voy Ahora")
    print("=" * 60)

    sol = calcular_sol_restante()
    print("Sol restante: {:.1f}h".format(sol["horas_restantes"]))
    print("Atardecer: {}".format(sol["hora_atardecer"]))

    test_medusas = predecir_medusas("NE", 26.0, "sur")
    print("Viento NE + 26C + corrientes sur: {}".format(test_medusas))

    test_medusas2 = predecir_medusas("SW", 22.0, None)
    print("Viento SW + 22C: {}".format(test_medusas2))

    for dist in [5, 15, 30, 60]:
        tipo = determinar_tipo_carretera(dist)
        tiempo = calcular_tiempo_viaje(dist, tipo)
        print("{}km ({}): {}min".format(dist, tipo, tiempo))

    print("=" * 60)