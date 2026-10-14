"""SANDAM 2026 - Web Scraping Module for Dynamic Pages

Scrapes:
1. UIB BeachCam - Real-time crowd estimation (AI cameras)
2. MedusApp - Jellyfish sightings
3. Platges de Balears - Beach occupation real-time
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path
import time
import random

# Intentar importar selenium/playwright
SELENIUM_AVAILABLE = False
PLAYWRIGHT_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    pass

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass


CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class SeleniumScraper:
    """Scraper usando Selenium para páginas dinámicas"""
    
    def __init__(self, headless: bool = True):
        self.driver = None
        self.headless = headless
        self.options = Options()
        
        if headless:
            self.options.add_argument("--headless=new")
        
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    def start(self):
        """Inicia el driver de Selenium"""
        if SELENIUM_AVAILABLE:
            self.driver = webdriver.Chrome(options=self.options)
            return True
        return False
    
    def stop(self):
        """Cierra el driver"""
        if self.driver:
            self.driver.quit()
    
    def get_page(self, url: str, wait_for: str = None, timeout: int = 10) -> str:
        """Obtiene el HTML de una página"""
        if not self.driver:
            return ""
        
        try:
            self.driver.get(url)
            
            if wait_for:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                )
            
            time.sleep(2)  # Esperar carga dinámica
            return self.driver.page_source
            
        except Exception as e:
            print(f"Error getting {url}: {e}")
            return ""


class PlaywrightScraper:
    """Scraper usando Playwright para páginas dinámicas"""
    
    def __init__(self, headless: bool = True):
        self.playwright = None
        self.browser = None
        self.context = None
        self.headless = headless
    
    def start(self):
        """Inicia Playwright"""
        if PLAYWRIGHT_AVAILABLE:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            return True
        return False
    
    def stop(self):
        """Cierra Playwright"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def get_page(self, url: str, wait_for: str = None, timeout: int = 10000) -> str:
        """Obtiene el HTML de una página"""
        if not self.context:
            return ""
        
        try:
            page = self.context.new_page()
            page.goto(url, wait_until="networkidle", timeout=timeout)
            
            if wait_for:
                page.wait_for_selector(wait_for, timeout=timeout)
            
            html = page.content()
            page.close()
            return html
            
        except Exception as e:
            print(f"Error getting {url}: {e}")
            return ""


