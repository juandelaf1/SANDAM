"""API Endpoint: Dónde Voy Ahora"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.deps import get_db
from src.models import Beach
from src.utils.recommendation_engine import (
    donde_ir_ahora,
    calcular_sol_restante,
    generar_recomendacion_completa,
    predecir_medusas,
)
from src.utils.scoring import calculate_overall_score


router = APIRouter(prefix="/donde-ir", tags=["donde-ir"])


def _beach_to_dict(beach: Beach) -> dict:
    return {
        "name": beach.name,
        "latitude": beach.latitude,
        "longitude": beach.longitude,
        "region": beach.region,
        "current_occupation": beach.current_occupation,
        "flag_color": beach.flag_color,
        "water_quality": beach.water_quality,
        "jellyfish_present": beach.jellyfish_present,
        "water_temp": beach.water_temp,
        "uv_index": beach.uv_index,
        "wave_height": beach.wave_height,
        "wind_speed": beach.wind_speed,
        "has_lifeguard": beach.has_lifeguard,
        "has_parking": beach.has_parking,
        "has_showers": beach.has_showers,
        "has_accessibility": beach.has_accessibility,
        "has_shade": beach.has_shade,
        "has_kiosk": beach.has_kiosk,
    }


@router.get("/ahora")
async def donde_ir_ahora_endpoint(
    lat: float = Query(..., ge=-90, le=90, description="Latitud del usuario (GPS)"),
    lon: float = Query(..., ge=-180, le=180, description="Longitud del usuario (GPS)"),
    incluir_marginales: bool = Query(False, description="Incluir playas marginales"),
    db: AsyncSession = Depends(get_db),
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
    result = await db.execute(select(Beach))
    playas_con_score = []
    for beach in result.scalars().all():
        playa = _beach_to_dict(beach)
        playa["score"] = calculate_overall_score(playa)
        playas_con_score.append(playa)

    recomendaciones = donde_ir_ahora(
        playas_con_score,
        lat,
        lon,
        incluye_marginales=incluir_marginales,
    )

    sol = calcular_sol_restante()

    # Estado global (FR-012): si no hay ninguna recomendacion elegible, se declara.
    if not playas_con_score:
        status = "insufficient_data"
    elif not recomendaciones:
        any_insufficient = any(p.get("score") is None for p in playas_con_score)
        status = "insufficient_data" if any_insufficient else "no_suitable_alternatives"
    elif recomendaciones:
        status = "ok"
    else:
        status = None

    return {
        "ubicacion_usuario": {"lat": lat, "lon": lon},
        "hora_actual": sol["hora_actual"],
        "atardecer": sol["hora_atardecer"],
        "sol_restante": f"{sol['horas_restantes']:.1f}h",
        "total_playas": len(playas_con_score),
        "recomendaciones": recomendaciones,
        "status": status,
        "travel_time_is_estimate": True,
    }


@router.get("/sol-restante")
async def sol_restante_endpoint():
    """Devuelve las horas de sol restantes hasta atardecer"""
    sol = calcular_sol_restante()
    return {
        "hora_actual": sol["hora_actual"],
        "hora_atardecer": sol["hora_atardecer"],
        "horas_restantes": round(sol["horas_restantes"], 1),
        "minutos_restantes": sol["minutos_restantes"],
    }


@router.get("/evaluar-playa/{playa_nombre}")
async def evaluar_playa_endpoint(
    playa_nombre: str,
    lat: float = Query(..., ge=-90, le=90, description="Tu latitud"),
    lon: float = Query(..., ge=-180, le=180, description="Tu longitud"),
    db: AsyncSession = Depends(get_db),
):
    """Evalúa si merece la pena ir a una playa específica"""
    result = await db.execute(
        select(Beach).where(Beach.name.ilike(f"%{playa_nombre}%")).limit(1)
    )
    beach = result.scalar_one_or_none()

    if not beach:
        return {"error": "Playa no encontrada"}

    playa = _beach_to_dict(beach)
    playa["score"] = calculate_overall_score(playa)

    return generar_recomendacion_completa(playa, lat, lon)


@router.get("/prediccion-medusas")
async def predecir_medusas_endpoint(
    viento: str = Query(None, description="Dirección viento (N, NE, E, SE, S, SW, W, NW)"),
    temperatura: float = Query(None, ge=0, le=40, description="Temperatura agua °C"),
    corrientes: str = Query(None, description="Dirección corrientes (norte/sur)"),
):
    """Predice riesgo de medusas basado en condiciones"""
    return predecir_medusas(viento, temperatura, corrientes)
