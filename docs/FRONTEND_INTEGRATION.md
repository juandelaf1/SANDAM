# 🔌 SANDAM - Guía de Integración Frontend

Cómo conectar SANDAM con aplicaciones frontend (Streamlit, Dash, React, etc.)

---

## 📦 Instalación del Cliente

### Python (Streamlit/Dash)

```python
import requests
import pandas as pd

BASE_URL = "http://localhost:8000/api/v1"
```

### JavaScript (React/Vue)

```javascript
const API_BASE = "http://localhost:8000/api/v1";

// Función helper
async function fetchAPI(endpoint, params = {}) {
  const response = await fetch(`${API_BASE}${endpoint}?${new URLSearchParams(params)}`);
  return response.json();
}
```

---

## 🎯 Casos de Uso Comunes

### 1. Mapa de Playas con Streamlit

```python
import streamlit as st
import requests

st.title("🏖️ SANDAM - Mapa de Playas")

# Fetch todas las playas
response = requests.get("http://localhost:8000/api/v1/beaches/")
beaches = response.json()

# Mostrar en mapa
st.map(beaches, latitude="latitude", longitude="longitude")
```

### 2. Tarjetas de Playa

```python
import streamlit as st

for beach in beaches:
    with st.card():
        st.header(beach["name"])
        st.metric("Ocupación", f"{beach['current_occupation']}%")
        st.write(f"🏷️ Bandera: {beach['flag_color']}")
        st.write(f"🌊 Calidad: {beach['water_quality']}")
```

### 3. Gráfico de Ocupación

```python
import plotly.express as px

# Preparar datos
df = pd.DataFrame(beaches)
df = df.sort_values("current_occupation", ascending=False)

# Gráfico de barras
fig = px.bar(
    df.head(20),
    x="name",
    y="current_occupation",
    color="flag_color",
    title="Top 20 Playas por Ocupación"
)
st.plotly_chart(fig)
```

### 4. KPIs con Métricas

```python
# Resumen del dashboard
summary = requests.get("http://localhost:8000/api/v1/dashboard/summary").json()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Playas", summary["total_beaches"])
col2.metric("Ocupación Media", f"{summary['avg_occupation']}%")
col3.metric("Alertas Activas", summary["active_alerts"])
col4.metric("Calidad Excelente", summary["quality_distribution"]["excellent"])
```

### 5. Distribución de Calidad (Pie Chart)

```python
import plotly.express as px

quality = summary["quality_distribution"]
df_quality = pd.DataFrame(list(quality.items()), columns=["Calidad", "Cantidad"])

fig = px.pie(df_quality, values="Cantidad", names="Calidad", title="Distribución Calidad Agua")
st.plotly_chart(fig)
```

### 6. Playas Cercanas con Métrica de Distancia

```python
# Obtener playas cercanas
nearby = requests.get(
    "http://localhost:8000/api/v1/beaches/nearby",
    params={"lat": 41.38, "lon": 2.19, "radius_km": 10}
).json()

for beach in nearby["beaches"]:
    st.write(f"📍 {beach['name']} - {beach['distance_km']:.2f} km")
```

### 7. Búsqueda Inteligente con Alternativas

```python
# Usuario busca una playa que tiene problemas
search = requests.get(
    "http://localhost:8000/api/v1/beaches/search",
    params={
        "name": "Barceloneta",
        "lat": 41.38,
        "lon": 2.19,
        "max_occupation": 50
    }
).json()

# Si hay alternativas, mostrar
if search.get("recommendation"):
    st.warning(f"⚠️ {search['recommendation']['reason']}")
    for alt in search["recommendation"]["alternatives"]:
        st.success(f"✅ {alt['beach']['name']} ({alt['distance_km']:.1f} km) - Score: {alt['score']}")
```

### 8. Recomendaciones de Seguridad

```python
# Obtener recomendaciones de una playa específica
beach_id = "550e8400-e29b-41d4-a716-446655440000"
recs = requests.get(f"http://localhost:8000/api/v1/beaches/{beach_id}/recommendations").json()

for rec in recs["recommendations"]:
    if rec["level"] == "safe":
        st.success(rec["message"])
    elif rec["level"] == "caution":
        st.warning(rec["message"])
    elif rec["level"] == "danger":
        st.error(rec["message"])
```

### 9. Tabla Filtrable

```python
import streamlit as st

# Filtros en sidebar
st.sidebar.header("Filtros")
flag_filter = st.sidebar.selectbox("Bandera", ["green", "yellow", "red"])
quality_filter = st.sidebar.selectbox("Calidad", ["excellent", "good", "sufficient"])

# Aplicar filtros
filtered = [
    b for b in beaches
    if b["flag_color"] == flag_filter and b["water_quality"] >= quality_filter
]

st.dataframe(filtered)
```

---

## 🔌 Integración con React

```jsx
import React, { useState, useEffect } from 'react';

function BeachMap() {
  const [beaches, setBeaches] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/beaches/')
      .then(res => res.json())
      .then(data => setBeaches(data));
  }, []);

  return (
    <div>
      {beaches.map(beach => (
        <BeachCard key={beach.id} beach={beach} />
      ))}
    </div>
  );
}

function BeachCard({ beach }) {
  const flagColors = {
    green: '🟢',
    yellow: '🟡',
    red: '🔴',
    unknown: '⚪'
  };

  return (
    <div className="beach-card">
      <h3>{beach.name}</h3>
      <span> {flagColors[beach.flag_color]} {beach.flag_color}</span>
      <p>Ocupación: {beach.current_occupation}%</p>
    </div>
  );
}
```

---

## 📊 Datos para Charts

### Distribución Banderas

```bash
GET /api/v1/dashboard/summary
```

Usar `flag_distribution` para pie chart.

### Serie de Ocupación (para time series)

```bash
GET /api/v1/dashboard/analytics/occupation?days=30
```

### Alertas por Playa

```bash
GET /api/v1/dashboard/alerts
```

---

## ⚠️ Manejo de Errores

```python
import requests
from requests.exceptions import ConnectionError

def safe_fetch(url, default=[]):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except (ConnectionError, requests.exceptions.Timeout):
        return default
    except Exception as e:
        st.error(f"Error: {e}")
        return default
```

---

## 🎨 Estilos Recomendados

### Colores por Flag

| Flag | Color | Hex |
|------|-------|-----|
| green | Verde | #22C55E |
| yellow | Amarillo | #EAB308 |
| red | Rojo | #EF4444 |
| unknown | Gris | #6B7280 |

### Colores por Calidad

| Quality | Color | Hex |
|---------|-------|-----|
| excellent | Azul | #3B82F6 |
| good | Verde | #22C55E |
| sufficient | Amarillo | #EAB308 |
| poor | Rojo | #EF4444 |
| unknown | Gris | #6B7280 |

---

## 📡 WebSockets (Futuro)

Para datos en tiempo real, implementar WebSocket:

```python
# Endpoint futuro
@app.websocket("/ws/beaches")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await get_live_beach_data()
        await websocket.send_json(data)
        await asyncio.sleep(30)
```

---

## 🔐 Autenticación (V2)

En versión futura, usar JWT:

```python
import requests

# Obtener token
token = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "user", "password": "pass"}
).json()["access_token"]

# Headers con token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/dashboard/summary", headers=headers)
```

---

## 📚 Recursos

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json