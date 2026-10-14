"""Analytics charts for SANDAM beaches using Plotly"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
import json


BEACH_DATA = [
    {"name": "Platja de Palma", "latitude": 39.5345, "longitude": 2.7175, "max_capacity": 20000, "current_occupation": 72, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.5},
    {"name": "Cala Major", "latitude": 39.5638, "longitude": 2.6272, "max_capacity": 3500, "current_occupation": 45, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.8},
    {"name": "Portals Nous", "latitude": 39.5361, "longitude": 2.5952, "max_capacity": 4000, "current_occupation": 68, "flag_color": "green", "water_quality": "good", "water_temp": 26.0},
    {"name": "Palmanova", "latitude": 39.5201, "longitude": 2.5499, "max_capacity": 8000, "current_occupation": 85, "flag_color": "yellow", "water_quality": "excellent", "water_temp": 26.8},
    {"name": "Magaluf", "latitude": 39.5092, "longitude": 2.5305, "max_capacity": 10000, "current_occupation": 92, "flag_color": "yellow", "water_quality": "good", "water_temp": 27.0},
    {"name": "Santa Ponca", "latitude": 39.4992, "longitude": 2.4856, "max_capacity": 6000, "current_occupation": 55, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.2},
    {"name": "Peguera", "latitude": 39.4783, "longitude": 2.4527, "max_capacity": 4500, "current_occupation": 40, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.5},
    {"name": "Cala Fornells", "latitude": 39.4711, "longitude": 2.4397, "max_capacity": 2000, "current_occupation": 25, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.0},
    {"name": "Camp de Mar", "latitude": 39.4568, "longitude": 2.4186, "max_capacity": 2500, "current_occupation": 35, "flag_color": "green", "water_quality": "excellent", "water_temp": 24.8},
    {"name": "Port d'Andratx", "latitude": 39.4393, "longitude": 2.3937, "max_capacity": 3000, "current_occupation": 50, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.2},
    {"name": "Cala Conills", "latitude": 39.4203, "longitude": 2.3784, "max_capacity": 1500, "current_occupation": 20, "flag_color": "yellow", "water_quality": "good", "water_temp": 24.5},
    {"name": "Cala Rajada", "latitude": 39.7406, "longitude": 3.4652, "max_capacity": 4000, "current_occupation": 60, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.8},
    {"name": "Cala Mesquida", "latitude": 39.7184, "longitude": 3.4528, "max_capacity": 3500, "current_occupation": 45, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.5},
    {"name": "Cala Agulla", "latitude": 39.6925, "longitude": 3.4418, "max_capacity": 2500, "current_occupation": 55, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.2},
    {"name": "Platja de Muro", "latitude": 39.8089, "longitude": 3.2102, "max_capacity": 12000, "current_occupation": 78, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.5},
    {"name": "Can Picafort", "latitude": 39.7667, "longitude": 3.1497, "max_capacity": 8000, "current_occupation": 65, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.2},
    {"name": "Cala San Vicente", "latitude": 39.8875, "longitude": 3.0849, "max_capacity": 2000, "current_occupation": 30, "flag_color": "green", "water_quality": "excellent", "water_temp": 24.8},
    {"name": "Port de Pollenca", "latitude": 39.9047, "longitude": 3.0825, "max_capacity": 6000, "current_occupation": 52, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.0},
    {"name": "Cala Millor", "latitude": 39.5983, "longitude": 3.3737, "max_capacity": 10000, "current_occupation": 70, "flag_color": "green", "water_quality": "excellent", "water_temp": 26.0},
    {"name": "Cala Bona", "latitude": 39.5773, "longitude": 3.3839, "max_capacity": 4000, "current_occupation": 48, "flag_color": "green", "water_quality": "excellent", "water_temp": 25.8},
]


def load_data(data: list | None = None) -> pd.DataFrame:
    """Load beach data into DataFrame"""
    if data is None:
        data = BEACH_DATA
    return pd.DataFrame(data)


def occupation_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of occupation by beach"""
    df_sorted = df.sort_values('current_occupation', ascending=True)

    color_map = {'green': '#22c55e', 'yellow': '#eab308', 'red': '#ef4444'}

    fig = px.bar(
        df_sorted,
        x='current_occupation',
        y='name',
        orientation='h',
        color='flag_color',
        color_discrete_map=color_map,
        title='Beach Occupation (%)',
        labels={'current_occupation': 'Occupation (%)', 'name': 'Beach'},
        text='current_occupation'
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title='Occupation (%)',
        yaxis_title='',
        showlegend=True,
        legend_title='Flag Color',
        height=600
    )

    return fig


