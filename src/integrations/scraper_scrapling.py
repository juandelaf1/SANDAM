"""SANDAM 2026 - Web Scraping with SCRAPLING Library

Scrapes real-time data from:
1. UIB BeachCam - Crowd AI estimation
2. MedusApp - Jellyfish sightings  
3. Platges de Balears - Official beach data
"""

from scrapling import Fetcher, StealthyFetcher
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path
import re


CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class UIBBeachCamScraper:
    """Scraper for UIB BeachCam using SCRAPLING"""
    
    BASE_URL = "https://ocupacioplatges.uib.cat"
    
    def __init__(self):
        self.cache_file = CACHE_DIR / "uib_beachcam.json"
        self.cache_duration = 300  # 5 min
    
    def scrape(self) -> List[Dict]:
        # Check cache
        if self.cache_file.exists():
            age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            if age.total_seconds() < self.cache_duration:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        
        results = []
        
        try:
            # Use Fetcher (regular) or StealthyFetcher (bypasses bots)
            fetcher = Fetcher()
            response = fetcher.fetch(self.BASE_URL)
            
            if response.status_code == 200:
                # Try different selectors
                selectors = [
                    ".beach-item",
                    ".playa", 
                    "[class*='beach']",
                    "article",
                    "div.card"
                ]
                
                for selector in selectors:
                    elements = response.css(selector).get_all()
                    if elements:
                        for elem in elements:
                            try:
                                name = elem.css("h3, h4, .name, .title").get_first(default="").text
                                occ = elem.css("[class*='occup'], [class*='fill'], .percentage").get_first(default="")
                                occ_match = re.search(r'\d+', occ.text) if occ else None
                                
                                if name:
                                    results.append({
                                        "name": name.strip(),
                                        "occupation": int(occ_match.group()) if occ_match else 50,
                                        "source": "UIB_BeachCam",
                                        "timestamp": datetime.now().isoformat()
                                    })
                            except:
                                continue
                        
                        if results:
                            break
        
        except Exception as e:
            print(f"UIB scraper error: {e}")
        
        # Save to cache
        if results:
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(results, f)
            except:
                pass
        
        return results


class MedusAppScraper:
    """Scraper for MedusApp jellyfish sightings"""
    
    BASE_URL = "https://www.medusapp.es"
    
    def __init__(self):
        self.cache_file = CACHE_DIR / "medusapp.json"
        self.cache_duration = 3600  # 1 hour
    
    def scrape(self) -> List[Dict]:
        # Check cache
        if self.cache_file.exists():
            age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            if age.total_seconds() < self.cache_duration:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        
        results = []
        
        try:
            # Try API first
            fetcher = Fetcher()
            
            # Try common API endpoints
            for endpoint in ["/api/sightings", "/api/v1/sightings", "/sightings"]:
                try:
                    response = fetcher.fetch(f"{self.BASE_URL}{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            results = data
                        elif isinstance(data, dict):
                            results = data.get("sightings", data.get("data", []))
                        break
                except:
                    continue
            
            # Fallback to web scraping
            if not results:
                response = fetcher.fetch(self.BASE_URL)
                if response.status_code == 200:
                    cards = response.css("[class*='sight'], .card, article").get_all()
                    for card in cards:
                        try:
                            location = card.css("[class*='location'], .place").get_first(default="").text
                            species = card.css("[class*='species'], .type").get_first(default="").text
                            date = card.css("[class*='date'], time").get_first(default="").text
                            
                            results.append({
                                "location": location.strip() if location else "Unknown",
                                "species": species.strip() if species else "Unknown",
                                "date": date.strip() if date else datetime.now().isoformat()
                            })
                        except:
                            continue
        
        except Exception as e:
            print(f"MedusApp scraper error: {e}")
        
        # Save to cache
        if results:
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(results, f)
            except:
                pass
        
        return results


class PlatgesBalearsScraper:
    """Scraper for Platges de Balears (official) using SCRAPLING"""
    
    BASE_URL = "https://www.platgesdebalears.com"
    
    def __init__(self):
        self.cache_file = CACHE_DIR / "platges_balears.json"
        self.cache_duration = 600  # 10 min
    
    def scrape(self) -> List[Dict]:
        # Check cache
        if self.cache_file.exists():
            age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            if age.total_seconds() < self.cache_duration:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        
        results = []
        
        try:
            # Use StealthyFetcher to bypass anti-bot
            fetcher = StealthyFetcher()
            response = fetcher.fetch(self.BASE_URL)
            
            if response.status_code == 200:
                # Try multiple selectors
                selectors = [
                    "[class*='beach-card']",
                    "[class*='playa-card']",
                    ".beach",
                    ".playa",
                    "article"
                ]
                
                for selector in selectors:
                    elements = response.css(selector).get_all()
                    if elements:
                        for elem in elements:
                            try:
                                # Name
                                name = elem.css("h3, h4, .name, .title").get_first(default="").text
                                
                                # Flag (verde/amarillo/rojo)
                                flag = "unknown"
                                flag_classes = elem.css(".flag, .status, [class*='flag']").get_first(default=None)
                                if flag_classes:
                                    class_str = str(flag_classes.attrib.get("class", ""))
                                    if "green" in class_str: flag = "green"
                                    elif "yellow" in class_str: flag = "yellow"
                                    elif "red" in class_str: flag = "red"
                                
                                # Occupation
                                occ = elem.css("[class*='occup'], .fill, .percentage").get_first(default="")
                                occ_match = re.search(r'\d+', occ.text) if occ else None
                                
                                if name:
                                    results.append({
                                        "name": name.strip(),
                                        "flag_color": flag,
                                        "current_occupation": int(occ_match.group()) if occ_match else 50,
                                        "source": "Platges_Balears",
                                        "timestamp": datetime.now().isoformat()
                                    })
                            except:
                                continue
                        
                        if results:
                            break
        
        except Exception as e:
            print(f"Platges scraper error: {e}")
        
        # Save to cache
        if results:
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(results, f)
            except:
                pass
        
        return results


def scrape_all_sources() -> Dict:
    """Run all scrapers and return combined results"""
    
    resultados = {
        "occupation": [],
        "jellyfish": [],
        "flags": [],
        "timestamp": datetime.now().isoformat()
    }
    
    print("=" * 50)
    print("SANDAM - Scraping with SCRAPLING")
    print("=" * 50)
    
    # UIB BeachCam
    try:
        print("\n[1/3] Scraping UIB BeachCam...")
        uib = UIBBeachCamScraper()
        data = uib.scrape()
        resultados["occupation"] = data
        print(f"    Found: {len(data)} beaches")
    except Exception as e:
        print(f"    Error: {e}")
    
    # MedusApp
    try:
        print("\n[2/3] Scraping MedusApp...")
        medusapp = MedusAppScraper()
        data = medusapp.scrape()
        resultados["jellyfish"] = data
        print(f"    Found: {len(data)} sightings")
    except Exception as e:
        print(f"    Error: {e}")
    
    # Platges de Balears
    try:
        print("\n[3/3] Scraping Platges de Balears...")
        platges = PlatgesBalearsScraper()
        data = platges.scrape()
        resultados["flags"] = data
        print(f"    Found: {len(data)} beaches")
    except Exception as e:
        print(f"    Error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Total: Occupation={len(resultados['occupation'])}, Jellyfish={len(resultados['jellyfish'])}, Flags={len(resultados['flags'])}")
    print("=" * 50)
    
    return resultados


if __name__ == "__main__":
    scrape_all_sources()