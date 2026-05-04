"""
SANDAM Dashboard - Streamlit App
Demo para visualización de datos de playas
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="SANDAM Dashboard",
    page_icon="🏖️",
    layout="wide"
)

API_BASE = "http://localhost:8000/api/v1"


@st.cache_data(ttl=60)
def fetch_beaches():
    try:
        response = requests.get(f"{API_BASE}/beaches/", timeout=5)
        return response.json().get("beaches", [])
    except Exception as e:
        st.error(f"Error conectando con API: {e}")
        return []


@st.cache_data(ttl=60)
def fetch_summary():
    try:
        response = requests.get(f"{API_BASE}/dashboard/summary", timeout=5)
        return response.json()
    except Exception:
        return {}


st.title("🏖️ SANDAM - Dashboard de Playas")

beaches = fetch_beaches()
summary = fetch_summary()

if beaches:
    st.sidebar.header("Filtros")

    regions = list(set([b.get("region") for b in beaches if b.get("region")]))
    selected_region = st.sidebar.selectbox("Región", ["Todas"] + regions)

    flags = st.sidebar.multiselect(
        "Bandera",
        ["green", "yellow", "red"],
        default=["green", "yellow", "red"]
    )

    filtered_beaches = [
        b for b in beaches
        if (selected_region == "Todas" or b.get("region") == selected_region)
        and b.get("flag_color") in flags
    ]

    st.header("📊 KPIs")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Playas", len(filtered_beaches))
    with col2:
        if summary:
            st.metric("Ocupación Media", f"{summary.get('avg_occupation', 0)}%")
        else:
            avg_occ = sum(b.get("current_occupation", 0) for b in filtered_beaches) / len(filtered_beaches) if filtered_beaches else 0
            st.metric("Ocupación Media", f"{avg_occ:.0f}%")
    with col3:
        if summary:
            st.metric("Alertas Activas", summary.get("active_alerts", 0))
        else:
            red_count = sum(1 for b in filtered_beaches if b.get("flag_color") == "red")
            st.metric("Banderas Rojas", red_count)
    with col4:
        excellent = sum(1 for b in filtered_beaches if b.get("water_quality") == "excellent")
        st.metric("Calidad Excelente", excellent)

    st.header("📍 Mapa de Playas")

    df_map = pd.DataFrame(filtered_beaches)
    if not df_map.empty and "latitude" in df_map.columns and "longitude" in df_map.columns:
        st.map(df_map[["latitude", "longitude"]])
    else:
        st.info("No hay datos de geolocalización disponibles")

    col1, col2 = st.columns(2)

    with col1:
        st.header("🏷️ Distribución de Banderas")
        flag_counts = {}
        for b in filtered_beaches:
            flag = b.get("flag_color", "unknown")
            flag_counts[flag] = flag_counts.get(flag, 0) + 1
        fig_flags = px.pie(
            names=list(flag_counts.keys()),
            values=list(flag_counts.values()),
            title="Banderas por color",
            color_discrete_map={"green": "#22C55E", "yellow": "#EAB308", "red": "#EF4444", "unknown": "#6B7280"}
        )
        st.plotly_chart(fig_flags, use_container_width=True)

    with col2:
        st.header("🌊 Calidad del Agua")
        quality_counts = {}
        for b in filtered_beaches:
            quality = b.get("water_quality", "unknown")
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        fig_quality = px.pie(
            names=list(quality_counts.keys()),
            values=list(quality_counts.values()),
            title="Distribución de calidad",
            color_discrete_map={"excellent": "#3B82F6", "good": "#22C55E", "sufficient": "#EAB308", "poor": "#EF4444", "unknown": "#6B7280"}
        )
        st.plotly_chart(fig_quality, use_container_width=True)

    st.header("📈 Playas por Ocupación")
    df_occ = pd.DataFrame(filtered_beaches)
    if not df_occ.empty and "name" in df_occ.columns:
        df_occ = df_occ.sort_values("current_occupation", ascending=False)
        fig_bar = px.bar(
            df_occ.head(15),
            x="name",
            y="current_occupation",
            color="flag_color",
            title="Top 15 Playas por Ocupación",
            color_discrete_map={"green": "#22C55E", "yellow": "#EAB308", "red": "#EF4444", "unknown": "#6B7280"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.header("🏖️ Listado de Playas")
    st.dataframe(
        filtered_beaches,
        column_config={
            "name": "Nombre",
            "region": "Región",
            "current_occupation": "Ocupación (%)",
            "flag_color": "Bandera",
            "water_quality": "Calidad",
            "has_lifeguard": "Socorrista",
            "has_shade": "Sombra"
        },
        hide_index=True,
        use_container_width=True
    )

else:
    st.warning("No hay datos disponibles. Asegúrate de que la API esté corriendo.")
    st.info("Ejecuta: uvicorn src.main:app --reload")

st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")