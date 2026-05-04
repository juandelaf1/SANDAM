from typing import List, Dict, Any
from src.models import FlagColor, WaterQuality


def generate_recommendations(beach: dict) -> List[Dict[str, Any]]:
    recommendations = []
    level = "safe"
    messages = []

    if beach.get("flag_color") == FlagColor.red:
        level = "danger"
        messages.append("🚫 No bañarse. Banderas rojas izgadas en la playa")
    elif beach.get("flag_color") == FlagColor.yellow:
        if level != "danger":
            level = "caution"
        messages.append("⚠️ Baño con precaución. Oleaje moderado")

    if beach.get("jellyfish_present"):
        if level != "danger":
            level = "warning"
        messages.append("🐙 Medusas detectadas. Evitar contacto con la piel")

    uv = beach.get("uv_index")
    if uv is not None:
        if uv >= 8:
            if level == "safe":
                level = "warning"
            messages.append(f"☀️ UV muy alto ({uv}). Usar protección SPF 50+")
        elif uv >= 6:
            if level == "safe":
                level = "caution"
            messages.append(f"☀️ UV alto ({uv}). Evitar exposición 12h-16h")

    wave = beach.get("wave_height")
    if wave is not None and wave > 2.0:
        if level != "danger":
            level = "warning"
        messages.append(f"🌊 Oleaje peligroso ({wave}m). No nadar")

    if beach.get("water_quality") == WaterQuality.poor:
        level = "danger"
        messages.append("🚫 Calidad agua mala. No bañarse")
    elif beach.get("water_quality") == WaterQuality.sufficient:
        if level == "safe":
            level = "caution"
        messages.append("⚠️ Calidad agua aceptable con precaución")

    occupation = beach.get("current_occupation", 0)
    if occupation >= 90:
        if level == "safe":
            level = "caution"
        messages.append(f"👥 Playa muy concurrida ({occupation}%)")
    elif occupation >= 70:
        messages.append(f"👥 Playa moderadamente ocupada ({occupation}%)")

    if not beach.get("has_lifeguard"):
        if level == "safe":
            level = "caution"
        messages.append("🏖️ Sin socorrista. Precaución extra")

    if beach.get("sargasso_level", 0) >= 2:
        messages.append("🌿 Nivel alto de sargazo en la orilla")

    if level == "safe":
        details = []
        if beach.get("flag_color") == FlagColor.green:
            details.append("✓ Bandera verde")
        if not beach.get("jellyfish_present"):
            details.append("✓ Sin medusas")
        if beach.get("water_quality") == WaterQuality.excellent:
            details.append("✓ Calidad agua excelente")
        if beach.get("has_lifeguard"):
            details.append("✓ Socorrista presente")
        if occupation < 50:
            details.append("✓ Playa tranquila")

        messages.append(" | ".join(details) if details else "Condiciones óptimas para el baño")

    return [
        {
            "level": level,
            "message": messages[0] if messages else "Sin recomendaciones",
            "details": messages[1:] if len(messages) > 1 else []
        }
    ]


def generate_alerts(beach: dict) -> List[Dict[str, Any]]:
    alerts = []

    if beach.get("flag_color") == FlagColor.red:
        alerts.append({
            "type": "danger",
            "message": "Bandera roja",
            "field": "flag_color"
        })

    if beach.get("jellyfish_present"):
        alerts.append({
            "type": "warning",
            "message": f"Medusas detectadas{': ' + beach['jellyfish_species'] if beach.get('jellyfish_species') else ''}",
            "field": "jellyfish_present"
        })

    if beach.get("water_quality") == WaterQuality.poor:
        alerts.append({
            "type": "danger",
            "message": "Calidad del agua comprometida",
            "field": "water_quality"
        })

    if beach.get("current_occupation", 0) >= 90:
        alerts.append({
            "type": "info",
            "message": "Playa a máxima capacidad",
            "field": "current_occupation"
        })

    return alerts


def get_safety_message(flag: FlagColor) -> str:
    messages = {
        FlagColor.green: "Seguro para el baño",
        FlagColor.yellow: "Baño con precaución",
        FlagColor.red: "Prohibido bañarse",
        FlagColor.unknown: "Consultar estado con autoridades"
    }
    return messages.get(flag, "Estado desconocido")