"""Meteorological data integration for SANDAM beaches"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import sys

sys.path.insert(0, 'C:/Users/JUAN/Desktop/Proyectos/SANDAM')

from src.integrations.aemet_client import AEMETClient


CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

MALLORCA_STATIONS = {
    "Palma Puerto": {"id": "B228", "lat": 39.57, "lon": 2.62},
    "Palma Aeropuerto": {"id": "B278", "lat": 39.55, "lon": 2.73},
    "Son Bonet": {"id": "B275E", "lat": 39.60, "lon": 2.70},
    "Andratx": {"id": "B103B", "lat": 39.55, "lon": 2.37},
    "Sóller": {"id": "B051A", "lat": 39.79, "lon": 2.42},
}


def get_cache_path(station_id: str) -> Path:
    return CACHE_DIR / f"weather_{station_id}.json"


def get_cached_weather(station_id: str, max_age_minutes: int = 30) -> Optional[Dict]:
    cache_path = get_cache_path(station_id)
    if not cache_path.exists():
        return None

    age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
    if age > timedelta(minutes=max_age_minutes):
        return None

    with open(cache_path, 'r') as f:
        return json.load(f)


def save_cached_weather(station_id: str, data: Dict) -> None:
    cache_path = get_cache_path(station_id)
    with open(cache_path, 'w') as f:
        json.dump(data, f)


def get_api_key() -> str:
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("AEMET_API_KEY="):
                    return line.split("=", 1)[1].strip()

    return os.environ.get("AEMET_API_KEY", "")


def fetch_weather_for_beach(beach_lat: float, beach_lon: float, api_key: str) -> Dict[str, Any]:
    nearest_station = None
    min_distance = float('inf')

    for name, station in MALLORCA_STATIONS.items():
        import math
        dist = math.sqrt((beach_lat - station["lat"])**2 + (beach_lon - station["lon"])**2)
        if dist < min_distance:
            min_distance = dist
            nearest_station = station

    if not nearest_station:
        return {"error": "No nearby station"}

    cached = get_cached_weather(nearest_station["id"])
    if cached:
        print(f"Using cached data for {nearest_station['id']}")
        return cached

    if not api_key:
        return {"error": "No API key available"}

    client = AEMETClient(api_key)

    try:
        import time
        time.sleep(2)
        obs = client.get_station_observation(nearest_station["id"])

        if obs and isinstance(obs, list) and len(obs) > 0:
            data = {
                "station": nearest_station.get("name", "Unknown"),
                "station_id": nearest_station["id"],
                "timestamp": datetime.now().isoformat(),
                "observation": obs[0] if obs else {}
            }
            save_cached_weather(nearest_station["id"], data)
            return data
        elif obs and isinstance(obs, dict):
            if "error" in obs:
                return obs
    except Exception as e:
        return {"error": str(e)}

    return {"error": "No data available"}

    return {"error": "No data available"}


def get_weather_for_all_beaches(beaches: List[Dict], api_key: str) -> List[Dict]:
    results = []

    for beach in beaches:
        weather = fetch_weather_for_beach(
            beach.get("latitude", 0),
            beach.get("longitude", 0),
            api_key
        )

        results.append({
            "beach": beach.get("name"),
            "weather": weather
        })

    return results


if __name__ == "__main__":
    api_key = get_api_key()

    if not api_key:
        print("No AEMET API key found in .env file")
        print("Add AEMET_API_KEY=your_key to .env")
        sys.exit(1)

    test_beaches = [
        {"name": "Platja de Palma", "latitude": 39.5345, "longitude": 2.7175},
        {"name": "Cala Major", "latitude": 39.5638, "longitude": 2.6272},
    ]

    print("Fetching weather for test beaches...")
    results = get_weather_for_all_beaches(test_beaches, api_key)

    for r in results:
        print(f"\n{r['beach']}:")
        if "error" in r["weather"]:
            print(f"  Error: {r['weather']['error']}")
        else:
            data = r["weather"].get("data", {})
            print(f"  Station: {r['weather'].get('station')}")
            print(f"  Data: {data}")