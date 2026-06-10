<p align="center">
  <img src="docs/img/sandam_banner.png" alt="SANDAM Banner" width="800">
</p>

# SANDAM — Smart Beach Management API

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
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

**Hypothesis**: An async FastAPI backend with geospatial search (Haversine), automated safety scoring, and fallback strategies can provide real-time beach intelligence and smart alternative recommendations.

**Solution**: SANDAM — a complete async REST API with **CRUD operations**, **proximity search**, **smart safety recommendations**, **automatic beach scoring**, and **analytics endpoints** for dashboard integration.

---

## Problem

- No centralized beach condition monitoring
- Overcrowding without real-time alternatives
- Manual safety flag updates
- Lack of historical occupancy data

## Key Features

| Feature | Description |
|---------|------------|
| Full CRUD | Create, read, update, delete beaches |
| Proximity Search | Haversine-based nearby beach finder |
| Safety Scoring | Automatic beach safety assessment |
| Smart Recommendations | Alternative suggestions when conditions are poor |
| Analytics Endpoints | KPIs, alerts, occupancy series, quality distribution |
| Fallback Strategy | Graceful degradation on API failures |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/beaches/` | Create beach |
| GET | `/api/v1/beaches/` | List all beaches |
| GET | `/api/v1/beaches/{id}` | Get beach details |
| GET | `/api/v1/beaches/nearby` | Find nearby beaches |
| GET | `/api/v1/beaches/search` | Smart search with alternatives |
| GET | `/api/v1/beaches/{id}/recommendations` | Safety recommendations |
| GET | `/api/v1/dashboard/summary` | Global KPIs |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI 0.115+ (async) |
| ORM | SQLAlchemy 2.0 (async) |
| DB Driver | asyncpg |
| Validation | Pydantic 2.9 |
| Database | PostgreSQL 14+ |
| Geospatial | Haversine algorithm |
| Dashboard | Streamlit |
| Containers | Docker Compose |

## Quick Start

```bash
git clone https://github.com/juandelaf1/SANDAM.git
cd SANDAM
docker-compose up -d
# API: http://localhost:8000
# Swagger: http://localhost:8000/docs
```

---

## Author

**Juan de la Fuente** — [@juandelaf1](https://github.com/juandelaf1)

juandelafuentelarrocca@gmail.com
