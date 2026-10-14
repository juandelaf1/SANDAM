"""Geospatial processing utilities for SANDAM beaches using geopandas"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from pathlib import Path


BEACH_DATA = [
    {"name": "Platja de Palma", "latitude": 39.5345, "longitude": 2.7175, "region": "Mallorca", "max_capacity": 20000, "current_occupation": 72, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.5},
    {"name": "Cala Major", "latitude": 39.5638, "longitude": 2.6272, "region": "Mallorca", "max_capacity": 3500, "current_occupation": 45, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.8},
    {"name": "Portals Nous", "latitude": 39.5361, "longitude": 2.5952, "region": "Mallorca", "max_capacity": 4000, "current_occupation": 68, "flag_color": "green", "water_quality": "good", "water_temp": 26.0},
    {"name": "Palmanova", "latitude": 39.5201, "longitude": 2.5499, "region": "Mallorca", "max_capacity": 8000, "current_occupation": 85, "flag_color": "yellow", "water_quality": "excellent", "water_temp": 26.8},
    {"name": "Magaluf", "latitude": 39.5092, "longitude": 2.5305, "region": "Mallorca", "max_capacity": 10000, "current_occupation": 92, "flag_color": "yellow", "water_quality": "good", "water_temp": 27.0},
    {"name": "Santa Ponça", "latitude": 39.4992, "longitude": 2.4856, "region": "Mallorca", "max_capacity": 6000, "current_occupation": 55, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.2},
    {"name": "Peguera", "latitude": 39.4783, "longitude": 2.4527, "region": "Mallorca", "max_capacity": 4500, "current_occupation": 40, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.5},
    {"name": "Cala Fornells", "latitude": 39.4711, "longitude": 2.4397, "region": "Mallorca", "max_capacity": 2000, "current_occupation": 25, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.0},
    {"name": "Camp de Mar", "latitude": 39.4568, "longitude": 2.4186, "region": "Mallorca", "max_capacity": 2500, "current_occupation": 35, "flag_color": "green", "water_quality": "excellent", "water_temp": 24.8},
    {"name": "Port d'Andratx", "latitude": 39.4393, "longitude": 2.3937, "region": "Mallorca", "max_capacity": 3000, "current_occupation": 50, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.2},
    {"name": "Cala conills", "latitude": 39.4203, "longitude": 2.3784, "region": "Mallorca", "max_capacity": 1500, "current_occupation": 20, "flag_color": "yellow", "water_quality": "good", "water_temp": 24.5},
    {"name": "Cala Rajada", "latitude": 39.7406, "longitude": 3.4652, "region": "Mallorca", "max_capacity": 4000, "current_occupation": 60, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.8},
    {"name": "Cala Mesquida", "latitude": 39.7184, "longitude": 3.4528, "region": "Mallorca", "max_capacity": 3500, "current_occupation": 45, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.5},
    {"name": "Cala Agulla", "latitude": 39.6925, "longitude": 3.4418, "region": "Mallorca", "max_capacity": 2500, "current_occupation": 55, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.2},
    {"name": "Platja de Muro", "latitude": 39.8089, "longitude": 3.2102, "region": "Mallorca", "max_capacity": 12000, "current_occupation": 78, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.5},
    {"name": "Can Picafort", "latitude": 39.7667, "longitude": 3.1497, "region": "Mallorca", "max_capacity": 8000, "current_occupation": 65, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.2},
    {"name": "Cala San Vicente", "latitude": 39.8875, "longitude": 3.0849, "region": "Mallorca", "max_capacity": 2000, "current_occupation": 30, "flag_color": "green", "water_quality": "excellent", "water_temp": 24.8},
    {"name": "Port de Pollença", "latitude": 39.9047, "longitude": 3.0825, "region": "Mallorca", "max_capacity": 6000, "current_occupation": 52, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.0},
    {"name": "Cala Millor", "latitude": 39.5983, "longitude": 3.3737, "region": "Mallorca", "max_capacity": 10000, "current_occupation": 70, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.0},
    {"name": "Cala Bona", "latitude": 39.5773, "longitude": 3.3839, "region": "Mallorca", "max_capacity": 4000, "current_occupation": 48, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.8},
]


def create_beaches_geodataframe(data: list[dict] | None = None) -> gpd.GeoDataFrame:
    """Create GeoDataFrame from beach data with Point geometries"""
    if data is None:
        data = BEACH_DATA

    df = pd.DataFrame(data)

    geometry = [Point(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]

    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    return gdf


def calculate_distances(gdf: gpd.GeoDataFrame, lat: float, lon: float) -> pd.DataFrame:
    """Calculate distances from a given point to all beaches using haversine approximation"""
    from math import radians, cos, sin, asin, sqrt

    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return c * 6371

    distances = []
    for idx, row in gdf.iterrows():
        dist = haversine(lon, lat, row.geometry.x, row.geometry.y)
        distances.append(dist)

    result = gdf.copy()
    result['distance_km'] = distances
    return result.sort_values('distance_km')


def create_buffer_zones(gdf: gpd.GeoDataFrame, radius_km: float = 5) -> gpd.GeoDataFrame:
    """Create buffer zones around each beach (approx 1 degree = 111km at equator)"""
    buffer_degrees = radius_km / 111.0

    gdf = gdf.copy()
    gdf['buffer_zone'] = gdf.geometry.buffer(buffer_degrees)

    return gdf


def find_nearby_beaches(gdf: gpd.GeoDataFrame, lat: float, lon: float, max_distance_km: float = 10) -> gpd.GeoDataFrame:
    """Find beaches within a maximum distance from a point"""
    gdf_with_distances = calculate_distances(gdf, lat, lon)
    return gdf_with_distances[gdf_with_distances['distance_km'] <= max_distance_km]


def export_to_geojson(gdf: gpd.GeoDataFrame, filepath: str) -> None:
    """Export GeoDataFrame to GeoJSON file"""
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver="GeoJSON")
    print(f"Exported to {output_path}")


def get_beaches_by_quality(gdf: gpd.GeoDataFrame, min_quality: str) -> gpd.GeoDataFrame:
    """Filter beaches by minimum water quality"""
    quality_order = {'excellent': 0, 'good': 1, 'sufficient': 2, 'poor': 3, 'unknown': 4}
    min_level = quality_order.get(min_quality, 0)
    return gdf[gdf['water_quality'].apply(lambda x: quality_order.get(x, 4) <= min_level)]


def get_beaches_by_occupation(gdf: gpd.GeoDataFrame, max_occupation: int) -> gpd.GeoDataFrame:
    """Filter beaches by maximum occupation percentage"""
    return gdf[gdf['current_occupation'] <= max_occupation]


def get_statistics(gdf: gpd.GeoDataFrame) -> dict:
    """Get statistics about beaches"""
    return {
        "total_beaches": len(gdf),
        "avg_occupation": gdf['current_occupation'].mean(),
        "min_occupation": gdf['current_occupation'].min(),
        "max_occupation": gdf['current_occupation'].max(),
        "quality_distribution": gdf['water_quality'].value_counts().to_dict(),
        "flag_distribution": gdf['flag_color'].value_counts().to_dict(),
        "avg_water_temp": gdf['water_temp'].mean(),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("SANDAM - Geopandas Processing Demo")
    print("=" * 60)

    gdf = create_beaches_geodataframe()
    print(f"\nCreated GeoDataFrame with {len(gdf)} beaches")
    print(f"CRS: {gdf.crs}")

    print("\n" + "-" * 40)
    print("Statistics:")
    print("-" * 40)
    stats = get_statistics(gdf)
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "-" * 40)
    print("Find beaches near Palma (39.57, 2.98):")
    print("-" * 40)
    nearby = find_nearby_beaches(gdf, 39.57, 2.98, max_distance_km=15)
    for _, row in nearby.iterrows():
        print(f"  {row['name']} - {row['distance_km']:.1f} km")

    print("\n" + "-" * 40)
    print("Beaches with excellent quality:")
    print("-" * 40)
    excellent = get_beaches_by_quality(gdf, 'excellent')
    for _, row in excellent.iterrows():
        print(f"  {row['name']} ({row['current_occupation']}% occupation)")

    print("\n" + "-" * 40)
    print("Exporting to GeoJSON...")
    print("-" * 40)
    export_to_geojson(gdf, "data/playas_mallorca.geojson")

    print("\nProcessing complete!")