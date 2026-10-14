"""SOCIB Client - Working with Real Data"""

import requests
from typing import Optional, Dict, List
from datetime import datetime
import json
from pathlib import Path
import math


CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

SOCIB_API_KEY = "fg1XJ43jxjkQ83o36VFcchho26I869v5"


class SOCIBClient:
    """SOCIB - REAL DATA from API"""

    BASE_URL = "https://api.socib.es"

    PLATFORMS = {
        "palma": {"id": "mooring:palma", "name": "Palma Bay Buoy", "lat": 39.53, "lon": 2.65},
        "mahon": {"id": "mooring:mahon", "name": "Mahon Buoy", "lat": 39.87, "lon": 3.72},
        "ibiza": {"id": "mooring:ibiza", "name": "Ibiza Buoy", "lat": 38.91, "lon": 1.43},
        "dragonera": {"id": "mooring:dragonera", "name": "Dragonera Buoy", "lat": 39.78, "lon": 2.32},
    }

    def __init__(self, api_key: str = None):
        self.api_key = api_key or SOCIB_API_KEY

    def _get_data(self, **params) -> Optional[Dict]:
        """Get data - key as query param, Accept: */*"""
        params["api_key"] = self.api_key
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/entries", 
                params=params, 
                headers={"Accept": "*/*"},
                timeout=20
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"SOCIB {response.status_code}")
        except Exception as e:
            print(f"SOCIB error: {e}")
        return None

    def get_value(self, platform_id: str, variable: str) -> Optional[float]:
        """Get latest value for variable"""
        data = self._get_data(
            data_source=platform_id,
            data_mode="real-time",
            standard_variable=variable,
            limit=1
        )
        
        if data and data.get("results"):
            return data["results"][0].get("value")
        return None

    def get_buoy_data(self, station_id: str = "mooring:palma") -> Dict:
        """Get buoy data"""
        result = {"station": station_id, "timestamp": datetime.now().isoformat(), "data": {}, "source": "socib"}
        
        vars_map = {
            "sea_water_temperature": "water_temp",
            "air_temperature": "air_temp", 
            "wind_speed": "wind_speed",
            "sea_surface_wave_significant_height": "wave_height",
            "sea_surface_wave_period": "wave_period",
        }
        
        for socib_var, local_name in vars_map.items():
            result["data"][local_name] = self.get_value(station_id, socib_var)
        
        if not any(v is not None for v in result["data"].values()):
            result["source"] = "no_data"
        
        return result

    def get_all_buoys(self) -> List[Dict]:
        """Get all buoys"""
        results = []
        for name, info in self.PLATFORMS.items():
            data = self.get_buoy_data(info["id"])
            results.append({
                "station": info["name"],
                "station_id": info["id"],
                "location": {"lat": info["lat"], "lon": info["lon"]},
                "data": data.get("data", {}),
                "source": data.get("source")
            })
        return results


if __name__ == "__main__":
    print("=" * 50)
    print("SOCIB - REAL DATA")
    print("=" * 50)
    
    client = SOCIBClient()
    buoys = client.get_all_buoys()
    
    for buoy in buoys:
        print(f"\n{buoy['station']} ({buoy['source']}):")
        for k, v in buoy['data'].items():
            print(f"  {k}: {v}")