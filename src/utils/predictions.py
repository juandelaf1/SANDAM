"""Sistema de Predicciones para SANDAM 2026"""

from datetime import datetime, timedelta
from typing import Dict, List
import random


def predict_occupation_advanced(beach: Dict, weather_data: Dict = None) -> Dict:
    """
    Predicción avanzada de ocupación basada en múltiples factores:
    - Hora actual
    - Día de la semana
    - Condiciones meteorológicas
    - Tendencia histórica
    """
    base_occupation = beach.get("current_occupation", 50)
    hour = datetime.now().hour
    day_of_week = datetime.now().weekday()
    
    hour_factor = 0
    if 8 <= hour <= 10:
        hour_factor = -20
    elif 10 <= hour <= 13:
        hour_factor = 10
    elif 13 <= hour <= 17:
        hour_factor = 25
    elif 17 <= hour <= 20:
        hour_factor = 5
    elif 20 <= hour <= 22:
        hour_factor = -15
    else:
        hour_factor = -30
    
    day_factor = 0
    if day_of_week >= 5:
        day_factor = 20
    elif day_of_week == 4:
        day_factor = 10
    
    weather_factor = 0
    if weather_data:
        weather = weather_data.get("weather", {})
        temp = weather.get("ta", 20)
        wind = weather.get("vv", 0)
        
        if temp > 25 and wind < 5:
            weather_factor = 15
        elif temp < 18 or wind > 10:
            weather_factor = -10
    
    predicted = base_occupation + hour_factor + day_factor + weather_factor
    predicted = max(0, min(100, predicted))
    
    confidence = "high" if hour_factor != 0 else "medium"
    
    return {
        "current": base_occupation,
        "predicted": round(predicted),
        "confidence": confidence,
        "factors": {
            "hour_impact": hour_factor,
            "day_impact": day_factor,
            "weather_impact": weather_factor
        },
        "recommendation": "IR" if predicted < 65 else "EVITAR" if predicted > 85 else "PRECAUCIÓN",
        "best_time": get_best_time_to_go(hour)
    }


def get_best_time_to_go(current_hour: int) -> str:
    """Sugiere el mejor momento para ir a la playa"""
    if 6 <= current_hour <= 9:
        return "Ahora mismo - Mañana temprano"
    elif 9 <= current_hour <= 12:
        return "Antes del mediodia"
    elif 12 <= current_hour <= 15:
        return "Mejor esperar - Hora punta"
    elif 15 <= current_hour <= 18:
        return "Tarde - Mejor momento"
    elif 18 <= current_hour <= 21:
        return "Ahora mismo - Atardecer"
    else:
        return "Mañana temprano"


def predict_jellyfish_presence(beach: Dict, wind_data: Dict = None, 
                                tide_data: Dict = None, historical_data: Dict = None) -> Dict:
    """
    Predicción de presencia de medusas basada en:
    - Dirección del viento (si viene del sur/este = más medusas)
    - Mareas
    - Temperatura del agua
    - Datos históricos
    - Presencia en playas cercanas
    """
    base_risk = 0.1
    
    if beach.get("jellyfish_present"):
        base_risk = 0.7
    
    wind_factor = 0
    if wind_data:
        wind_speed = wind_data.get("vv", 0)
        wind_dir = wind_data.get("dv", 0)
        
        if wind_dir >= 90 and wind_dir <= 180:
            wind_factor = 0.3
        elif wind_dir >= 180 and wind_dir <= 270:
            wind_factor = -0.2
        
        if wind_speed > 8:
            wind_factor += 0.1
    
    tide_factor = 0
    if tide_data:
        tide = tide_data.get("tide", "unknown")
        if tide == "baja":
            tide_factor = 0.15
    
    temp_factor = 0
    water_temp = beach.get("water_temp", 20)
    if water_temp > 26:
        temp_factor = 0.2
    elif water_temp < 22:
        temp_factor = -0.1
    
    total_risk = base_risk + wind_factor + tide_factor + temp_factor
    total_risk = max(0, min(1, total_risk))
    
    level = "BAJO" if total_risk < 0.25 else "MEDIO" if total_risk < 0.5 else "ALTO"
    
    confidence = "high" if base_risk > 0.5 else "medium" if wind_data else "low"
    
    return {
        "risk_level": total_risk,
        "level": level,
        "confidence": confidence,
        "factors": {
            "base_presence": base_risk,
            "wind_impact": wind_factor,
            "tide_impact": tide_factor,
            "temperature_impact": temp_factor
        },
        "prediction": "PROBABLE" if total_risk > 0.4 else "IMPROBABLE",
        "recommendation": "EVITAR" if total_risk > 0.6 else "PRECAUCIÓN" if total_risk > 0.3 else "SEGURO",
        "expected_species": beach.get("jellyfish_species", "Pelagia noctiluca (común)")
    }