def quality_pie_chart(df: pd.DataFrame) -> go.Figure:
    """Pie chart of water quality distribution"""
    quality_counts = df['water_quality'].value_counts()

    color_map = {
        'excellent': '#3b82f6',
        'good': '#22c55e',
        'sufficient': '#eab308',
        'poor': '#ef4444',
        'unknown': '#6b7280'
    }

    fig = px.pie(
        values=quality_counts.values,
        names=quality_counts.index,
        title='Water Quality Distribution',
        color=quality_counts.index,
        color_discrete_map=color_map,
        hole=0.4
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


def flag_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Donut chart of flag color distribution"""
    flag_counts = df['flag_color'].value_counts()

    color_map = {'green': '#22c55e', 'yellow': '#eab308', 'red': '#ef4444', 'unknown': '#6b7280'}

    fig = go.Figure(data=[go.Pie(
        labels=flag_counts.index,
        values=flag_counts.values,
        hole=0.5,
        marker=dict(colors=[color_map.get(c, '#6b7280') for c in flag_counts.index])
    )])

    fig.update_layout(title='Beach Flag Status', showlegend=True)
    return fig


def temperature_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter plot of water temp vs occupation"""
    fig = px.scatter(
        df,
        x='water_temp',
        y='current_occupation',
        size='max_capacity',
        color='flag_color',
        hover_name='name',
        color_discrete_map={'green': '#22c55e', 'yellow': '#eab308', 'red': '#ef4444', 'unknown': '#6b7280'},
        title='Water Temperature vs Occupation',
        labels={
            'water_temp': 'Water Temperature (°C)',
            'current_occupation': 'Occupation (%)',
            'max_capacity': 'Max Capacity'
        }
    )

    fig.update_layout(height=500)
    return fig


def geo_scatter_map(df: pd.DataFrame) -> go.Figure:
    """Geospatial scatter map of beaches"""
    fig = px.scatter_geo(
        df,
        lat='latitude',
        lon='longitude',
        color='current_occupation',
        size='max_capacity',
        hover_name='name',
        color_continuous_scale='RdYlGn_r',
        title='Beach Locations - Occupation Map',
        projection='natural earth'
    )

    fig.update_geos(
        center=dict(lat=39.6, lon=2.9),
        projection_scale=50,
        showland=True,
        landcolor='rgb(243, 243, 243)',
        countrycolor='rgb(204, 204, 204)',
        coastlinecolor='rgb(204, 204, 204)',
        showocean=True,
        oceancolor='rgb(230, 245, 255)'
    )

    fig.update_layout(height=500)
    return fig


def create_dashboard(df: pd.DataFrame) -> go.Figure:
    """Create full dashboard with multiple charts"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Occupation by Beach',
            'Water Quality Distribution',
            'Flag Status',
            'Temperature vs Occupation'
        ),
        specs=[[{"type": "bar"}, {"type": "pie"}],
               [{"type": "pie"}, {"type": "scatter"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    df_sorted = df.sort_values('current_occupation', ascending=True)
    color_map = {'green': '#22c55e', 'yellow': '#eab308', 'red': '#ef4444'}

    fig.add_trace(
        go.Bar(
            x=df_sorted['current_occupation'],
            y=df_sorted['name'],
            orientation='h',
            marker_color=[color_map.get(c, '#6b7280') for c in df_sorted['flag_color']],
            text=df_sorted['current_occupation'],
            textposition='outside'
        ),
        row=1, col=1
    )

    quality_counts = df['water_quality'].value_counts()
    quality_colors = ['#3b82f6', '#22c55e', '#eab308', '#ef4444', '#6b7280'][:len(quality_counts)]
    fig.add_trace(
        go.Pie(labels=quality_counts.index, values=quality_counts.values, hole=0.4, marker=dict(colors=quality_colors)),
        row=1, col=2
    )

    flag_counts = df['flag_color'].value_counts()
    flag_colors = [color_map.get(c, '#6b7280') for c in flag_counts.index]
    fig.add_trace(
        go.Pie(labels=flag_counts.index, values=flag_counts.values, hole=0.5, marker=dict(colors=flag_colors)),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df['water_temp'],
            y=df['current_occupation'],
            mode='markers',
            marker=dict(
                size=df['max_capacity'] / 200,
                color=[color_map.get(c, '#6b7280') for c in df['flag_color']]
            ),
            text=df['name'],
            textposition='top center'
        ),
        row=2, col=2
    )

    fig.update_layout(
        height=800,
        title_text='SANDAM Beach Analytics Dashboard',
        showlegend=False
    )

    fig.update_xaxes(title_text='Occupation (%)', row=1, col=1)
    fig.update_yaxes(title_text='', row=1, col=1, tickfont=dict(size=8))
    fig.update_xaxes(title_text='Water Temp (°C)', row=2, col=2)
    fig.update_yaxes(title_text='Occupation (%)', row=2, col=2)

    return fig


def save_chart(fig: go.Figure, filepath: str) -> None:
    """Save chart to HTML file"""
    from pathlib import Path
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output_path)
    print(f"Chart saved to {output_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("SANDAM - Plotly Charts Generator")
    print("=" * 60)

    df = load_data()
    print(f"\nLoaded {len(df)} beaches")

    print("\n1. Creating occupation bar chart...")
    fig1 = occupation_bar_chart(df)
    save_chart(fig1, "notebooks/chart_occupation.html")

    print("\n2. Creating quality pie chart...")
    fig2 = quality_pie_chart(df)
    save_chart(fig2, "notebooks/chart_quality.html")

    print("\n3. Creating flag distribution chart...")
    fig3 = flag_distribution_chart(df)
    save_chart(fig3, "notebooks/chart_flags.html")

    print("\n4. Creating temperature scatter plot...")
    fig4 = temperature_scatter(df)
    save_chart(fig4, "notebooks/chart_temperature.html")

    print("\n5. Creating geo scatter map...")
    fig5 = geo_scatter_map(df)
    save_chart(fig5, "notebooks/chart_geo.html")

    print("\n6. Creating full dashboard...")
    fig_dashboard = create_dashboard(df)
    save_chart(fig_dashboard, "notebooks/dashboard_analytics.html")

    print("\nAll charts generated successfully!")