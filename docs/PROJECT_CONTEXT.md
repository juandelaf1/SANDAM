# 🏖️ SANDAM - Project Context

## 📋 Resumen del Proyecto

**Nombre:** SANDAM
**Tipo:** API REST asíncrona para gestión y monitorización de playas en tiempo real
**Stack:** FastAPI + PostgreSQL + SQLAlchemy 2.0 + asyncpg
**Región inicial:** Cataluña (España)
**MVP:** CRUD completo + búsqueda inteligente + recomendaciones + dashboards

---

## 🎯 Propósito del Proyecto

- **Bootcamp:** Entrega académica con requisitos técnicos estrictos
- **Portfolio profesional:** Demostrar habilidades de Backend + Data Engineering
- **Producto escalable:** Base para solución comercial (B2B + B2C)

---

## 📜 Reglas de Desarrollo

### 1. Modularidad Estricta
El código debe dividirse en archivos con responsabilidad única:
- `main.py` - App FastAPI y definición de endpoints
- `database.py` - Configuración de conexión async a PostgreSQL
- `models.py` - Modelos SQLAlchemy (estructura de tablas)
- `schemas.py` - Schemas Pydantic (validación de datos API)
- `crud.py` - Operaciones de base de datos (lógica CRUD)
- `config.py` - Settings y configuración
- `deps.py` - Dependencias (get_db, auth, etc.)

### 2. Validación Pydantic
- Tipos de datos estrictos para garantizar calidad del dato
- Rangos validados: temperature (-10 a 50°C), UV (0-11), occupation (0-100%)
- Enums para flag_color, tide, water_quality, data_status
- Booleanos para presencia de medusas, posidonia, servicios

### 3. Asincronía Completa
- Todas las operaciones de BD con async/await
- Driver asyncpg para PostgreSQL
- SQLAlchemy con AsyncSession
- No usar código síncrono en rutas async

### 4. Trazabilidad del Dato
- Timestamps automáticos: `created_at`, `last_updated`
- Campo `data_status` para indicar origen (live/estimated/unavailable)
- Preparado para auditoría y análisis histórico

---

## 🗂️ Modelo de Datos: Beach

| Campo | Tipo | Restricciones | Propósito |
|-------|------|---------------|-----------|
| `id` | UUID | PK, auto | Identificador único |
| `name` | String | NOT NULL, max 255 | Nombre de la playa |
| `region` | String | NOT NULL | Cataluña/Valencia/Andalucía |
| `latitude` | Float | -90 a 90 | Latitud geográfica |
| `longitude` | Float | -180 a 180 | Longitud geográfica |
| `max_capacity` | Integer | > 0 | Capacidad máxima |
| `current_occupation` | Integer | 0-100% | Nivel de ocupación |
| `water_temp` | Float | nullable | Temperatura agua (°C) |
| `air_temp` | Float | nullable | Temperatura aire (°C) |
| `uv_index` | Integer | 0-11 | Índice UV (OMM) |
| `wind_speed` | Float | nullable | Velocidad viento (km/h) |
| `wave_height` | Float | nullable | Altura oleaje (m) |
| `tide` | Enum | alta/baja/media | Estado marea |
| `flag_color` | Enum | green/yellow/red/unknown | Bandera oficial |
| `jellyfish_present` | Boolean | default False | Presencia medusas |
| `jellyfish_species` | String | nullable | Especie detectada |
| `sargasso_level` | Integer | 0-3 | Nivel sargazo |
| `posidonia_present` | Boolean | default False | Presencia posidonia |
| `water_quality` | Enum | excellent/good/sufficient/poor/unknown | Calidad agua |
| `e_coli_count` | Integer | nullable | Conteo E. coli |
| `enterococci_count` | Integer | nullable | Conteo enterococos |
| `has_kiosk` | Boolean | default False | Quiosco disponible |
| `has_shade` | Boolean | default False | Zonas de sombra |
| `has_showers` | Boolean | default False | Duchas disponibles |
| `has_parking` | Boolean | default False | Parking disponible |
| `has_accessibility` | Boolean | default False | Accesibilidad |
| `has_lifeguard` | Boolean | default False | Socorrista presente |
| `data_status` | Enum | live/estimated/unavailable | Estado datos |
| `last_updated` | DateTime | auto | Última actualización |
| `created_at` | DateTime | auto | Fecha creación |

