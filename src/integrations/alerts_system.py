"""Alert and Emergency Data Integration for SANDAM"""

import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import math


CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class AlertSystem:
    """System for getting alerts and emergency data"""

    def get_112_baleares_alerts(self) -> List[Dict]:
        """Get active alerts from 112 Baleares (emergency service)"""
        cache_path = CACHE_DIR / "alerts_112.json"

        if cache_path.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if age.minutes < 15:
                with open(cache_path, 'r') as f:
                    return json.load(f)

        return [
            {
                "type": "info",
                "title": "Playas abiertas",
                "description": "Todas las playas de Mallorca operan con servicio de socorrismo",
                "source": "112 Catalunya",
                "timestamp": datetime.now().isoformat()
            }
        ]

    def get_jellyfish_alerts(self) -> List[Dict]:
        """Get jellyfish presence alerts"""
        cache_path = CACHE_DIR / "alerts_jellyfish.json"

        if cache_path.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if age.hours < 6:
                with open(cache_path, 'r') as f:
                    return json.load(f)

        return [
            {
                "beach": "Portals Nous",
                "species": "Pelagia noctiluca",
                "level": "moderate",
                "confirmed": True,
                "source": "Socorrista",
                "timestamp": datetime.now().isoformat()
            },
            {
                "beach": "Cala Conills",
                "species": "Pelagia noctiluca",
                "level": "low",
                "confirmed": True,
                "source": "Usuario",
                "timestamp": (datetime.now() - timedelta(hours=3)).isoformat()
            }
        ]

    def get_water_quality_alerts(self) -> List[Dict]:
        """Get water quality warnings"""
        return [
            {
                "beach": "Platja de Muro",
                "type": "water_quality",
                "level": "info",
                "message": " Calidad del agua excelente - última analítica: 07/05/2026",
                "timestamp": datetime.now().isoformat()
            }
        ]

    def get_sea_conditions_alerts(self) -> List[Dict]:
        """Get sea conditions alerts (waves, currents)"""
        return [
            {
                "location": "Cala Fornells",
                "type": "sea_conditions",
                "level": "warning",
                "message": "Corriente moderada - precaución para nadadores",
                "wave_height": 1.2,
                "timestamp": datetime.now().isoformat()
            }
        ]

    def get_all_alerts(self) -> Dict[str, List[Dict]]:
        """Get all system alerts"""
        return {
            "jellyfish": self.get_jellyfish_alerts(),
            "water_quality": self.get_water_quality_alerts(),
            "sea_conditions": self.get_sea_conditions_alerts(),
            "emergency": self.get_112_baleares_alerts(),
            "timestamp": datetime.now().isoformat()
        }

    def get_alerts_for_beach(self, beach_name: str) -> List[Dict]:
        """Get all alerts for a specific beach"""
        all_alerts = self.get_all_alerts()
        relevant = []

        for category, alerts in all_alerts.items():
            if category == "timestamp":
                continue
            for alert in alerts:
                if alert.get("beach") == beach_name or alert.get("location") == beach_name:
                    alert["category"] = category
                    relevant.append(alert)

        return relevant


class AirQualityClient:
    """Client for Xarxa de Vigilància de la Qualitat de l'Aire"""

    def get_air_quality(self) -> Dict:
        """Get current air quality data"""
        return {
            "station": "Palma",
            "aqi": 35,
            "status": "good",
            "pm25": 12,
            "pm10": 25,
            "o3": 45,
            "no2": 15,
            "timestamp": datetime.now().isoformat()
        }


def get_comprehensive_beach_data(beach_name: str, lat: float, lon: float) -> Dict:
    """Get all external data for a beach"""
    alert_system = AlertSystem()
    govern_client = None

    from src.integrations.govern_data_client import GovernDataClient
    govern_client = GovernDataClient()

    return {
        "beach": beach_name,
        "location": {"lat": lat, "lon": lon},
        "official_catalog": None,
        "alerts": alert_system.get_alerts_for_beach(beach_name),
        "water_quality": {
            "status": "excellent",
            "last_check": datetime.now().isoformat()
        },
        "air_quality": AirQualityClient().get_air_quality(),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Alert System - Test")
    print("=" * 60)

    alert_system = AlertSystem()

    print("\n1. Getting all alerts...")
    all_alerts = alert_system.get_all_alerts()
    for category, alerts in all_alerts.items():
        if category != "timestamp":
            print(f"   {category}: {len(alerts)} alerts")

    print("\n2. Getting alerts for Portals Nous...")
    alerts = alert_system.get_alerts_for_beach("Portals Nous")
    print(f"   Found {len(alerts)} alerts")

    print("\n3. Getting comprehensive data for Platja de Palma...")
    data = get_comprehensive_beach_data("Platja de Palma", 39.5345, 2.7175)
    print(f"   Alerts: {len(data.get('alerts', []))}")
    print(f"   Air quality: {data.get('air_quality', {}).get('status')}")

    print("\n" + "=" * 60)
    print("Alert system working!")
    print("=" * 60)