class UIBBeachCamScraper:
    """
    Scraper para UIB BeachCam
    URL: https://ocupacioplatges.uib.cat/
    Datos: Estimación de ocupación por cámaras AI
    """
    
    BASE_URL = "https://ocupacioplatges.uib.cat"
    
    def __init__(self):
        self.cache_file = CACHE_DIR / "uib_beachcam.json"
        self.cache_duration = 300  # 5 minutos
    
    def scrape(self, use_selenium: bool = True) -> List[Dict]:
        """Obtiene datos de ocupación de playas"""
        
        # Verificar caché
        if self.cache_file.exists():
            age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            if age.total_seconds() < self.cache_duration:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        
        resultados = []
        
        # Intentar con requests primero (más rápido)
        try:
            response = requests.get(self.BASE_URL, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                resultados = self._parse_html(soup)
        except Exception as e:
            print(f"Requests failed: {e}")
        
        # Si no hay resultados, intentar con Selenium/Playwright
        if not resultados and use_selenium:
            resultados = self._scrape_dynamic()
        
        # Guardar en caché
        if resultados:
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(resultados, f)
            except:
                pass
        
        return resultados
    
    def _parse_html(self, soup: BeautifulSoup) -> List[Dict]:
        """Parsea el HTML de UIB BeachCam"""
        beaches = []
        
        # Buscar elementos de playa (estructura puede variar)
        # Nota: La web usa JS dinámico, verificar estructura real
        beach_cards = soup.find_all('div', class_='beach-card')
        
        for card in beach_cards:
            try:
                name = card.find('h3') or card.find('span')
                if name:
                    name = name.text.strip()
                
                # Buscar datos de ocupación
                occupation_elem = card.find('div', class_='occupation')
                occupation = 0
                if occupation_elem:
                    import re
                    match = re.search(r'\d+', occupation_elem.text)
                    if match:
                        occupation = int(match.group())
                
                beaches.append({
                    "name": name,
                    "occupation": occupation,
                    "source": "UIB_BeachCam",
                    "timestamp": datetime.now().isoformat()
                })
            except:
                continue
        
        return beaches
    
    def _scrape_dynamic(self) -> List[Dict]:
        """Usa Selenium/Playwright para scraping dinámico"""
        
        resultados = []
        
        # Intentar Playwright primero
        if PLAYWRIGHT_AVAILABLE:
            scraper = PlaywrightScraper(headless=True)
            if scraper.start():
                try:
                    html = scraper.get_page(self.BASE_URL, wait_for="beach")
                    soup = BeautifulSoup(html, 'html.parser')
                    resultados = self._parse_html(soup)
                except Exception as e:
                    print(f"Playwright error: {e}")
                finally:
                    scraper.stop()
        
        # Si falla, intentar Selenium
        if not resultados and SELENIUM_AVAILABLE:
            scraper = SeleniumScraper(headless=True)
            if scraper.start():
                try:
                    html = scraper.get_page(self.BASE_URL, wait_for="beach")
                    soup = BeautifulSoup(html, 'html.parser')
                    resultados = self._parse_html(soup)
                except Exception as e:
                    print(f"Selenium error: {e}")
                finally:
                    scraper.stop()
        
        return resultados


class MedusAppScraper:
    """
    Scraper para MedusApp
    URL: https://www.medusapp.es/
    Datos: Avistamientos de medusas
    """
    
    BASE_URL = "https://www.medusapp.es"
    # Endpoints conocidos
    API_ENDPOINT = "/api/v1/sightings"
    
    def __init__(self):
        self.cache_file = CACHE_DIR / "medusapp.json"
        self.cache_duration = 3600  # 1 hora
    
    def scrape(self) -> List[Dict]:
        """Obtiene avistamientos de medusas"""
        
        # Verificar caché
        if self.cache_file.exists():
            age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            if age.total_seconds() < self.cache_duration:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        
        resultados = []
        
        # Intentar API directa primero
        try:
            response = requests.get(f"{self.BASE_URL}{self.API_ENDPOINT}", timeout=15)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    resultados = data
                elif isinstance(data, dict) and 'sightings' in data:
                    resultados = data['sightings']
        except Exception as e:
            print(f"MedusApp API error: {e}")
        
        # Intentar web scraping
        if not resultados:
            resultados = self._scrape_web()
        
        # Guardar en caché
        if resultados:
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(resultados, f)
            except:
                pass
        
        return resultados
    
    def _scrape_web(self) -> List[Dict]:
        """Scrapea la web de MedusApp"""
        try:
            response = requests.get(self.BASE_URL, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Buscar avistamientos
                sightings = []
                cards = soup.find_all('div', class_='sighting-card')
                
                for card in cards:
                    try:
                        location = card.find('span', class_='location')
                        species = card.find('span', class_='species')
                        date = card.find('span', class_='date')
                        
                        sightings.append({
                            "location": location.text if location else "Unknown",
                            "species": species.text if species else "Unknown",
                            "date": date.text if date else datetime.now().isoformat()
                        })
                    except:
                        continue
                
                return sightings
        except Exception as e:
            print(f"MedusApp scrap error: {e}")
        
        return []


class PlatgesBalearsScraper:
    """
    Scraper para Platges de Balears (web oficial)
    URL: https://www.platgesdebalears.com
    Datos: Bandera, ocupación, temp, medusas (todo en tiempo real)
    """
    
    BASE_URL = "https://www.platgesdebalears.com"
    
    def __init__(self):
        self.cache_file = CACHE_DIR / "platges_balears.json"
        self.cache_duration = 600  # 10 minutos
    
    def scrape(self) -> List[Dict]:
        """Obtiene datos de todas las playas"""
        
        # Verificar caché
        if self.cache_file.exists():
            age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            if age.total_seconds() < self.cache_duration:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        
        # Intentar con Playwright (la web es muy dinámica)
        resultados = self._scrape_with_playwright()
        
        if not resultados:
            resultados = self._scrape_with_requests()
        
        # Guardar en caché
        if resultados:
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(resultados, f)
            except:
                pass
        
        return resultados
    
    def _scrape_with_requests(self) -> List[Dict]:
        """Intento con requests simple"""
        try:
            response = requests.get(self.BASE_URL, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return self._parse_beaches(soup)
        except Exception as e:
            print(f"Platges requests error: {e}")
        return []
    
    def _scrape_with_playwright(self) -> List[Dict]:
        """Usa Playwright para web dinámica"""
        if not PLAYWRIGHT_AVAILABLE:
            return []
        
        scraper = PlaywrightScraper(headless=True)
        if not scraper.start():
            return []
        
        try:
            html = scraper.get_page(self.BASE_URL, wait_for=".beach-card", timeout=15000)
            soup = BeautifulSoup(html, 'html.parser')
            return self._parse_beaches(soup)
        except Exception as e:
            print(f"Platges Playwright error: {e}")
            return []
        finally:
            scraper.stop()
    
    def _parse_beaches(self, soup: BeautifulSoup) -> List[Dict]:
        """Parsea los datos de playas"""
        beaches = []
        
        # Buscar tarjetas de playa (estructura real puede variar)
        cards = soup.find_all('div', class_=['beach-card', 'playa-card', 'card'])
        
        for card in cards:
            try:
                # Nombre
                name_elem = card.find(['h3', 'h4', 'span'], class_=['name', 'title', 'playa-name'])
                name = name_elem.text.strip() if name_elem else "Unknown"
                
                # Estado (verde/amarillo/rojo)
                flag = "unknown"
                flag_elem = card.find(['span', 'div'], class_=['flag', 'status', 'bandeira'])
                if flag_elem:
                    flag_class = flag_elem.get('class', [])
                    if 'green' in flag_class or 'success' in flag_class:
                        flag = "green"
                    elif 'yellow' in flag_class or 'warning' in flag_class:
                        flag = "yellow"
                    elif 'red' in flag_class or 'danger' in flag_class:
                        flag = "red"
                
                # Ocupación
                occupation = 50
                occ_elem = card.find(['span', 'div', 'p'], class_=['occupation', 'occupancy', 'fill'])
                if occ_elem:
                    import re
                    match = re.search(r'\d+', occ_elem.text)
                    if match:
                        occupation = int(match.group())
                
                beaches.append({
                    "name": name,
                    "flag_color": flag,
                    "current_occupation": occupation,
                    "source": "Platges_Balears",
                    "timestamp": datetime.now().isoformat()
                })
            except:
                continue
        
        return beaches


def scrape_all_sources() -> Dict:
    """
    Ejecuta todos los scrapers y retorna datos combinados
    """
    resultados = {
        "occupation": [],
        "jellyfish": [],
        "flags": [],
        "timestamp": datetime.now().isoformat()
    }
    
    print("Scraping sources...")
    
    # UIB BeachCam - Ocupación
    try:
        uib = UIBBeachCamScraper()
        data = uib.scrape()
        if data:
            resultados["occupation"] = data
            print(f"UIB BeachCam: {len(data)} beaches")
    except Exception as e:
        print(f"UIB error: {e}")
    
    # MedusApp - Medusas
    try:
        medusapp = MedusAppScraper()
        data = medusapp.scrape()
        if data:
            resultados["jellyfish"] = data
            print(f"MedusApp: {len(data)} avistamientos")
    except Exception as e:
        print(f"MedusApp error: {e}")
    
    # Platges de Balears - Todo
    try:
        platges = PlatgesBalearsScraper()
        data = platges.scrape()
        if data:
            resultados["flags"] = data
            print(f"Platges Balears: {len(data)} beaches")
    except Exception as e:
        print(f"Platges error: {e}")
    
    return resultados


if __name__ == "__main__":
    print("=" * 60)
    print("SANDAM - Web Scraping Test")
    print("=" * 60)
    
    print(f"\nSelenium available: {SELENIUM_AVAILABLE}")
    print(f"Playwright available: {PLAYWRIGHT_AVAILABLE}")
    
    print("\nScraping all sources...")
    data = scrape_all_sources()
    
    print(f"\nTotal results:")
    print(f"  Occupation: {len(data['occupation'])}")
    print(f"  Jellyfish: {len(data['jellyfish'])}")
    print(f"  Flags: {len(data['flags'])}")
    
    print("\n" + "=" * 60)