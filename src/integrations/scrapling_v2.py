"""SANDAM 2026 - SCRAPLING Integration (API v0.4.x)"""

from scrapling import Fetcher, StealthyFetcher
from scrapling.parser import Selector
from typing import List, Dict
from datetime import datetime
import json
from pathlib import Path
import re

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class UIBBeachCam:
    """Scraper for UIB BeachCam - Real-time crowd AI"""
    
    URL = "https://ocupacioplatges.uib.cat"
    
    def get_data(self) -> List[Dict]:
        cache = CACHE_DIR / "uib_cache.json"
        if cache.exists() and (datetime.now().timestamp() - cache.stat().st_mtime) < 300:
            with open(cache) as f:
                return json.load(f)
        
        try:
            # Configure and fetch
            fetcher = Fetcher()
            fetcher.configure(browser="chrome", bypass=True)
            response = fetcher.get(self.URL)
            
            results = []
            # Try selectors
            for sel in [".beach-item", "article.beach", "[data-beach]"]:
                items = response.css(sel)
                for item in items:
                    name = item.css("h3, h4, .name").text()
                    occ_text = item.css("[class*=occup], .count").text()
                    occ = int(re.search(r"\d+", occ_text).group()) if re.search(r"\d+", occ_text) else 50
                    
                    results.append({"name": name.strip(), "occupation": occ, "source": "UIB_BeachCam"})
                    break
                
                if results:
                    break
                    
        except Exception as e:
            print(f"UIB error: {e}")
            results = []
        
        with open(cache, 'w') as f:
            json.dump(results, f)
        return results


class MedusAppData:
    """MedusApp jellyfish data"""
    
    URL = "https://www.medusapp.es"
    
    def get_data(self) -> List[Dict]:
        cache = CACHE_DIR / "medusapp_cache.json"
        if cache.exists() and (datetime.now().timestamp() - cache.stat().st_mtime) < 3600:
            with open(cache) as f:
                return json.load(f)
        
        results = []
        
        try:
            fetcher = Fetcher()
            fetcher.configure(browser="chrome")
            
            # Try API endpoints
            for endpoint in ["/api/v1/sightings", "/sightings"]:
                try:
                    r = fetcher.get(f"{self.URL}{endpoint}")
                    if r.status_code == 200:
                        results = r.json()
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"MedusApp error: {e}")
        
        with open(cache, 'w') as f:
            json.dump(results, f)
        return results


class PlatgesBalears:
    """Official Platges de Balears data"""
    
    URL = "https://www.platgesdebalears.com"
    
    def get_data(self) -> List[Dict]:
        cache = CACHE_DIR / "platges_cache.json"
        if cache.exists() and (datetime.now().timestamp() - cache.stat().st_mtime) < 600:
            with open(cache) as f:
                return json.load(f)
        
        results = []
        
        try:
            # Use StealthyFetcher for anti-bot sites
            fetcher = StealthyFetcher()
            fetcher.configure(browser="chrome", bypass=True, timeout=30)
            response = fetcher.get(self.URL)
            
            # Parse with multiple selectors
            for sel in ["[class*=card]", ".beach", "article"]:
                items = response.css(sel)
                for item in items:
                    name = item.css("h3, h4, .title").text()
                    flag = item.css(".flag").attrib.get("class", "")
                    flag = "green" if "green" in flag else "yellow" if "yellow" in flag else "red" if "red" in flag else "unknown"
                    
                    if name:
                        results.append({
                            "name": name.strip(),
                            "flag": flag,
                            "source": "Platges_Balears"
                        })
                
                if results:
                    break
                    
        except Exception as e:
            print(f"Platges error: {e}")
        
        with open(cache, 'w') as f:
            json.dump(results, f)
        return results


def scrape_all() -> Dict:
    """Main scraper - gets all data"""
    print("=" * 50)
    print("SANDAM - SCRAPLING")
    print("=" * 50)
    
    data = {
        "occupation": UIBBeachCam().get_data(),
        "jellyfish": MedusAppData().get_data(),
        "flags": PlatgesBalears().get_data(),
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"Results: {len(data['occupation'])} occ, {len(data['jellyfish'])} jellyfish, {len(data['flags'])} flags")
    return data


if __name__ == "__main__":
    scrape_all()