# SANDAM — Smart Beach Management API

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![Pydantic](https://img.shields.io/badge/Pydantic-2.9-CC0000?logo=pydantic)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **Real-time beach monitoring and smart recommendation API. Async FastAPI + PostgreSQL + geospatial scoring.**

---

## Elevator Pitch

**Problem**: Beachgoers and local authorities lack a centralized system to check real-time beach conditions — occupancy, water quality, safety flags, and nearby alternatives. Municipalities struggle to manage overcrowding and safety alerts efficiently.

**Solution**: SANDAM — an async REST API with **CRUD operations**, **proximity search**, **smart safety recommendations**, **beach scoring**, **predictions**, external data integrations (AEMET, SOCIB) and **analytics endpoints** for dashboards.

---

## Key Features

| Feature | Description |
|---------|-------------|
| Full CRUD | Create, read, update, delete beaches |
| Proximity Search | Haversine-based nearby beach finder |
| Safety Scoring | Automatic beach safety assessment |
| Smart Recommendations | Alternative suggestions when conditions are poor |
| "Dónde ir ahora" | GPS + travel time + remaining sunlight algorithm |
| Predictions | Occupation, jellyfish risk, shade and forecast |
| External Data | AEMET weather stations, SOCIB oceanography |
| Analytics Endpoints | KPIs, alerts, occupancy and quality distribution |
| Fallback Strategy | Graceful degradation when the DB or APIs are unavailable |

---

## Quick Start

### Option A — Docker (API + PostgreSQL)

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec api python seed_data.py   # carga 20 playas de Mallorca
# API:      http://localhost:8000
# Swagger:  http://localhost:8000/docs
```

### Option B — Local

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (source .venv/bin/activate en Linux/macOS)
pip install -r requirements.txt

cp .env.example .env              # ajusta DATABASE_URL
# Arranca PostgreSQL (docker compose up -d postgres) y carga datos:
python seed_data.py

uvicorn src.main:app --reload     # http://localhost:8000
```

La API arranca en **modo degradado** si la base de datos no responde: `/health` sigue en 200 y `/health/ready` indica el estado real de la conexión.

---

## Tests

```bash
pytest            # requieren SQLite (aiosqlite), no necesitan PostgreSQL
ruff check src tests seed_data.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/beaches/` | Create beach |
| GET | `/api/v1/beaches/` | List beaches (filters + pagination) |
| GET | `/api/v1/beaches/{id}` | Get beach details |
| PUT | `/api/v1/beaches/{id}` | Update beach |
| DELETE | `/api/v1/beaches/{id}` | Delete beach |
| GET | `/api/v1/beaches/nearby` | Find nearby beaches |
| GET | `/api/v1/beaches/best-nearby` | Best nearby beaches by score |
| GET | `/api/v1/beaches/search` | Smart search with alternatives |
| GET | `/api/v1/beaches/{id}/recommendations` | Safety recommendations |
| GET | `/api/v1/dashboard/summary` | Global KPIs |
| GET | `/api/v1/dashboard/alerts` | Active alerts |
| GET | `/api/v1/dashboard/analytics/occupation` | Average occupation by region |
| GET | `/api/v1/dashboard/analytics/quality` | Water quality distribution |
| GET | `/api/v1/dashboard/analytics/safety` | Flag distribution |
| GET | `/api/v1/donde-ir/ahora` | "Dónde ir ahora" (needs `lat` & `lon`) |
| GET | `/api/v1/donde-ir/sol-restante` | Remaining sunlight |
| GET | `/api/v1/donde-ir/evaluar-playa/{name}` | Evaluate a specific beach |
| GET | `/api/v1/donde-ir/prediccion-medusas` | Jellyfish risk rules |
| GET | `/api/v1/predictions/occupation/{name}` | Occupation prediction |
| GET | `/api/v1/predictions/jellyfish/{name}` | Jellyfish risk |
| GET | `/api/v1/predictions/shade/{name}` | Shade availability |
| GET | `/api/v1/predictions/forecast/{name}` | Multi-day forecast |
| GET | `/api/v1/predictions/ideal-score/{name}` | "Playa ideal" score |
| GET | `/api/v1/weather/beach/{id}` | Weather for a beach (AEMET) |
| GET | `/api/v1/weather/nearby` | Weather by coordinates |
| GET | `/api/v1/weather/stations` | AEMET stations |
| GET | `/api/v1/external/sources` | Available data sources |
| GET | `/api/v1/external/comprehensive/{id}` | Aggregated data for a beach |
| GET | `/api/v1/external/compare/{id}` | Compare with nearby beaches |
| GET | `/api/v1/scraper/actualizar` | Refresh data from scrapers |

> Nota: los endpoints de `scraper` y las predicciones de `forecast`/`shade` usan fuentes heurísticas/aleatorias; revisa la fase de datos reales antes de usarlos en producción.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async) |
| DB Driver | asyncpg / aiosqlite |
| Validation | Pydantic v2 |
| Database | PostgreSQL 14+ |
| Geospatial | Haversine algorithm |
| Dashboard | Streamlit / Dash |
| Containers | Docker + Compose |

---

## Project Layout

```
src/
├── api/              # routers (beaches, search, dashboard, predictions, ...)
├── integrations/     # AEMET, SOCIB, scrapers
├── utils/            # scoring, distance, recommendations, predictions
├── config.py         # settings (pydantic-settings)
├── database.py       # async engine + session
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas
├── crud.py           # database operations
└── main.py           # FastAPI app
tests/                # pytest suite (SQLite, no DB required)
docs/                 # project context and guides
```

---

## Author

**Juan de la Fuente** — [@juandelaf1](https://github.com/juandelaf1)

juandelafuentelarrocca@gmail.com
