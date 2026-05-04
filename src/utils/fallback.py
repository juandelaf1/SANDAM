from typing import Any, Dict, Optional
from src.models import FlagColor, WaterQuality, DataStatus


def apply_fallback_values(beach: Dict[str, Any]) -> Dict[str, Any]:
    if beach.get("data_status") == DataStatus.unavailable:
        beach["water_temp"] = None
        beach["air_temp"] = None
        beach["uv_index"] = None
        beach["wind_speed"] = None
        beach["wave_height"] = None

    if beach.get("flag_color") == FlagColor.unknown:
        beach["_flag_warning"] = "Estado de bandera no disponible"

    if beach.get("water_quality") == WaterQuality.unknown:
        beach["_quality_warning"] = "Consultar fuentes oficiales para calidad del agua"

    if beach.get("jellyfish_present") is None:
        beach["jellyfish_present"] = False
        beach["_jellyfish_disclaimer"] = "Sin datos de medusas. Precaución recomendada"

    return beach


def get_fallback_recommendation(field: str) -> Optional[Dict[str, str]]:
    fallbacks = {
        "water_temp": {
            "message": "Temperatura del agua no disponible",
            "advice": "Consultar fuentes locales"
        },
        "uv_index": {
            "message": "Índice UV no disponible",
            "advice": "Usar protección solar como medida preventiva"
        },
        "flag_color": {
            "message": "Bandera no disponible",
            "advice": "Consultar con el servicio de playas local"
        },
        "water_quality": {
            "message": "Calidad del agua no disponible",
            "advice": "Evitar baths si hay dudas sobre calidad"
        }
    }
    return fallbacks.get(field)


def is_data_available(beach: Dict[str, Any]) -> bool:
    critical_fields = ["flag_color", "water_quality"]
    for field in critical_fields:
        value = beach.get(field)
        if value in [FlagColor.unknown, WaterQuality.unknown]:
            return False
    return True


def get_data_status_summary(beach: Dict[str, Any]) -> Dict[str, int]:
    available_count = 0
    unavailable_count = 0

    data_fields = [
        "water_temp", "air_temp", "uv_index",
        "wind_speed", "wave_height",
        "e_coli_count", "enterococci_count"
    ]

    for field in data_fields:
        if beach.get(field) is not None:
            available_count += 1
        else:
            unavailable_count += 1

    return {
        "available": available_count,
        "unavailable": unavailable_count,
        "total": len(data_fields)
    }