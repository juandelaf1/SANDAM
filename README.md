# 🏖️ SANDAM - Smart Beach Management API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

API REST asíncrona para gestión y monitorización en tiempo real del estado de las playas de Mallorca (Illes Balears). Sistema de recomendaciones inteligentes que sugiere alternativas cuando una playa no cumple los criterios de seguridad o disponibilidad.

## 📋 Características

- ✅ CRUD completo de playas
- ✅ Búsqueda por proximidad geográfica (Haversine)
- ✅ Sistema de recomendaciones de seguridad
- ✅ Búsqueda inteligente con alternativas sugeridas
- ✅ Scoring automático de playas
- ✅ Endpoints especializados para dashboards
- ✅ Medidas de contención (fallback strategy)
- ✅ Trazabilidad completa del dato

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Framework | FastAPI 0.115+ |
| ORM | SQLAlchemy 2.0 (async) |
| Driver DB | asyncpg |
| Validación | Pydantic 2.9 |
| Server | Uvicorn 0.30 |
| Base de datos | PostgreSQL 16 |
| Testing | pytest |
| Dashboard | Streamlit |

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11+
- PostgreSQL 16+ (ya instalado en el sistema)

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/juandelaf1/SANDAM.git
cd SANDAM

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configurar Base de Datos

1. Abrir **pgAdmin** (ya instalado en el sistema)
2. Crear una nueva base de datos llamada `sandam`
3. Configurar la contraseña del usuario `postgres` (si no la tienes, dejar la que está en .env)

### Ejecutar la API

```bash
# Iniciar el servidor
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Verificar Instalación

```bash
# Health check
curl http://localhost:8000/health

# Documentación interactiva (Swagger UI)
# http://localhost:8000/docs
```

### (Opcional) Cargar Datos de Ejemplo

```bash
python seed_data.py
```

Esto cargará 20 playas de Mallorca con datos de ejemplo.

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
├── .env
├── .gitignore
├── requirements.txt
├── seed_data.py
└── README.md
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

### Salud

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/health/ready` | Readiness probe |

## 🔍 Ejemplos de Uso

### Listar todas las playas

```bash
curl http://localhost:8000/api/v1/beaches/
```

### Buscar playas cercanas

```bash
curl "http://localhost:8000/api/v1/beaches/nearby?lat=39.52&lon=2.55&radius_km=10"
```

### Obtener recomendaciones de una playa

```bash
curl http://localhost:8000/api/v1/beaches/{id}/recommendations
```

### Obtener KPIs del dashboard

```bash
curl http://localhost:8000/api/v1/dashboard/summary
```

## 🎯 Datos de Ejemplo

El proyecto incluye 20 playas de Mallorca con nombres reales:

1. Platja de Palma
2. Cala Major
3. Portals Nous
4. Palmanova
5. Magaluf
6. Santa Ponça
7. Peguera
8. Cala Fornells
9. Camp de Mar
10. Port d'Andratx
11. Cala conills
12. Cala Rajada
13. Cala Mesquida
14. Cala Agulla
15. Platja de Muro
16. Can Picafort
17. Cala San Vicente
18. Port de Pollença
19. Cala Millor
20. Cala Bona

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=src --cov-report=html
```

## 📝 Notas para Desarrollo

- La base de datos usa PostgreSQL local (no Docker)
- Los datos de ejemplo son simulados pero con nombres de playas reales de Mallorca
- El sistema de recomendaciones sugere alternativas cuando una playa está llena o tiene problemas de seguridad

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE)

## 👤 Autor

- **Juan de la Fuente Larrocca** - [juandelaf1](https://github.com/juandelaf1)

---

🏖️ **SANDAM** - Tu guía inteligente de playas de Mallorca