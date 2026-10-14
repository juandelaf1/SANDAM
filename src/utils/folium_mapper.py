"""Interactive maps for SANDAM beaches using Folium"""

import folium
from folium.plugins import MarkerCluster, HeatMap
from pathlib import Path
import json


BEACH_DATA = [
    {"name": "Platja de Palma", "latitude": 39.5345, "longitude": 2.7175, "region": "Mallorca", "max_capacity": 20000, "current_occupation": 72, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.5, "has_lifeguard": True, "has_parking": True},
    {"name": "Cala Major", "latitude": 39.5638, "longitude": 2.6272, "region": "Mallorca", "max_capacity": 3500, "current_occupation": 45, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.8, "has_lifeguard": True, "has_parking": True},
    {"name": "Portals Nous", "latitude": 39.5361, "longitude": 2.5952, "region": "Mallorca", "max_capacity": 4000, "current_occupation": 68, "flag_color": "green", "water_quality": "good", "water_temp": 26.0, "has_lifeguard": True, "has_parking": True},
    {"name": "Palmanova", "latitude": 39.5201, "longitude": 2.5499, "region": "Mallorca", "max_capacity": 8000, "current_occupation": 85, "flag_color": "yellow", "water_quality": "excellent", "water_temp": 26.8, "has_lifeguard": True, "has_parking": True},
    {"name": "Magaluf", "latitude": 39.5092, "longitude": 2.5305, "region": "Mallorca", "max_capacity": 10000, "current_occupation": 92, "flag_color": "yellow", "water_quality": "good", "water_temp": 27.0, "has_lifeguard": True, "has_parking": True},
    {"name": "Santa Ponca", "latitude": 39.4992, "longitude": 2.4856, "region": "Mallorca", "max_capacity": 6000, "current_occupation": 55, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.2, "has_lifeguard": True, "has_parking": True},
    {"name": "Peguera", "latitude": 39.4783, "longitude": 2.4527, "region": "Mallorca", "max_capacity": 4500, "current_occupation": 40, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.5, "has_lifeguard": True, "has_parking": True},
    {"name": "Cala Fornells", "latitude": 39.4711, "longitude": 2.4397, "region": "Mallorca", "max_capacity": 2000, "current_occupation": 25, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.0, "has_lifeguard": True, "has_parking": True},
    {"name": "Camp de Mar", "latitude": 39.4568, "longitude": 2.4186, "region": "Mallorca", "max_capacity": 2500, "current_occupation": 35, "flag_color": "green", "water_quality": "excellent", "water_temp": 24.8, "has_lifeguard": True, "has_parking": True},
    {"name": "Port d'Andratx", "latitude": 39.4393, "longitude": 2.3937, "region": "Mallorca", "max_capacity": 3000, "current_occupation": 50, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.2, "has_lifeguard": True, "has_parking": True},
    {"name": "Cala Conills", "latitude": 39.4203, "longitude": 2.3784, "region": "Mallorca", "max_capacity": 1500, "current_occupation": 20, "flag_color": "yellow", "water_quality": "good", "water_temp": 24.5, "has_lifeguard": True, "has_parking": True},
    {"name": "Cala Rajada", "latitude": 39.7406, "longitude": 3.4652, "region": "Mallorca", "max_capacity": 4000, "current_occupation": 60, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.8, "has_lifeguard": True, "has_parking": True},
    {"name": "Cala Mesquida", "latitude": 39.7184, "longitude": 3.4528, "region": "Mallorca", "max_capacity": 3500, "current_occupation": 45, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.5, "has_lifeguard": True, "has_parking": True},
    {"name": "Cala Agulla", "latitude": 39.6925, "longitude": 3.4418, "region": "Mallorca", "max_capacity": 2500, "current_occupation": 55, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.2, "has_lifeguard": True, "has_parking": True},
    {"name": "Platja de Muro", "latitude": 39.8089, "longitude": 3.2102, "region": "Mallorca", "max_capacity": 12000, "current_occupation": 78, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.5, "has_lifeguard": True, "has_parking": True},
    {"name": "Can Picafort", "latitude": 39.7667, "longitude": 3.1497, "region": "Mallorca", "max_capacity": 8000, "current_occupation": 65, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.2, "has_lifeguard": True, "has_parking": True},
    {"name": "Cala San Vicente", "latitude": 39.8875, "longitude": 3.0849, "region": "Mallorca", "max_capacity": 2000, "current_occupation": 30, "flag_color": "green", "water_quality": "excellent", "water_temp": 24.8, "has_lifeguard": True, "has_parking": True},
    {"name": "Port de Pollenca", "latitude": 39.9047, "longitude": 3.0825, "region": "Mallorca", "max_capacity": 6000, "current_occupation": 52, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.0, "has_lifeguard": True, "has_parking": True},
    {"name": "Cala Millor", "latitude": 39.5983, "longitude": 3.3737, "region": "Mallorca", "max_capacity": 10000, "current_occupation": 70, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.0, "has_lifeguard": True, "has_parking": True},
    {"name": "Cala Bona", "latitude": 39.5773, "longitude": 3.3839, "region": "Mallorca", "max_capacity": 4000, "current_occupation": 48, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.8, "has_lifeguard": True, "has_parking": True},
]


FLAG_COLORS = {
    "green": "green",
    "yellow": "orange",
    "red": "red",
    "unknown": "gray"
}


