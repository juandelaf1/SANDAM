# 🏖️ SANDAM - Smart Beach Management API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

API REST asíncrona para gestión y monitorización en tiempo real del estado de las playas. Sistema de recomendaciones inteligentes que sugiere alternativas cuando una playa no cumple los criterios de seguridad o disponibilidad.

## 📋 Características

- ✅ CRUD completo de playas
- ✅ Búsqueda por proximidad geográfica (Haversine)
- ✅ Sistema de recomendaciones de seguridad
- ✅ Búsqueda inteligente con alternativas sugeridas
- ✅ Scoring automático de playas
- ✅ Endpoints especializados para dashboards
- ✅ Medidas de contención (fallback strategy)
- ✅ Trazabilidad completa del dato
- ✅ Preparado para integración con APIs externas (ACA, AEMET, NOAA)
- ✅ Docker-compose para desarrollo rápido

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Framework | FastAPI 0.115+ |
| ORM | SQLAlchemy 2.0 (async) |
| Driver DB | asyncpg |
| Validación | Pydantic 2.9 |
| Server | Uvicorn 0.30 |
| Base de datos | PostgreSQL 14+ |
| Testing | pytest |
| Dashboard | Streamlit |

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11+
- PostgreSQL 14+ (o Docker)

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/juandelaf1/SANDAM.git
cd SANDAM

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar con Docker
docker-compose up -d

# O ejecutar directamente
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Verificar instalación

```bash
# Health check
curl http://localhost:8000/health

# Documentación interactiva
# http://localhost:8000/docs
```

## 📁 Estructura del Proyecto

```
SANDAM/
├── src/
│   ├── main.py              # App FastAPI
│   ├── config.py            # Configuración
│   ├── database.py          # Conexión DB
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── crud.py              # Operaciones CRUD
│   ├── deps.py              # Dependencias
│   ├── utils/
│   │   ├── scoring.py       # Sistema de puntuación
│   │   ├── recommendations.py # Recomendaciones seguridad
│   │   ├── distance.py      # Algoritmo Haversine
│   │   └── fallback.py      # Medidas contención
│   └── api/
│       ├── beaches.py      # Endpoints beaches
│       ├── search.py        # Búsqueda inteligente
│       ├── recommendations.py # Recomendaciones
│       ├── analytics.py    # Analytics
│       └── dashboard.py    # KPIs
├── tests/
├── docs/
├── notebooks/dashboards/   # Streamlit apps
├── docker-compose.yml
└── requirements.txt
```

## 📊 Endpoints Principales

### Playas (CRUD)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/beaches/` | Crear playa |
| GET | `/api/v1/beaches/` | Listar todas |
| GET | `/api/v1/beaches/{id}` | Obtener una playa |
| PUT | `/api/v1/beaches/{id}` | Actualizar playa |
| DELETE | `/api/v1/beaches/{id}` | Eliminar playa |

### Búsqueda y Recomendaciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/beaches/nearby` | Playas cercanas |
| GET | `/api/v1/beaches/best-nearby` | Mejores cercanas |
| GET | `/api/v1/beaches/search` | Búsqueda inteligente |
| GET | `/api/v1/beaches/{id}/recommendations` | Recomendaciones seguridad |

### Dashboards

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/summary` | KPIs globales |
| GET | `/api/v1/dashboard/alerts` | Alertas activas |
| GET | `/api/v1/dashboard/analytics/occupation` | Serie ocupación |
| GET | `/api/v1/dashboard/analytics/quality` | Distribución calidad |

### Salud

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/health/ready` | Readiness probe |

## 🔍 Ejemplos de Uso

### Crear una playa

```bash
curl -X POST "http://localhost:8000/api/v1/beaches/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Platja de la Barceloneta",
    "region": "Cataluña",
    "latitude": 41.3803,
    "longitude": 2.1898,
    "max_capacity": 15000,
    "current_occupation": 45,
    "flag_color": "green",
    "water_quality": "excellent",
    "has_lifeguard": true,
    "has_shade": true,
    "has_showers": true
  }'
```

### Buscar playas cercanas

```bash
curl "http://localhost:8000/api/v1/beaches/nearby?lat=41.38&lon=2.19&radius_km=10"
```

### Búsqueda inteligente con alternativas

```bash
curl "http://localhost:8000/api/v1/beaches/search?name=Barceloneta&lat=41.38&lon=2.19"
```

### Obtener KPIs para dashboard

```bash
curl "http://localhost:8000/api/v1/dashboard/summary"
```

## 🐳 Docker

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down
```

Servicios disponibles:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

## 📦 Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Connection string PostgreSQL | postgresql+asyncpg://postgres:postgres@localhost:5432/sandam |
| `API_HOST` | Host de la API | 0.0.0.0 |
| `API_PORT` | Puerto de la API | 8000 |
| `LOG_LEVEL` | Nivel de logging | INFO |
| `CORS_ORIGINS` | Origins permitidos para CORS | * |

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=src --cov-report=html
```

## 📈 Roadmap

- [x] Fase 1: MVP Core (CRUD + Search + Recommendations)
- [ ] Fase 2: Integración API ACA (Cataluña)
- [ ] Fase 3: Dashboards Streamlit
- [ ] Fase 4: Autenticación + Webhooks
- [ ] Fase 5: Producto comercial

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE)

## 👤 Autor

- **Juan de lafuente** - [juandelaf1](https://github.com/juandelaf1)

---

🏖️ **SANDAM** - Tu guía inteligente de playas