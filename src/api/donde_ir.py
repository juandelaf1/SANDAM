"""API Endpoint: Dónde Voy Ahora"""

from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

from src.deps import get_db
from src.models import Beach
from sqlalchemy import select
from src.utils.recommendation_engine import (
    donde_ir_ahora,
    calcular_sol_restante,
    generar_recomendacion_completa,
    predecir_medusas
)


router = APIRouter(prefix="/donde-ir", tags=["donde-ir"])


@router.get("/ahora")
async def donde_ir_ahora_endpoint(
    lat: float = Query(..., description="Latitud del usuario (GPS)"),
    lon: float = Query(..., description="Longitud del usuario (GPS)"),
    incluir_marginales: bool = Query(False, description="Incluir playas marginales"),
    db = None
):
    """
    🚀 ALGORITMO PRINCIPAL: Dónde voy ahora
    
    Dado tu ubicación GPS y la hora actual, te dice:
    - Qué playas están a tiempo de llegar
    - Cuánto tiempo de viaje
    - Cuándo llegas
    - Si merece la pena (teniendo en cuenta el sol que queda)
    
    Returns: Lista de recomendaciones ordenadas por meritocracia
    """
    # Obtener todas las playas
    # (En producción, usar db. Aquí usamos datos en memoria)
    from src.utils.geopandas_processor import BEACH_DATA
    
    # Añadir score a cada playa
    playas_con_score = []
    for b in BEACH_DATA:
        score = calcular_score_playa(b)
        b["score"] = score
        b["latitude"] = b.get("lat", b.get("latitude"))
        b["longitude"] = b.get("lon", b.get("longitude"))
        playas_con_score.append(b)
    
    # Ejecutar algoritmo
    recomendaciones = donde_ir_ahora(
        playas_con_score,
        lat,
        lon,
        incluye_marginales=incluir_marginales
    )
    
    # Añadir info sol
    sol = calcular_sol_restante()
    
    return {
        "ubicacion_usuario": {"lat": lat, "lon": lon},
        "hora_actual": sol["hora_actual"],
        "atardecer": sol["hora_atardecer"],
        "sol_restante": f"{sol['horas_restantes']:.1f}h",
        "total_playas": len(playas_con_score),
        "recomendaciones": recomendaciones
    }


@router.get("/sol-restante")
async def sol_restante_endpoint():
    """Devuelve las horas de sol restantes hasta atardecer"""
    sol = calcular_sol_restante()
    return {
        "hora_actual": sol["hora_actual"],
        "hora_atardecer": sol["hora_atardecer"],
        "horas_restantes": round(sol["horas_restantes"], 1),
        "minutos_restantes": sol["minutos_restantes"]
    }


@router.get("/evaluar-playa/{playa_nombre}")
async def evaluar_playa_endpoint(
    playa_nombre: str,
    lat: float = Query(..., description="Tu latitud"),
    lon: float = Query(..., description="Tu longitud")
):
    """Evalúa si merece la pena ir a una playa específica"""
    from src.utils.geopandas_processor import BEACH_DATA
    
    # Buscar playa
    playa = None
    for b in BEACH_DATA:
        if playa_nombre.lower() in b.get("name", "").lower():
            playa = b
            break
    
    if not playa:
        return {"error": "Playa no encontrada"}
    
    score = calcular_score_playa(playa)
    playa["score"] = score
    
    evaluacion = generar_recomendacion_completa(playa, lat, lon)
    
    return evaluacion


@router.get("/prediccion-medusas")
async def predecir_medusas_endpoint(
    viento: str = Query(None, description="Dirección viento (N, NE, E, SE, S, SW, W, NW)"),
    temperatura: float = Query(None, ge=0, le=40, description="Temperatura agua °C"),
    corrientes: str = Query(None, description="Dirección corrientes (norte/sur)")
):
    """Predice riesgo de medusas basado en condiciones"""
    prediccion = predecir_medusas(viento, temperatura, corrientes)
    return prediccion


def calcular_score_playa(beach: dict) -> float:
    """Calcula score 0-100 para una playa"""
    score = 0
    
    # Ocupación (30%)
    ocupacion = beach.get("current_occupation", 50)
    score_ocupacion = max(0, (100 - ocupacion) * 0.30)
    score += score_ocupacion
    
    # Bandera (30%)
    flag = beach.get("flag_color", "unknown")
    if flag == "green":
        score += 30
    elif flag == "yellow":
        score += 15
    
    # Medusas (20%)
    if not beach.get("jellyfish_present", False):
        score += 20
    
    # Calidad agua (10%)
    calidad = beach.get("water_quality", "unknown")
    if calidad == "excellent":
        score += 10
    elif calidad == "good":
        score += 7
    
    # Servicios (10%)
    servicios = 0
    if beach.get("has_lifeguard"): servicios += 2
    if beach.get("has_parking"): servicios += 2
    if beach.get("has_showers"): servicios += 2
    if beach.get("has_accessibility"): servicios += 2
    if beach.get("has_shade"): servicios += 2
    score += servicios
    
    return round(score, 1)