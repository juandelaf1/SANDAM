"""SANDAM 2026 - SCRAPLING Integration - CORREGIDO"""

from scrapling import Fetcher, StealthyFetcher
from datetime import datetime
import json
from pathlib import Path
import re

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class UIBBeachCam:
    """UIB BeachCam - AI crowd estimation"""
    
    URL = "https://ocupacioplatges.uib.cat"
    
    def get_data(self) -> list:
        cache = CACHE_DIR / "uib_cache.json"
        if cache.exists() and (datetime.now().timestamp() - cache.stat().st_mtime) < 300:
            with open(cache) as f:
                return json.load(f)
        
        results = []
        
        try:
            fetcher = Fetcher()
            response = fetcher.get(self.URL)
            
            # Find beach elements
            for sel in [".beach-item", "article.beach", "[data-beach]"]:
                items = response.css(sel)
                for item in items:
                    name = item.css("h3, h4, .name").text()
                    if name:
                        results.append({
                            "name": name.strip(),
                            "source": "UIB_BeachCam"
                        })
                if results:
                    break
                    
        except Exception as e:
            print(f"UIB: {e}")
        
        with open(cache, 'w') as f:
            json.dump(results, f)
        return results


class MedusAppScraper:
    """MedusApp - Jellyfish sightings"""
    
    URL = "https://www.medusapp.es"
    
    def get_data(self) -> list:
        cache = CACHE_DIR / "medusapp_cache.json"
        if cache.exists() and (datetime.now().timestamp() - cache.stat().st_mtime) < 3600:
            with open(cache) as f:
                return json.load(f)
        
        results = []
        
        try:
            fetcher = Fetcher()
            for endpoint in ["/api/v1/sightings", "/api/sightings"]:
                r = fetcher.get(f"{self.URL}{endpoint}")
                if r.status_code == 200:
                    results = r.json() if isinstance(r.json(), list) else r.json().get("data", [])
                    break
        except Exception as e:
            print(f"MedusApp: {e}")
        
        with open(cache, 'w') as f:
            json.dump(results, f)
        return results


class PlatgesBalears:
    """Platges de Balears - Official beach data"""
    
    URL = "https://www.platgesdebalears.com"
    
    def get_data(self) -> list:
        cache = CACHE_DIR / "platges_cache.json"
        if cache.exists() and (datetime.now().timestamp() - cache.stat().st_mtime) < 600:
            with open(cache) as f:
                return json.load(f)
        
        results = []
        
        try:
            fetcher = StealthyFetcher()
            response = fetcher.get(self.URL)
            
            for sel in ["[class*=card]", ".beach-card", "article"]:
                items = response.css(sel)
                for item in items:
                    name = item.css("h3, h4, .title").text()
                    if name:
                        results.append({
                            "name": name.strip(),
                            "source": "Platges_Balears"
                        })
                if results:
                    break
                    
        except Exception as e:
            print(f"Platges: {e}")
        
        with open(cache, 'w') as f:
            json.dump(results, f)
        return results


def scrape_all() -> dict:
    """Ejecutar todos los scrapers"""
    print("SANDAM SCRAPLING...")
    
    data = {
        "occupation": UIBBeachCam().get_data(),
        "jellyfish": MedusAppScraper().get_data(),
        "flags": PlatgesBalears().get_data(),
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"Results: {len(data['occupation'])} occ, {len(data['jellyfish'])} jellyfish, {len(data['flags'])} flags")
    return data


if __name__ == "__main__":
    scrape_all()