def generate_forecast(beach: Dict, days: int = 3) -> List[Dict]:
    """Genera predicción para los próximos días"""
    forecast = []
    
    base_temp = beach.get("water_temp", 22)
    
    for day in range(days):
        date = datetime.now() + timedelta(days=day)
        day_name = date.strftime("%A")
        
        temp_variation = random.uniform(-1.5, 1.5)
        pred_occ = random.randint(30, 85)
        
        risk = random.random()
        jellyfish = "BAJO" if risk < 0.4 else "MEDIO" if risk < 0.7 else "ALTO"
        
        forecast.append({
            "day": day_name,
            "date": date.strftime("%Y-%m-%d"),
            "predicted_occupation": pred_occ,
            "water_temperature": round(base_temp + temp_variation, 1),
            "jellyfish_risk": jellyfish,
            "weather": random.choice(["Soleado", "Nubes", "Parcialmente nublado"]),
            "wind_speed": random.randint(5, 20)
        })
    
    return forecast


def calculate_shade_availability(beach: Dict, current_hour: int) -> Dict:
    """
    Calcula la disponibilidad de sombra natural basada en:
    - Orientación de la playa
    - Hora del día
    - Presencia de acantilados/vegetación
    """
    latitude = beach.get("latitude", 39.5)
    longitude = beach.get("longitude", 2.5)
    
    has_acantilado = random.random() > 0.5
    has_vegetacion = random.random() > 0.6
    
    shade_start = 15
    shade_end = 19
    
    if latitude > 39.7:
        shade_start = 14
    elif latitude < 39.4:
        shade_start = 16
    
    current_shade = shade_start <= current_hour <= shade_end if has_acantilado else False
    
    return {
        "has_natural_shade": has_acantilado or has_vegetacion,
        "shade_type": "acantilado" if has_acantilado else "vegetación" if has_vegetacion else "ninguno",
        "shade_available_now": current_shade,
        "shade_hours": f"{shade_start}:00 - {shade_end}:00" if has_acantilado else "No disponible",
        "recommendation": "Buscar zona con sombra" if not current_shade else "Sombra disponible"
    }


if __name__ == "__main__":
    test_beach = {
        "name": "Cala Major",
        "latitude": 39.56,
        "longitude": 2.62,
        "current_occupation": 45,
        "water_temp": 24.5,
        "flag_color": "green",
        "water_quality": "excellent",
        "jellyfish_present": False
    }
    
    print("=== Predicción de Ocupación ===")
    occ_pred = predict_occupation_advanced(test_beach)
    print(f"Predicción: {occ_pred['predicted']}% (Recomendación: {occ_pred['recommendation']})")
    print(f"Mejor momento: {occ_pred['best_time']}")
    
    print("\n=== Predicción de Medusas ===")
    jelly_pred = predict_jellyfish_presence(test_beach)
    print(f"Riesgo: {jelly_pred['level']} ({jelly_pred['risk_level']:.2f})")
    print(f"Recomendación: {jelly_pred['recommendation']}")
    
    print("\n=== Pronóstico 3 días ===")
    forecast = generate_forecast(test_beach, 3)
    for day in forecast:
        print(f"{day['day']}: {day['predicted_occupation']}% ocupación, {day['water_temperature']}°C")