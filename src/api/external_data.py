"""Unified external data endpoint for SANDAM"""

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.deps import get_db
from src.models import Beach

router = APIRouter(prefix="/external", tags=["external_data"])

_MALLORCA_STATIONS = {
    "B228": {"name": "Palma Puerto", "lat": 39.554, "lon": 2.625},
    "B278": {"name": "Palma Aeropuerto", "lat": 39.552, "lon": 2.737},
    "B275E": {"name": "Son Bonet", "lat": 39.600, "lon": 2.707},
    "B103B": {"name": "Andratx", "lat": 39.558, "lon": 2.222},
    "B051A": {"name": "Soller", "lat": 39.793, "lon": 2.424},
}


def _find_nearest_station(lat: float, lon: float) -> dict:
    import math
    nearest = None
    min_dist = float('inf')
    for station_id, station in _MALLORCA_STATIONS.items():
        dist = math.sqrt((lat - station["lat"])**2 + (lon - station["lon"])**2)
        if dist < min_dist:
            min_dist = dist
            nearest = {"id": station_id, **station}
    return nearest


@router.get("/comprehensive/{beach_id}")
async def get_comprehensive_beach_data(
    beach_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive external data for a beach"""
    result = await db.execute(select(Beach).where(Beach.id == beach_id))
    beach = result.scalar_one_or_none()

    if not beach:
        return {"error": "Beach not found"}

    station = _find_nearest_station(beach.latitude, beach.longitude)

    return {
        "beach": {
            "id": str(beach.id),
            "name": beach.name,
            "location": {"lat": beach.latitude, "lon": beach.longitude}
        },
        "weather": {
            "station": station["name"],
            "station_id": station["id"],
            "data": {"note": "Use /weather/beach/{id} for real data"}
        },
        "ocean": {
            "note": "SOCIB integration - use /external/sources for info"
        },
        "air_quality": {
            "note": "Air quality data available via integration"
        },
        "data_sources": {
            "weather": "AEMET",
            "ocean": "SOCIB",
            "air_quality": "Xarxa de Vigilància",
            "catalog": "Govern Illes Balears"
        },
        "updated": datetime.now().isoformat()
    }


@router.get("/compare/{beach_id}")
async def compare_with_nearby(
    beach_id: str,
    radius_km: float = Query(15, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Compare beach with nearby alternatives"""
    try:
        result = await db.execute(select(Beach).where(Beach.id == beach_id))
        beach = result.scalar_one_or_none()

        if not beach:
            return {"error": "Beach not found"}

        result_all = await db.execute(select(Beach))
        all_beaches = result_all.scalars().all()
        current_beach_id = str(beach_id)

        import math
        nearby_beaches = []
        for b in all_beaches:
            beach_uuid = str(b.id)
            if len(beach_uuid) > 10 and len(current_beach_id) > 10 and beach_uuid[:8] == current_beach_id[:8]:
                continue
            dist = math.sqrt(
                (beach.latitude - b.latitude)**2 + 
                (beach.longitude - b.longitude)**2
            ) * 111
            if dist <= radius_km:
                nearby_beaches.append({
                    "beach": {"id": str(b.id), "name": b.name, "distance_km": round(dist, 2)},
                    "occupation": b.current_occupation,
                    "flag_color": b.flag_color,
                    "water_quality": b.water_quality
                })

        nearby_beaches.sort(key=lambda x: x["distance_km"])

        return {
            "current_beach": {
                "name": beach.name,
                "occupation": beach.current_occupation,
                "flag_color": beach.flag_color,
                "water_quality": beach.water_quality
            },
            "nearby_alternatives": nearby_beaches[:10]
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/sources")
async def get_data_sources():
    """Get list of all available data sources"""
    return {
        "sources": [
            {
                "name": "AEMET",
                "type": "meteorology",
                "data": ["temperature", "humidity", "wind", "pressure"],
                "status": "active"
            },
            {
                "name": "SOCIB",
                "type": "oceanography",
                "data": ["wave_height", "wave_period", "currents", "temperature"],
                "status": "partial"
            },
            {
                "name": "Govern Illes Balears",
                "type": "catalog",
                "data": ["beach_info", "services", "location"],
                "status": "active"
            },
            {
                "name": "Xarxa de Vigilància Qualitat de l'Aire",
                "type": "air_quality",
                "data": ["AQI", "PM25", "PM10", "O3"],
                "status": "active"
            },
            {
                "name": "112 Baleares",
                "type": "alerts",
                "data": ["emergency_alerts"],
                "status": "active"
            }
        ],
        "note": "Some data sources use mock data when API is unavailable"
    }