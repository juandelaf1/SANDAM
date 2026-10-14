"""Weather endpoint for SANDAM API"""

import asyncio
import math
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.deps import get_db
from src.models import Beach

router = APIRouter(prefix="/weather", tags=["weather"])

MALLORCA_STATIONS = {
    "B228": {"name": "Palma Puerto", "lat": 39.554, "lon": 2.625},
    "B278": {"name": "Palma Aeropuerto", "lat": 39.552, "lon": 2.737},
    "B275E": {"name": "Son Bonet", "lat": 39.600, "lon": 2.707},
    "B103B": {"name": "Andratx - Sant Elm", "lat": 39.558, "lon": 2.222},
    "B051A": {"name": "Sóller Puerto", "lat": 39.793, "lon": 2.424},
}


def find_nearest_station(lat: float, lon: float) -> dict:
    """Find nearest weather station to given coordinates"""
    nearest = None
    min_dist = float('inf')

    for station_id, station in MALLORCA_STATIONS.items():
        dist = math.sqrt((lat - station["lat"])**2 + (lon - station["lon"])**2)
        if dist < min_dist:
            min_dist = dist
            nearest = {"id": station_id, **station}

    return nearest


async def get_weather_from_aemet(station_id: str) -> dict:
    """Get weather data from AEMET (cached or fresh)"""
    from src.integrations.weather_integration import get_cached_weather, fetch_weather_for_beach, get_api_key
    from src.integrations.aemet_client import AEMETClient

    cached = get_cached_weather(station_id, max_age_minutes=30)
    if cached:
        return cached

    api_key = get_api_key()
    if not api_key:
        return {"error": "No API key"}

    client = AEMETClient(api_key)

    station_info = MALLORCA_STATIONS.get(station_id, {})
    beach_data = {"latitude": station_info.get("lat", 39.5), "longitude": station_info.get("lon", 2.5)}

    try:
        import time
        time.sleep(1)
        obs = client.get_station_observation(station_id)
        if obs and isinstance(obs, list) and len(obs) > 0:
            data = {
                "station": station_info.get("name", station_id),
                "station_id": station_id,
                "timestamp": datetime.now().isoformat(),
                "observation": obs[0]
            }
            from src.integrations.weather_integration import save_cached_weather
            save_cached_weather(station_id, data)
            return data
    except Exception as e:
        return {"error": str(e)}

    return {"error": "No data available"}


@router.get("/beach/{beach_id}")
async def get_weather_for_beach(
    beach_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get weather data for a specific beach"""
    from sqlalchemy import select

    result = await db.execute(select(Beach).where(Beach.id == beach_id))
    beach = result.scalar_one_or_none()

    if not beach:
        return {"error": "Beach not found"}

    station = find_nearest_station(beach.latitude, beach.longitude)
    weather = await get_weather_from_aemet(station["id"])

    return {
        "beach": beach.name,
        "latitude": beach.latitude,
        "longitude": beach.longitude,
        "nearest_station": station["name"],
        "station_distance": "approximate",
        "weather": weather.get("observation", {}) if "error" not in weather else weather,
        "updated": weather.get("timestamp", datetime.now().isoformat())
    }


@router.get("/nearby")
async def get_weather_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
):
    """Get weather for nearest station to coordinates"""
    station = find_nearest_station(lat, lon)
    weather = await get_weather_from_aemet(station["id"])

    return {
        "requested_location": {"lat": lat, "lon": lon},
        "nearest_station": station["name"],
        "station_id": station["id"],
        "weather": weather.get("observation", {}) if "error" not in weather else weather,
        "updated": weather.get("timestamp", datetime.now().isoformat())
    }


@router.get("/stations")
async def get_stations():
    """Get list of available weather stations"""
    return {"stations": MALLORCA_STATIONS}