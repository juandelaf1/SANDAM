"""Prediction endpoints for SANDAM API"""

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.deps import get_db
from src.models import Beach
from src.utils.predictions import (
    predict_occupation_advanced,
    predict_jellyfish_presence,
    calculate_shade_availability,
    generate_forecast
)

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/occupation/{beach_name}")
async def predict_beach_occupation(
    beach_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Predict beach occupation for current time period"""
    result = await db.execute(select(Beach).where(Beach.name.ilike(f"%{beach_name}%")))
    beach = result.scalar_one_or_none()

    if not beach:
        return {"error": "Beach not found"}

    beach_dict = {
        "name": beach.name,
        "current_occupation": beach.current_occupation,
        "latitude": beach.latitude,
        "longitude": beach.longitude,
        "water_temp": beach.water_temp
    }

    prediction = predict_occupation_advanced(beach_dict)

    return {
        "beach": beach.name,
        "beach_id": str(beach.id),
        "current_occupation": beach.current_occupation,
        "predicted_occupation": prediction["predicted"],
        "confidence": prediction["confidence"],
        "recommendation": prediction["recommendation"],
        "best_time": prediction["best_time"],
        "factors": prediction["factors"],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/jellyfish/{beach_name}")
async def predict_jellyfish_risk(
    beach_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Predict jellyfish presence risk"""
    result = await db.execute(select(Beach).where(Beach.name.ilike(f"%{beach_name}%")))
    beach = result.scalar_one_or_none()

    if not beach:
        return {"error": "Beach not found"}

    beach_dict = {
        "name": beach.name,
        "jellyfish_present": beach.jellyfish_present,
        "jellyfish_species": beach.jellyfish_species,
        "water_temp": beach.water_temp,
        "flag_color": beach.flag_color
    }

    prediction = predict_jellyfish_presence(beach_dict)

    return {
        "beach": beach.name,
        "beach_id": str(beach.id),
        "risk_level": prediction["risk_level"],
        "level": prediction["level"],
        "confidence": prediction["confidence"],
        "prediction": prediction["prediction"],
        "recommendation": prediction["recommendation"],
        "expected_species": prediction["expected_species"],
        "factors": prediction["factors"],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/shade/{beach_name}")
async def get_shade_availability(
    beach_name: str,
    hour: int = Query(None, ge=0, le=23, description="Hour of day (0-23)"),
    db: AsyncSession = Depends(get_db)
):
    """Get natural shade availability for a beach"""
    result = await db.execute(select(Beach).where(Beach.name.ilike(f"%{beach_name}%")))
    beach = result.scalar_one_or_none()

    if not beach:
        return {"error": "Beach not found"}

    current_hour = hour if hour is not None else datetime.now().hour

    beach_dict = {
        "latitude": beach.latitude,
        "longitude": beach.longitude
    }

    shade_info = calculate_shade_availability(beach_dict, current_hour)

    return {
        "beach": beach.name,
        "beach_id": str(beach.id),
        "current_hour": current_hour,
        "has_natural_shade": shade_info["has_natural_shade"],
        "shade_type": shade_info["shade_type"],
        "shade_available_now": shade_info["shade_available_now"],
        "shade_hours": shade_info["shade_hours"],
        "recommendation": shade_info["recommendation"],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/forecast/{beach_name}")
async def get_beach_forecast(
    beach_name: str,
    days: int = Query(3, ge=1, le=7),
    db: AsyncSession = Depends(get_db)
):
    """Get forecast for next N days"""
    result = await db.execute(select(Beach).where(Beach.name.ilike(f"%{beach_name}%")))
    beach = result.scalar_one_or_none()

    if not beach:
        return {"error": "Beach not found"}

    beach_dict = {
        "name": beach.name,
        "water_temp": beach.water_temp,
        "latitude": beach.latitude,
        "longitude": beach.longitude
    }

    forecast = generate_forecast(beach_dict, days)

    return {
        "beach": beach.name,
        "beach_id": str(beach.id),
        "forecast": forecast,
        "generated_at": datetime.now().isoformat()
    }


@router.get("/ideal-score/{beach_name}")
async def get_ideal_score(
    beach_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Calculate 'Playa Ideal' score for a beach"""
    result = await db.execute(select(Beach).where(Beach.name.ilike(f"%{beach_name}%")))
    beach = result.scalar_one_or_none()

    if not beach:
        return {"error": "Beach not found"}

    beach_dict = {
        "name": beach.name or "",
        "current_occupation": beach.current_occupation or 50,
        "flag_color": beach.flag_color or "unknown",
        "water_quality": beach.water_quality or "unknown",
        "jellyfish_present": bool(beach.jellyfish_present) if beach.jellyfish_present is not None else False,
        "jellyfish_species": beach.jellyfish_species or "",
        "has_lifeguard": bool(beach.has_lifeguard) if beach.has_lifeguard is not None else False,
        "has_parking": bool(beach.has_parking) if beach.has_parking is not None else False,
        "has_accessibility": bool(beach.has_accessibility) if beach.has_accessibility is not None else False,
        "has_showers": bool(beach.has_showers) if beach.has_showers is not None else False,
        "has_shade": bool(beach.has_shade) if beach.has_shade is not None else False,
        "has_kiosk": bool(beach.has_kiosk) if beach.has_kiosk is not None else False
    }

    from src.utils.predictions import predict_occupation_advanced, predict_jellyfish_presence

    score_result = calculate_ideal_score(beach_dict)
    occ_pred = predict_occupation_advanced(beach_dict)
    jelly_pred = predict_jellyfish_presence(beach_dict)

    return {
        "beach": beach.name,
        "beach_id": str(beach.id),
        "score": score_result["score"],
        "rating": score_result["rating"],
        "factors": score_result["factors"],
        "prediction": {
            "occupation": occ_pred["predicted"],
            "recommendation": occ_pred["recommendation"]
        },
        "jellyfish": {
            "risk": jelly_pred["level"],
            "recommendation": jelly_pred["recommendation"]
        },
        "timestamp": datetime.now().isoformat()
    }


def calculate_ideal_score(beach: dict) -> dict:
    """Calculate the 'Playa Ideal' score"""
    score = 0
    factors = {}

    ocupacion = beach.get("current_occupation", 50)
    score_ocupacion = max(0, (100 - ocupacion) * 0.30)
    factors["ocupacion"] = {"score": round(score_ocupacion, 1), "max": 30}
    score += score_ocupacion

    flag = beach.get("flag_color", "unknown")
    if flag == "green":
        flag_score = 30
    elif flag == "yellow":
        flag_score = 15
    else:
        flag_score = 0
    factors["bandera"] = {"score": flag_score, "max": 30}
    score += flag_score

    risk_medusas = 0.1
    if beach.get("jellyfish_present"):
        risk_medusas = 0.7
    score_medusas = (1 - risk_medusas) * 20
    factors["medusas"] = {"score": round(score_medusas, 1), "max": 20}
    score += score_medusas

    quality = beach.get("water_quality", "unknown")
    if quality == "excellent":
        quality_score = 10
    elif quality == "good":
        quality_score = 7
    elif quality == "sufficient":
        quality_score = 4
    else:
        quality_score = 1
    factors["calidad"] = {"score": quality_score, "max": 10}
    score += quality_score

    sust_points = 0
    if beach.get("has_lifeguard"):
        sust_points += 0.4
    if beach.get("has_parking"):
        sust_points += 0.3
    if beach.get("has_accessibility"):
        sust_points += 0.3
    sust_score = sust_points * 10
    factors["sostenibilidad"] = {"score": round(sust_score, 1), "max": 10}
    score += sust_score

    return {
        "score": round(score, 1),
        "rating": "EXCELENTE" if score >= 80 else "BUENA" if score >= 60 else "REGULAR" if score >= 40 else "NO RECOMENDADA",
        "factors": factors
    }