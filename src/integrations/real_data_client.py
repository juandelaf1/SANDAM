"""Real Beach Data Scraper for SANDAM - platgesdebalears.com"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from datetime import datetime
import json
from pathlib import Path
import re


CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class PlatgesBalearsClient:
    """Scraper for official beach data from platgesdebalears.com"""
    
    BASE_URL = "https://www.platgesdebalears.com"
    
    MALLORCA_BEACHES = [
        "Palma", "Can Picafort", "Alcúdia", "Cala Millor", "Cala Rajada",
        "Cala Bona", "Cala Morlanda", "Cala Nau", "Port de Pollença",
        "Port d'Alcúdia", "Muro", "Colonia de Sant Jordi", "Santanyí",
        "Cala d'Or", "Cala Ferrera", "Cala Serena", "Cala Gran",
        "S'Arenal", "Cala Blava", "Llucmajor", "Cala Pi", "Cala Llarga",
        "Calaenmore", "Son Serra de Marina", "Cala Mesquida", "Cala Tortuga",
        "Cala Agulla", "Cala Ratjada", "Cala Gat", "Cala Son Moll",
        "Capdepera", "Cala Mesquida", "Fornells", "Cala Presili",
        "Platja des Carregador", "Platja de Muntanya"
    ]

    def get_beach_status(self, beach_name: str = None) -> List[Dict]:
        """Scrape beach status from official page"""
        cache_file = "platges_status.json"
        cache_path = CACHE_DIR / cache_file
        
        if cache_path.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if age.total_seconds() < 1800:
                with open(cache_path, 'r') as f:
                    cached = json.load(f)
                    if beach_name:
                        return [b for b in cached if beach_name.lower() in b.get("name", "").lower()]
                    return cached
        
        try:
            response = requests.get(
                f"{self.BASE_URL/caiba}",
                timeout=20,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml"
                }
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                beaches = self._parse_html_beaches(soup)
                
                with open(cache_path, 'w') as f:
                    json.dump(beaches, f)
                
                if beach_name:
                    return [b for b in beaches if beach_name.lower() in b.get("name", "").lower()]
                return beaches
                
        except Exception as e:
            print(f"Platges scrape error: {e}")
        
        return []

    def _parse_html_beaches(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse beach data from HTML"""
        beaches = []
        
        cards = soup.find_all('div', class_='beach-card')
        
        for card in cards:
            try:
                name = card.find('h3', class_='beach-name')
                if not name:
                    continue
                    
                name = name.text.strip()
                
                flag_elem = card.find('span', class_='flag')
                flag = flag_elem.get('class', ['unknown'])[-1] if flag_elem else 'unknown'
                
                occupation_elem = card.find('div', class_='occupation')
                occupation = int(re.search(r'\d+', occupation_elem.text).group()) if occupation_elem else 50
                
                temp_elem = card.find('span', class_='temperature')
                temperature = float(temp_elem.text.replace('°C', '')) if temp_elem else None
                
                beaches.append({
                    "name": name,
                    "flag": flag,
                    "occupation": occupation,
                    "water_temperature": temperature,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception:
                continue
        
        return beaches


class AEMETRealClient:
    """Real AEMET weather integration"""
    
    BASE_URL = "https://opendata.aemet.es/opendata/api"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_station_data(self, station_id: str = "C249") -> Optional[Dict]:
        """Get real-time data from AEMET station"""
        cache_path = CACHE_DIR / f"aemet_station_{station_id}.json"
        
        if cache_path.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if age.total_seconds() < 1800:
                with open(cache_path, 'r') as f:
                    return json.load(f)
        
        try:
            url = f"{self.BASE_URL}/observacion/convencional/datos/estacion/{station_id}"
            response = requests.get(
                url,
                params={"api_key": self.api_key},
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                datos_url = data.get("datos")
                
                if datos_url:
                    data_response = requests.get(datos_url, timeout=20)
                    if data_response.status_code == 200:
                        final_data = data_response.json()
                        with open(cache_path, 'w') as f:
                            json.dump(final_data, f)
                        return final_data
                        
        except Exception as e:
            print(f"AEMET error: {e}")
        
        return None
    
    def get_forecast(self, zone: str = "mallorca") -> Optional[Dict]:
        """Get weather forecast for zone"""
        cache_path = CACHE_DIR / f"aemet_forecast_{zone}.json"
        
        if cache_path.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if age.total_seconds() < 3600:
                with open(cache_path, 'r') as f:
                    return json.load(f)
        
        try:
            url = f"{self.BASE_URL}/prediccion/provincia/hoy"
            response = requests.get(
                url,
                params={"api_key": self.api_key},
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                with open(cache_path, 'w') as f:
                    json.dump(data, f)
                return data
                
        except Exception as e:
            print(f"AEMET forecast error: {e}")
        
        return None


def load_api_key() -> str:
    """Load AEMET API key from .env"""
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("AEMET_API_KEY"):
                    return line.split("=")[1].strip()
    return ""


if __name__ == "__main__":
    print("=" * 60)
    print("Real Data Sources Test")
    print("=" * 60)
    
    print("\n1. Testing AEMET...")
    api_key = load_api_key()
    if api_key:
        aemet = AEMETRealClient(api_key)
        data = aemet.get_station_data("C249")
        print(f"   AEMET station data: {'OK' if data else 'Failed'}")
    else:
        print("   No API key found")
    
    print("\n2. Testing Platges de Balears...")
    platges = PlatgesBalearsClient()
    beaches = platges.get_beach_status()
    print(f"   Found {len(beaches)} beaches")
    
    print("\n" + "=" * 60)