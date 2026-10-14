"""CAIB Open Data - Enhanced with Real Data"""

import requests
from typing import Optional, Dict, List
from datetime import datetime
import json
from pathlib import Path
import math


CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class CAIBOpenDataClient:
    """Client for CAIB (Govern Illes Balears) Open Data - REAL DATA"""
    
    BASE_URL = "https://intranet.caib.es/opendatacataleg/api/3/action"
    
    def search_datasets(self, query: str) -> List[Dict]:
        """Search datasets in CAIB catalog"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/package_search",
                params={"q": query},
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("result", {}).get("results", [])
        except Exception as e:
            print(f"CAIB search error: {e}")
        return []

    def get_beach_climate_data(self) -> Optional[Dict]:
        """Get REAL maritime climate data for beaches"""
        cache_path = CACHE_DIR / "caib_beach_climate.json"
        
        if cache_path.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if age.total_seconds() < 86400 * 7:
                with open(cache_path, 'r') as f:
                    return json.load(f)
        
        datasets = self.search_datasets("clima marítim platges")
        
        for ds in datasets:
            if "resources" in ds:
                for res in ds["resources"]:
                    if res.get("format") == "GeoJSON":
                        try:
                            geo_response = requests.get(res["url"], timeout=30)
                            if geo_response.status_code == 200:
                                geo_data = geo_response.json()
                                with open(cache_path, 'w') as f:
                                    json.dump(geo_data, f)
                                return geo_data
                        except Exception as e:
                            print(f"Error fetching climate GeoJSON: {e}")
        
        return None

    def get_beach_climate_for_location(self, lat: float, lon: float) -> Dict:
        """Get climate data for nearest beach location"""
        data = self.get_beach_climate_data()
        
        if not data:
            return {}
        
        features = data.get("features", [])
        
        min_dist = float('inf')
        nearest = None
        
        for feat in features:
            props = feat.get("properties", {})
            x = props.get("XUTM", 0)
            y = props.get("YUTM", 0)
            
            lat_utm = y / 100000
            lon_utm = x / 100000
            
            dist = math.sqrt((lat_utm - lat)**2 + (lon_utm - lon)**2)
            
            if dist < min_dist:
                min_dist = dist
                nearest = props
        
        if nearest:
            return {
                "name": nearest.get("NAME", "Unknown"),
                "wave_height_mean": nearest.get("HS_MITJANA"),
                "wave_height_100yr": nearest.get("HSRP100"),
                "surge_mean": nearest.get("SURGE_MEAN"),
                "tide_mean": nearest.get("MAREA_MEAN"),
                "setup_mean": nearest.get("SETUP_MEAN"),
                "source": "CAIB_OpenData"
            }
        
        return {}

    def get_posidonia_zones(self) -> Optional[Dict]:
        """Get Posidonia oceanica protection zones"""
        cache_path = CACHE_DIR / "caib_posidonia.json"
        
        if cache_path.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if age.total_seconds() < 86400 * 7:
                with open(cache_path, 'r') as f:
                    return json.load(f)
        
        datasets = self.search_datasets("posidònia")
        
        for ds in datasets:
            if "resources" in ds:
                for res in ds["resources"]:
                    if res.get("format") == "GeoJSON":
                        try:
                            geo_response = requests.get(res["url"], timeout=30)
                            if geo_response.status_code == 200:
                                geo_data = geo_response.json()
                                with open(cache_path, 'w') as f:
                                    json.dump(geo_data, f)
                                return geo_data
                        except Exception as e:
                            print(f"Error fetching posidonia GeoJSON: {e}")
        
        return None


def get_climate_for_beach(lat: float, lon: float) -> Dict:
    """Get real climate data for beach"""
    client = CAIBOpenDataClient()
    return client.get_beach_climate_for_location(lat, lon)


if __name__ == "__main__":
    print("=" * 50)
    print("CAIB Client - REAL Data Test")
    print("=" * 50)
    
    client = CAIBOpenDataClient()
    
    print("\nGetting climate for Platja de Palma (39.53, 2.72)...")
    climate = client.get_beach_climate_for_location(39.53, 2.72)
    print(f"Result: {climate}")
    
    print("\n" + "=" * 50)