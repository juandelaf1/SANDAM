"""API Endpoint: Datos en Tiempo Real (Scraping)"""

from fastapi import APIRouter
from src.integrations.scraper import scrape_all_sources

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.get("/actualizar")
async def actualizar_datos():
    """
    Ejecuta todos los scrapers y obtiene datos en tiempo real:
    - UIB BeachCam: Ocupación real por cámaras AI
    - MedusApp: Avistamientos de medusas
    - Platges de Balears: Banderas y ocupación oficial
    """
    try:
        datos = scrape_all_sources()
        
        return {
            "status": "success",
            "sources": {
                "uib_beachcam": {
                    "occupation_count": len(datos.get("occupation", [])),
                    "data": datos.get("occupation", [])
                },
                "medusapp": {
                    "sightings_count": len(datos.get("jellyfish", [])),
                    "data": datos.get("jellyfish", [])
                },
                "platges_balears": {
                    "beaches_count": len(datos.get("flags", [])),
                    "data": datos.get("flags", [])
                }
            },
            "timestamp": datos.get("timestamp")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/ocupacion")
async def obtener_ocupacion():
    """Obtiene solo datos de ocupación (UIB BeachCam)"""
    from src.integrations.scraper import UIBBeachCamScraper
    
    scraper = UIBBeachCamScraper()
    datos = scraper.scrape()
    
    return {
        "source": "UIB_BeachCam",
        "beaches": datos,
        "count": len(datos)
    }


@router.get("/medusas")
async def obtener_medusas():
    """Obtiene solo avistamientos de medusas (MedusApp)"""
    from src.integrations.scraper import MedusAppScraper
    
    scraper = MedusAppScraper()
    datos = scraper.scrape()
    
    return {
        "source": "MedusApp",
        "sightings": datos,
        "count": len(datos)
    }


@router.get("/banderas")
async def obtener_banderas():
    """Obtiene solo banderas (Platges de Balears)"""
    from src.integrations.scraper import PlatgesBalearsScraper
    
    scraper = PlatgesBalearsScraper()
    datos = scraper.scrape()
    
    return {
        "source": "Platges_Balears",
        "beaches": datos,
        "count": len(datos)
    }