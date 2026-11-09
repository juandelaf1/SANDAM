"""API Endpoint: Datos de scraping (procedencia mixta/según fuente; no afirmar tiempo real verificado sin evidencia)."""

import asyncio

from fastapi import APIRouter

from src.integrations.scraper import (
    MedusAppScraper,
    PlatgesBalearsScraper,
    UIBBeachCamScraper,
    scrape_all_sources,
)

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.get("/actualizar")
async def actualizar_datos():
    """
    Ejecuta scrapers y devuelve datos según fuente disponible (procedencia mixta).
    Modo B/Q1-Q2: no afirmar ocupación/capacidad/tiempo real verificado sin fuente, metodología y latencia conocidas.
    - UIB BeachCam: señal/estimación de ocupación (verificar procedencia)
    - MedusApp: avistamientos reportados
    - Platges de Balears: banderas/indicadores publicados oficialmente
    """
    try:
        datos = await asyncio.to_thread(scrape_all_sources)

        return {
            "status": "success",
            "sources": {
                "uib_beachcam": {
                    "occupation_count": len(datos.get("occupation", [])),
                    "data": datos.get("occupation", []),
                },
                "medusapp": {
                    "sightings_count": len(datos.get("jellyfish", [])),
                    "data": datos.get("jellyfish", []),
                },
                "platges_balears": {
                    "beaches_count": len(datos.get("flags", [])),
                    "data": datos.get("flags", []),
                },
            },
            "timestamp": datos.get("timestamp"),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/ocupacion")
async def obtener_ocupacion():
    """Obtiene solo datos de ocupación (UIB BeachCam)"""
    scraper = UIBBeachCamScraper()
    datos = await asyncio.to_thread(scraper.scrape)

    return {
        "source": "UIB_BeachCam",
        "beaches": datos,
        "count": len(datos),
    }


@router.get("/medusas")
async def obtener_medusas():
    """Obtiene solo avistamientos de medusas (MedusApp)"""
    scraper = MedusAppScraper()
    datos = await asyncio.to_thread(scraper.scrape)

    return {
        "source": "MedusApp",
        "sightings": datos,
        "count": len(datos),
    }


@router.get("/banderas")
async def obtener_banderas():
    """Obtiene solo banderas (Platges de Balears)"""
    scraper = PlatgesBalearsScraper()
    datos = await asyncio.to_thread(scraper.scrape)

    return {
        "source": "Platges_Balears",
        "beaches": datos,
        "count": len(datos),
    }
