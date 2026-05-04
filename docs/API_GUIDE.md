# 📖 SANDAM API Guide

Guía completa de endpoints y ejemplos de uso.

## 🌐 Base URL

```
http://localhost:8000/api/v1
```

## 📋 Endpoints

---

### 1. BEACHES (CRUD)

#### 1.1 Crear una playa

```
POST /beaches/
```

**Request Body:**

```json
{
  "name": "Platja de la Barceloneta",
  "region": "Cataluña",
  "latitude": 41.3803,
  "longitude": 2.1898,
  "max_capacity": 15000,
  "current_occupation": 45,
  "water_temp": 22.5,
  "air_temp": 28.0,
  "uv_index": 7,
  "wind_speed": 12.5,
  "wave_height": 0.5,
  "tide": "baja",
  "flag_color": "green",
  "jellyfish_present": false,
  "sargasso_level": 0,
  "posidonia_present": false,
  "water_quality": "excellent",
  "has_kiosk": true,
  "has_shade": true,
  "has_showers": true,
  "has_parking": true,
  "has_accessibility": true,
  "has_lifeguard": true
}
```

**Response (201):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Platja de la Barceloneta",
  "region": "Cataluña",
  "latitude": 41.3803,
  "longitude": 2.1898,
  "max_capacity": 15000,
  "current_occupation": 45,
  "water_temp": 22.5,
  "air_temp": 28.0,
  "uv_index": 7,
  "wind_speed": 12.5,
  "wave_height": 0.5,
  "tide": "baja",
  "flag_color": "green",
  "jellyfish_present": false,
  "jellyfish_species": null,
  "sargasso_level": 0,
  "posidonia_present": false,
  "water_quality": "excellent",
  "e_coli_count": null,
  "enterococci_count": null,
  "has_kiosk": true,
  "has_shade": true,
  "has_showers": true,
  "has_parking": true,
  "has_accessibility": true,
  "has_lifeguard": true,
  "data_status": "live",
  "last_updated": "2026-05-04T12:00:00Z",
  "created_at": "2026-05-04T12:00:00Z"
}
```

---

#### 1.2 Listar todas las playas (con filtros)

```
GET /beaches/
```

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `skip` | int | Offset para paginación (default: 0) |
| `limit` | int | Límite de resultados (default: 100) |
| `region` | str | Filtrar por región |
| `flag_color` | str | Filtrar por color de bandera |
| `water_quality` | str | Filtrar por calidad del agua |
| `has_lifeguard` | bool | Filtrar por presencia de socorrista |
| `has_shade` | bool | Filtrar por sombras |
| `occupation_min` | int | Ocupación mínima (%) |
| `occupation_max` | int | Ocupación máxima (%) |

**Ejemplos:**

```bash
# Todas las playas
GET /beaches/

# Playas con bandera verde
GET /beaches/?flag_color=green

# Playas con socorrista y sombras
GET /beaches/?has_lifeguard=true&has_shade=true

# Playas con ocupación menor al 50%
GET /beaches/?occupation_max=50

# Calidad de agua excelente
GET /beaches/?water_quality=excellent
```

---

#### 1.3 Obtener una playa por ID

```
GET /beaches/{id}
```

**Response (200):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Platja de la Barceloneta",
  "region": "Cataluña",
  "latitude": 41.3803,
  "longitude": 2.1898,
  ...
  "data_status": "live",
  "last_updated": "2026-05-04T12:00:00Z",
  "created_at": "2026-05-04T12:00:00Z"
}
```

---

#### 1.4 Actualizar una playa

```
PUT /beaches/{id}
```

**Request Body (todos los campos opcionales):**

```json
{
  "current_occupation": 75,
  "flag_color": "yellow",
  "water_temp": 23.0
}
```

**Response (200):** Playa actualizada

---

#### 1.5 Eliminar una playa

```
DELETE /beaches/{id}
```

**Response (204):** Sin contenido

---

### 2. BÚSQUEDA Y RECOMENDACIONES

#### 2.1 Playas cercanas

```
GET /beaches/nearby
```

**Query Parameters:**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `lat` | float | Sí | Latitud |
| `lon` | float | Sí | Longitud |
| `radius_km` | float | No | Radio de búsqueda (default: 10) |
| `limit` | int | No | Límite de resultados (default: 10) |

**Ejemplo:**

```bash
GET /beaches/nearby?lat=41.38&lon=2.19&radius_km=15
```

**Response:**

```json
{
  "requested_lat": 41.38,
  "requested_lon": 2.19,
  "radius_km": 15,
  "beaches": [
    {
      "id": "...",
      "name": "Platja de la Barceloneta",
      "latitude": 41.3803,
      "longitude": 2.1898,
      "distance_km": 0.5,
      ...
    },
    ...
  ]
}
```