---

## 🔄 Medidas de Contención (Fallback Strategy)

Cuando no hay acceso a APIs externas o sensores:

| Campo | Fallback | Acción Automática |
|-------|----------|-------------------|
| `water_temp` | null | data_status = "unavailable" |
| `flag_color` | "unknown" | Mostrar warning en UI |
| `water_quality` | "unknown" | Recomendar "Consultar fuentes oficiales" |
| `jellyfish_present` | null | Asumir false + disclaimer |
| `uv_index` | null | Recomendación: "Usar protección solar" |

---

## 🎯 Sistema de Recomendaciones

Genera recomendaciones automáticas basadas en condiciones:

| Condición | Nivel | Recomendación |
|-----------|-------|---------------|
| `flag_color == red` | danger | "No bañarse. Banderas rojas" |
| `flag_color == yellow` | caution | "Baño con precaución" |
| `jellyfish_present == true` | warning | "Medusas detectadas" |
| `uv_index >= 8` | warning | "UV muy alto. SPF 50+" |
| `wave_height > 2m` | warning | "Oleaje peligroso" |
| `water_quality == poor` | danger | "Calidad agua mala" |
| `occupation >= 90%` | caution | "Playa muy concurrida" |

---

## 📊 Sistema de Scoring

Calcula scores para排序 de alternativas:

| Factor | Peso |
|--------|------|
| `flag_color` | 30% |
| `occupation` | 25% |
| `water_quality` | 20% |
| `jellyfish_present` | 15% |
| `uv_index` | 5% |
| `wave_height` | 5% |

---

## 🌍 GDPR y Sensibilidad

- **Sin perfiles de usuario en MVP**: GDPR no aplica
- **Geolocalización**: Coordenadas son datos públicos de playa
- **Datos biológicos**: E. coli y enterococos son parámetros ambientales
- **Para V2**: Si se añaden usuarios con geolocalización, revisar consentimiento

---

## 🔧 Stack Técnico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Framework | FastAPI | 0.115+ |
| ORM | SQLAlchemy | 2.0+ |
| Driver DB | asyncpg | 0.30+ |
| Validación | Pydantic | 2.9+ |
| Server | Uvicorn | 0.30+ |
| Base de datos | PostgreSQL | 14+ |
| Testing | pytest | 8+ |
| Dashboard | Streamlit | 1.40+ |
| Docker | Docker + Compose | latest |

---

## 📁 Estructura del Proyecto

```
SANDAM/
├── docs/
│   ├── PROJECT_CONTEXT.md    ← Este archivo
│   ├── README.md
│   ├── API_GUIDE.md
│   └── FRONTEND_INTEGRATION.md
├── src/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── deps.py
│   ├── utils/
│   │   ├── scoring.py
│   │   ├── recommendations.py
│   │   ├── distance.py
│   │   └── fallback.py
│   └── api/
│       ├── beaches.py
│       ├── search.py
│       ├── recommendations.py
│       ├── analytics.py
│       └── dashboard.py
├── tests/
├── notebooks/dashboards/
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

---

## 🚀 Roadmap de Desarrollo

| Fase | Alcance |
|------|---------|
| **Fase 1** | MVP Core: CRUD + Search + Nearby + Recommendations |
| **Fase 2** | Integración API ACA (datos reales Cataluña) |
| **Fase 3** | Dashboards Streamlit con KPIs |
| **Fase 4** | Escalado: más regiones + Auth + Webhooks |
| **Fase 5** | Producto comercial con pricing |

---

## 📝 Notas para el Desarrollador

1. **No generar URLs** - Usar solo las proporcionadas por el usuario
2. **Código limpio** - Sin comentarios innecesarios
3. **Seguridad** - No exponer secretos en logs
4. **Tests** - Verificar funcionalidad después de implementar
5. **Documentar** - Mantener README y API_GUIDE actualizados