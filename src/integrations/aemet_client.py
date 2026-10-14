"""AEMET OpenData API Client for SANDAM"""

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
import time


class AEMETClient:
    """Client for AEMET OpenData API"""

    BASE_URL = "https://opendata.aemet.es/opendata/api"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _make_request(self, endpoint: str, max_retries: int = 3) -> Dict[str, Any]:
        """Make request to AEMET API with 2-step process"""
        url = f"{self.BASE_URL}{endpoint}"

        if self.api_key and "?" not in url:
            url += f"?api_key={self.api_key}"
        elif self.api_key:
            url += f"&api_key={self.api_key}"

        self.session.headers.update({
            "User-Agent": "SANDAM/1.0 (Python)",
            "Accept": "application/json, text/html"
        })

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=60)

                if response.status_code == 404:
                    return {"error": "Endpoint not found", "details": url}
                if response.status_code != 200:
                    print(f"Attempt {attempt + 1}: Status {response.status_code}")
                    time.sleep(2)
                    continue

                content_type = response.headers.get("content-type", "")
                if "html" in content_type:
                    print(f"Received HTML instead of JSON, retrying...")
                    time.sleep(2)
                    continue

                data = response.json()

                if isinstance(data, dict) and data.get("estado") and data.get("estado") != 200:
                    return {"error": data.get("descripcion", "Unknown error")}

                datos_url = data.get("datos") if isinstance(data, dict) else None
                if not datos_url:
                    return data

                for data_attempt in range(3):
                    try:
                        datos_response = self.session.get(datos_url, timeout=60)
                        if datos_response.status_code == 200:
                            return datos_response.json()
                        elif datos_response.status_code == 404:
                            return data
                    except Exception as e:
                        print(f"Data fetch attempt {data_attempt + 1}: {e}")
                        time.sleep(2)

                return data

            except requests.exceptions.ConnectionError as e:
                print(f"Connection error (attempt {attempt + 1}): {e}")
                time.sleep(3)
            except Exception as e:
                print(f"Request error (attempt {attempt + 1}): {e}")
                time.sleep(2)

        return {"error": "Max retries exceeded"}

    def get_beaches_forecast(self, beach_code: str) -> Optional[Dict]:
        """
        Get forecast for a specific beach.

        Args:
            beach_code: Beach ID (e.g., '0704001' for Cala Major, Mallorca)

        Returns:
            Dictionary with forecast data or None if not found
        """
        try:
            endpoint = f"/prediccion/especifica/playa/{beach_code}"
            return self._make_request(endpoint)
        except Exception as e:
            print(f"Error fetching beach forecast: {e}")
            return None

    def get_all_beaches(self) -> List[Dict]:
        """
        Get list of all available beaches with their codes.

        Returns:
            List of beach dictionaries
        """
        try:
            endpoint = "/prediccion/especifica/playa/"
            return self._make_request(endpoint)
        except Exception as e:
            print(f"Error fetching beaches list: {e}")
            return []

    def get_uv_forecast(self, days_ahead: int = 1) -> Optional[Dict]:
        """
        Get UV radiation forecast.

        Args:
            days_ahead: Days from today (0-4)

        Returns:
            UV forecast data
        """
        if days_ahead < 0 or days_ahead > 4:
            days_ahead = 0

        try:
            endpoint = f"/prediccion/uv/d+{days_ahead}"
            return self._make_request(endpoint)
        except Exception as e:
            print(f"Error fetching UV forecast: {e}")
            return None

    def get_municipality_forecast(self, municipality_id: str) -> Optional[Dict]:
        """
        Get forecast for a municipality.

        Args:
            municipality_id: Municipality ID (e.g., '07040' for Calvià)

        Returns:
            Municipality forecast data
        """
        try:
            endpoint = f"/prediccion/especifica/municipio/diaria/{municipality_id}"
            return self._make_request(endpoint)
        except Exception as e:
            print(f"Error fetching municipality forecast: {e}")
            return None

    def get_observation_stations(self) -> List[Dict]:
        """Get list of all observation stations."""
        try:
            endpoint = "/valores/climatologicos/inventarioestaciones/todasestaciones"
            return self._make_request(endpoint)
        except Exception as e:
            print(f"Error fetching stations: {e}")
            return []

    def get_station_observation(self, station_id: str) -> Optional[Any]:
        """
        Get latest observation data for a station.

        Args:
            station_id: Station ID (e.g., 'B242' for Palma)

        Returns:
            Current observation data
        """
        try:
            endpoint = f"/observacion/convencional/datos/estacion/{station_id}"
            result = self._make_request(endpoint)
            return result
        except Exception as e:
            print(f"Error fetching station observation: {e}")
            return None


MALLORCA_BEACH_CODES = {
    "Platja de Palma": "0704001",
    "Cala Major": "0704001",
    "Palmanova": "0705101",
    "Magaluf": "0705102",
    "Santa Ponça": "0705103",
    "Peguera": "0705104",
    "Port d'Andratx": "0704401",
    "Cala Rajada": "0705401",
    "Cala Millor": "0706201",
    "Port de Pollença": "0706401",
}


def get_beach_code(beach_name: str) -> Optional[str]:
    """Get AEMET beach code from beach name"""
    return MALLORCA_BEACH_CODES.get(beach_name)


def get_mallorca_municipalities() -> Dict[str, str]:
    """Get municipality codes for Mallorca"""
    return {
        "Palma": "07040",
        "Calvià": "07051",
        "Andratx": "07044",
        "Santanyí": "07055",
        "Manacor": "07037",
        "Felanitx": "07021",
        "Sant Llorenç des Cardassar": "07061",
        "Son Servera": "07063",
        "Capdepera": "07016",
        "Artà": "07005",
        "Alcúdia": "07001",
        "Muro": "07042",
        "Sa Pobla": "07050",
        "Pollença": "07064",
        "Esporles": "07020",
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python aemet_client.py <API_KEY>")
        print("Get your API key from: https://opendata.aemet.es")
        sys.exit(1)

    api_key = sys.argv[1]
    client = AEMETClient(api_key)

    print("=" * 60)
    print("AEMET API Client - Test")
    print("=" * 60)

    print("\n1. Getting beaches list...")
    beaches = client.get_all_beaches()
    print(f"   Found {len(beaches) if isinstance(beaches, list) else 'unknown'} beaches")

    print("\n2. Testing UV forecast...")
    uv = client.get_uv_forecast(0)
    print(f"   UV data: {'Available' if uv else 'Not available'}")

    print("\n3. Getting stations...")
    stations = client.get_observation_stations()
    print(f"   Found {len(stations) if isinstance(stations, list) else 'unknown'} stations")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)