QUALITY_ICONS = {
    "excellent": "blue",
    "good": "lightblue",
    "sufficient": "lightgray",
    "poor": "red",
    "unknown": "gray"
}


def create_beach_popup(beach: dict) -> str:
    """Create HTML popup for a beach"""
    flag_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴", "unknown": "⚪"}

    return f"""
    <div style="font-family: Arial, sans-serif; width: 200px;">
        <h4 style="margin: 0 0 10px 0; color: #333;">{beach['name']}</h4>
        <p><strong>Region:</strong> {beach['region']}</p>
        <p><strong>Ocupation:</strong> {beach['current_occupation']}%</p>
        <p><strong>Flag:</strong> {flag_emoji.get(beach['flag_color'], '⚪')} {beach['flag_color'].upper()}</p>
        <p><strong>Water Quality:</strong> {beach['water_quality'].upper()}</p>
        <p><strong>Water Temp:</strong> {beach['water_temp']}°C</p>
        <p><strong>Max Capacity:</strong> {beach['max_capacity']}</p>
        <p><strong>Services:</strong>
            {"🚨" if beach['has_lifeguard'] else ""}
            {"🅿️" if beach['has_parking'] else ""}
        </p>
    </div>
    """


def create_basic_map(beaches: list[dict] | None = None, center: tuple = (39.62, 2.95), zoom: int = 10) -> folium.Map:
    """Create basic map with beach markers"""
    if beaches is None:
        beaches = BEACH_DATA

    m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")

    for beach in beaches:
        color = FLAG_COLORS.get(beach['flag_color'], 'gray')

        folium.Marker(
            location=[beach['latitude'], beach['longitude']],
            popup=create_beach_popup(beach),
            tooltip=f"{beach['name']} ({beach['current_occupation']}%)",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)

    return m


def create_clustered_map(beaches: list[dict] | None = None) -> folium.Map:
    """Create map with clustered markers"""
    if beaches is None:
        beaches = BEACH_DATA

    m = folium.Map(location=(39.62, 2.95), zoom_start=10, tiles="OpenStreetMap")

    cluster = MarkerCluster(name="Beaches")

    for beach in beaches:
        color = FLAG_COLORS.get(beach['flag_color'], 'gray')

        folium.Marker(
            location=[beach['latitude'], beach['longitude']],
            popup=create_beach_popup(beach),
            tooltip=f"{beach['name']}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(cluster)

    cluster.add_to(m)

    folium.LayerControl().add_to(m)

    return m


def create_heatmap(beaches: list[dict] | None = None) -> folium.Map:
    """Create map with heatmap layer showing occupation density"""
    if beaches is None:
        beaches = BEACH_DATA

    m = folium.Map(location=(39.62, 2.95), zoom_start=10, tiles="OpenStreetMap")

    heat_data = [[b['latitude'], b['longitude'], b['current_occupation']/100] for b in beaches]
    HeatMap(heat_data, radius=25, blur=15, name="Occupation Heatmap").add_to(m)

    for beach in beaches:
        color = FLAG_COLORS.get(beach['flag_color'], 'gray')
        folium.Marker(
            location=[beach['latitude'], beach['longitude']],
            popup=create_beach_popup(beach),
            tooltip=f"{beach['name']}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)

    folium.LayerControl().add_to(m)

    return m


def create_full_dashboard_map(beaches: list[dict] | None = None) -> folium.Map:
    """Create full dashboard with multiple layers"""
    if beaches is None:
        beaches = BEACH_DATA

    m = folium.Map(location=(39.62, 2.95), zoom_start=10, tiles=None)

    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
    folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(m)
    folium.TileLayer('cartodbdark_matter', name='CartoDB Dark').add_to(m)

    fg_markers = folium.FeatureGroup(name="Beach Markers")
    for beach in beaches:
        color = FLAG_COLORS.get(beach['flag_color'], 'gray')
        folium.Marker(
            location=[beach['latitude'], beach['longitude']],
            popup=create_beach_popup(beach),
            tooltip=f"{beach['name']}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(fg_markers)
    fg_markers.add_to(m)

    fg_heatmap = folium.FeatureGroup(name="Occupation Heatmap", show=False)
    heat_data = [[b['latitude'], b['longitude'], b['current_occupation']/100] for b in beaches]
    HeatMap(heat_data, radius=25, blur=15).add_to(fg_heatmap)
    fg_heatmap.add_to(m)

    folium.LayerControl().add_to(m)

    return m


def save_map(m: folium.Map, filepath: str) -> None:
    """Save map to HTML file"""
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    m.save(output_path)
    print(f"Map saved to {output_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("SANDAM - Folium Map Generator")
    print("=" * 60)

    print("\n1. Creating basic map...")
    basic_map = create_basic_map()
    save_map(basic_map, "notebooks/mapa_playas_basic.html")

    print("\n2. Creating clustered map...")
    cluster_map = create_clustered_map()
    save_map(cluster_map, "notebooks/mapa_playas_cluster.html")

    print("\n3. Creating heatmap...")
    heatmap = create_heatmap()
    save_map(heatmap, "notebooks/mapa_playas_heatmap.html")

    print("\n4. Creating full dashboard map...")
    dashboard_map = create_full_dashboard_map()
    save_map(dashboard_map, "notebooks/mapa_playas_dashboard.html")

    print("\nAll maps generated successfully!")