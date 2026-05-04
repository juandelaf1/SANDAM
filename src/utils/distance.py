import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def sort_by_distance(beaches: list, lat: float, lon: float, key: str = "distance_km") -> list:
    for beach in beaches:
        beach[key] = haversine_distance(
            lat, lon,
            beach["latitude"], beach["longitude"]
        )

    return sorted(beaches, key=lambda x: x.get(key, float("inf")))


def is_within_radius(lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float) -> bool:
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_km


def format_distance(distance_km: float) -> str:
    if distance_km < 1:
        return f"{int(distance_km * 1000)} m"
    else:
        return f"{distance_km:.1f} km"