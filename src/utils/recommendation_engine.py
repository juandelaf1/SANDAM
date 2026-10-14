"""SANDAM 2026 - Motor de Recomendaciones Inteligentes

Contiene:
1. Algoritmo "Dónde voy ahora" (GPS + tiempo + sol)
2. Predicción medusas basada en reglas
3. Score Playa Ideal mejorado con distancia
4. Cálculo de atardecer por fecha/ubicación
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math
from src.utils.distance import haversine_distance


# Constantes Mallorca
LATITUD_MALLORCA = 39.5
LONGITUD_MALLORCA = 2.9

# Factor tiempo viaje Mallorca (minutos por km)
# Carretera montaña = 1.5x, comarcal = 1.3x, autopistas = 1.0x
FACTOR_CARRETERA = {
    "autopista": 1.0,
    "comarcal": 1.3,
    "montaña": 1.5
}

# Horas aproximadas atardecer Mallorca (mes a mes)
ATARDECER_MALLORCA = {
    1: 17, 2: 18, 3: 18, 4: 19, 5: 20, 6: 21,
    7: 21, 8: 20, 9: 19, 10: 18, 11: 17, 12: 17
}


def obtener_hora_atardecer(mes: int = None) -> datetime:
    """Obtiene la hora aproximada de atardecer en Mallorca"""
    if mes is None:
        mes = datetime.now().month
    
    hora_atardecer = ATARDECER_MALLORCA.get(mes, 20)
    hora_minutos = {
        17: (17, 30), 18: (18, 0), 19: (19, 30), 20: (20, 30), 21: (21, 0)
    }
    h, m = hora_minutos.get(hora_atardecer, (20, 30))
    hoy = datetime.now()
    
    return hoy.replace(hour=h, minute=m, second=0, microsecond=0)


def calcular_tiempo_viaje(distancia_km: float, tipo_carretera: str = "comarcal") -> int:
    """Calcula tiempo de viaje estimado en minutos"""
    factor = FACTOR_CARRETERA.get(tipo_carretera, 1.3)
    # Asumiendo velocidad promedio 60km/h en Mallorca
    return int((distancia_km / 60) * factor * 60)


def determinar_tipo_carretera(distancia_km: float) -> str:
    """Determina el tipo de carretera basado en distancia"""
    if distancia_km < 20:
        return "autopista"
    elif distancia_km < 50:
        return "comarcal"
    else:
        return "montaña"


def predecir_medusas(viento_direccion: str = None, temperatura_agua: float = None, 
                    corrientes: str = None) -> Dict:
    """
    Predice riesgo de medusas basado en reglas:
    - Viento NE + temp > 24°C = riesgo ALTO
    - Corrientes desde sur = riesgo ALTO  
    - Viento SW = riesgo BAJO (mar hacia tierra)
    """
    riesgo = "BAJO"
    nivel = 0
    factores = []
    
    # Factor viento
    if viento_direccion:
        viento_upper = viento_direccion.upper()
        if "NE" in viento_upper or "N" in viento_upper and "E" in viento_upper:
            riesgo = "ALTO"
            nivel += 3
            factores.append(f"Viento {viento_direccion} arrastra medusas")
        elif "SW" in viento_upper or "W" in viento_upper:
            riesgo = "BAJO"
            nivel -= 1
            factores.append(f"Viento {viento_direccion} aleja medusas")
    
    # Factor temperatura
    if temperatura_agua and temperatura_agua > 24:
        nivel += 2
        factores.append(f"Temp agua {temperatura_agua}°C favorable")
    
    # Factor corrientes
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
        "recomendacion": "Evitar baño" if riesgo == "ALTO" else "Precaución" if riesgo == "MEDIO" else "Seguro"
    }


def calcular_sol_restante() -> Dict:
    """Calcula horas de sol restantes hasta atardecer"""
    ahora = datetime.now()
    atardecer = obtener_hora_atardecer()
    
    diferencia = atardecer - ahora
    horas = diferencia.total_seconds() / 3600
    
    return {
        "hora_actual": ahora.strftime("%H:%M"),
        "hora_atardecer": atardecer.strftime("%H:%M"),
        "horas_restantes": max(0, horas),
        "minutos_restantes": max(0, int(diferencia.total_seconds() / 60))
    }


def donde_ir_ahora(playas: List[Dict], lat_usuario: float, lon_usuario: float,
                 incluye_marginales: bool = False) -> List[Dict]:
    """
    ALGORITMO PRINCIPAL: Dónde voy ahora
    
    Recibe lista de playas con sus datos y recomienda según:
    1. Distancia desde posición GPS del usuario
    2. Tiempo de viaje estimado
    3. Horas de sol restantes
    4. Score de la playa
    
    Retorna lista filtrada y ordenada
    """
    
    sol = calcular_sol_restante()
    sol_restante_min = sol["minutos_restantes"]
    buffer_min = 60  # 1 hora de buffer
    
    recomendaciones = []
    
    for playa in playas:
        # Calcular distancia
        distancia = haversine_distance(
            lat_usuario, lon_usuario,
            playa.get("latitude", 0), 
            playa.get("longitude", 0)
        )
        
        # Calcular tiempo de viaje
        tipo_carretera = determinar_tipo_carretera(distancia)
        tiempo_viaje = calcular_tiempo_viaje(distancia, tipo_carretera)
        
        # Score de la playa
        score = playa.get("score", 50)
        
        # Determinar status
        if tiempo_viaje < (sol_restante_min - buffer_min):
            status = "recomendada"
            color = "verde"
        elif tiempo_viaje < sol_restante_min:
            status = "marginal"
            color = "amarillo"
        else:
            status = "no_merece"
            color = "rojo"
        
        # Calcular score final (prioriza cercanía + calidad)
        factor_distancia = max(0.5, 1 - (distancia / 100))  # Menos distancia = más bonus
        score_final = score * factor_distancia
        
        hora_llegada = datetime.now() + timedelta(minutes=tiempo_viaje)
        
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
                    "accesible": playa.get("has_accessibility")
                }
            }
        })
    
    # Filtrar según preference
    if not incluye_marginales:
        recomendaciones = [r for r in recomendaciones if r["status"] != "no_merece"]
    
    # Ordenar por score_final descendente
    return sorted(recomendaciones, key=lambda x: x["score_final"], reverse=True)


def generar_recomendacion_completa(playa: Dict, lat_usuario: float, lon_usuario: float) -> Dict:
    """Genera recomendación completa para una playa específica"""
    
    distancia = haversine_distance(
        lat_usuario, lon_usuario,
        playa.get("latitude", 0), 
        playa.get("longitude", 0)
    )
    
    tipo_carretera = determinar_tipo_carretera(distancia)
    tiempo_viaje = calcular_tiempo_viaje(distancia, tipo_carretera)
    sol = calcular_sol_restante()
    
    # Predicción medusas
    medusas = predecir_medusas(
        viento_direccion=playa.get("wind_direction"),
        temperatura_agua=playa.get("water_temp"),
        corrientes=playa.get("current_direction")
    )
    
    # Evaluación general
    merece_ir = tiempo_viaje < (sol["minutos_restantes"] - 60)
    
    mensaje = ""
    if not merece_ir:
        mensaje = f"Te quedan {sol['minutos_restantes']}min de sol. El viaje dura {tiempo_viaje}min + tiempo en playa. Considera una playa más cercana."
    
    return {
        "playa": playa.get("name"),
        "distancia": f"{distancia:.1f} km",
        "tiempo_viaje": f"{tiempo_viaje} min",
        "llegada": f"{datetime.now().strftime('%H:%M')} + {tiempo_viaje}min = {(datetime.now() + timedelta(minutes=tiempo_viaje)).strftime('%H:%M')}",
        "score": playa.get("score", 0),
        "sol_restante": f"{sol['horas_restantes']:.1f}h ({sol['minutos_restantes']}min)",
        "merrece_ir": merece_ir,
        "mensaje": mensaje,
        "medusas": medusas,
        "flags": {
            "playa": playa.get("flag_color"),
            "calidad": playa.get("water_quality"),
            "ocupacion": f"{playa.get('current_occupation', 0)}%"
        }
    }


# Testing
if __name__ == "__main__":
    print("=" * 60)
    print("SANDAM - Algoritmo Dónde Voy Ahora")
    print("=" * 60)
    
    # Test sol restante
    sol = calcular_sol_restante()
    print(f"\nSol restante: {sol['horas_restantes']:.1f}h")
    print(f"Atardecer: {sol['hora_atardecer']}")
    
    # Test predicción medusas
    print("\n--- Predicción Medusas ---")
    test_medusas = predecir_medusas("NE", 26.0, "sur")
    print(f"Viento NE + 26°C + corrientes sur: {test_medusas}")
    
    test_medusas2 = predecir_medusas("SW", 22.0, None)
    print(f"Viento SW + 22°C: {test_medusas2}")
    
    # Test tiempo viaje
    print("\n--- Tiempos de viaje ---")
    for dist in [5, 15, 30, 60]:
        tipo = determinar_tipo_carretera(dist)
        tiempo = calcular_tiempo_viaje(dist, tipo)
        print(f"{dist}km ({tipo}): {tiempo}min")
    
    print("\n" + "=" * 60)