---

#### 2.2 Mejores playas cercanas

```
GET /beaches/best-nearby
```

**Query Parameters:**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `lat` | float | Sí | Latitud |
| `lon` | float | Sí | Longitud |
| `radius_km` | float | No | Radio (default: 10) |
| `limit` | int | No | Límite (default: 5) |

**Respuesta:** Playas ordenadas por score (best first)

---

#### 2.3 Búsqueda inteligente

```
GET /beaches/search
```

**Query Parameters:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `name` | str | Nombre de playa a buscar |
| `lat` | float | Latitud para proximidad |
| `lon` | float | Longitud para proximidad |
| `radius_km` | float | Radio (default: 10) |
| `max_occupation` | int | Ocupación máxima deseada |
| `min_quality` | str | Calidad mínima (good/excellent) |
| `avoid_jellyfish` | bool | Evitar playas con medusas |

**Ejemplo:**

```bash
GET /beaches/search?name=Barceloneta&lat=41.38&lon=2.19&max_occupation=70
```

**Response:**

```json
{
  "requested_beach": {
    "id": "...",
    "name": "Platja de la Barceloneta",
    "current_occupation": 85,
    "flag_color": "yellow",
    ...
  },
  "recommendation": {
    "reason": "Ocupación alta (85%)",
    "alternatives": [
      {
        "beach": { ... },
        "distance_km": 2.3,
        "score": 92,
        "improvements": ["Ocupación menor", "Bandera verde"]
      },
      ...
    ]
  }
}
```

---

#### 2.4 Recomendaciones de seguridad

```
GET /beaches/{id}/recommendations
```

**Response:**

```json
{
  "beach_id": "550e8400-e29b-41d4-a716-446655440000",
  "beach_name": "Platja de la Barceloneta",
  "data_status": "live",
  "recommendations": [
    {
      "level": "safe",
      "message": "Condiciones óptimas para el baño",
      "details": [
        "✓ Bandera verde",
        "✓ Sin medusas",
        "✓ Calidad agua excelente",
        "✓ Socorrista presente"
      ]
    }
  ],
  "alerts": [],
  "last_updated": "2026-05-04T12:00:00Z"
}
```

---

### 3. DASHBOARDS

#### 3.1 Resumen global (KPIs)

```
GET /dashboard/summary
```

**Response:**

```json
{
  "total_beaches": 150,
  "avg_occupation": 58.3,
  "quality_distribution": {
    "excellent": 65,
    "good": 50,
    "sufficient": 25,
    "poor": 10
  },
  "flag_distribution": {
    "green": 100,
    "yellow": 35,
    "red": 5,
    "unknown": 10
  },
  "active_alerts": 3,
  "last_updated": "2026-05-04T12:00:00Z"
}
```

---

#### 3.2 Alertas activas

```
GET /dashboard/alerts
```

**Response:**

```json
{
  "alerts": [
    {
      "beach_id": "...",
      "beach_name": "Platja de la Poblenou",
      "alert_type": "danger",
      "message": "Bandera roja izgada",
      "timestamp": "2026-05-04T11:30:00Z"
    },
    ...
  ],
  "count": 3
}
```

---

#### 3.3 Analytics: Ocupación

```
GET /dashboard/analytics/occupation
```

**Parámetros:**
- `region`: Filtrar por región
- `days`: Días de histórico (default: 30)

---

#### 3.4 Analytics: Calidad agua

```
GET /dashboard/analytics/quality
```

---

### 4. SALUD

#### 4.1 Health check

```
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-05-04T12:00:00Z"
}
```

---

#### 4.2 Readiness probe

```
GET /health/ready
```

**Response:**

```json
{
  "ready": true,
  "database": "connected"
}
```

---

## 📊 Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Unprocessable Entity |
| 500 | Internal Server Error |

---

## 🔐 Enums

### flag_color
- `green` - Segura para bathe
- `yellow` - Precaución
- `red` - Prohibido baignarse
- `unknown` - Estado no disponible

### tide
- `alta`
- `baja`
- `media`

### water_quality
- `excellent`
- `good`
- `sufficient`
- `poor`
- `unknown`

### data_status
- `live` - Datos en tiempo real
- `estimated` - Datos estimados/calculados
- `unavailable` - Sin datos disponibles

---

## 📝 Notas

1. Todos los timestamps están en formato ISO 8601 (UTC)
2. Las coordenadas usan el sistema WGS84
3. Las distancias se calculan en kilómetros usando Haversine
4. El sistema de scoring devuelve valores 0-100 (mayor = mejor)