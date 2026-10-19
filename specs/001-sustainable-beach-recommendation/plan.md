# Implementation Plan: Recomendación de playas consciente de la presión turística y la capacidad de acogida

**Branch**: `001-sustainable-beach-recommendation` | **Date**: 2026-10-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-sustainable-beach-recommendation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command; its definition describes the execution workflow.

## Summary

Sustituir el actual sistema de recomendación (tres implementaciones de scoring divergentes y una
sola suma ponderada) por un modelo en **dos etapas** — elegibilidad y comparación de alternativas
elegibles — con un **único scoring canónico**, etiquetado de datos (observación/estimación/
predicción/caducado/desconocido), explicaciones por playa, determinismo, y degradación explícita
ante fallos de fuentes. El enfoque técnico reutiliza la arquitectura existente (FastAPI +
SQLAlchemy async + PostgreSQL) y **no introduce** nuevas dependencias de infraestructura.

## Technical Context

**Language/Version**: Python 3.11+ (entorno verificado: Python 3.13.12)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, asyncpg, aiosqlite (tests),
httpx/requests, ruff, pytest

**Storage**: PostgreSQL 14+ en producción; SQLite en memoria (`sqlite+aiosqlite:///:memory:`) en tests

**Testing**: pytest (+ pytest-asyncio); los tests actuales no requieren PostgreSQL

**Target Platform**: servicio web (contenedor Linux vía `Dockerfile`/`docker-compose.yml`); desarrollo verificado en Windows PowerShell

**Project Type**: single project (web-service)

**Performance Goals**: la recomendación evalúa el conjunto completo de playas del ámbito (20 en el
seed actual). Objetivo: respuesta interactiva; sin requisitos de alta concurrencia para el MVP.

**Constraints**: sin nuevas dependencias de infraestructura (sin Redis, PostGIS, colas, edge);
compatibilidad del contrato actual de la API de recomendación; determinismo del ranking; sin
`random` en rutas que devuelvan datos que parezcan reales.

**Scale/Scope**: Mallorca; ~20 playas; 1 especificación funcional; sin multi-región.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cumplimiento del diseño |
|-----------|--------------------------|
| I. Prioridad ambiental y seguridad | Elegibilidad como etapa previa; las exclusiones no se pueden compensar |
| II. Veracidad y trazabilidad del dato | Etiquetado de datos + procedencia (fuente) en cada valor relevante |
| III. Modelo en dos etapas y transparencia | Diseño explícito en dos etapas con explicaciones |
| IV. Scoring canónico único | Un único módulo canónico; se eliminan/desactivan las variantes divergentes |
| V. SDD | Este plan deriva de la spec 001 y de la constitución |
| VI. Verificación/determinismo | Tareas de tests incluidas (dominio, contrato, datos ausentes, exclusiones, determinismo) |
| VII. Migraciones explícitas | **Nuevos campos de cuatro metadatos requieren migración Alembic** (ADR 0003) |
| VIII. Secretos/privacidad | No se introducen datos personales; no se tocan credenciales |
| IX. Simplicidad | Sin nuevas dependencias; reutiliza la arquitectura existente |

**Resultado**: PASA. La única dependencia estructural es la necesidad de Alembic para cambios de
esquema (principio VII), ya contemplada como tarea previa. No se requiere justificar violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/001-sustainable-beach-recommendation/
├── plan.md              # Este archivo (/speckit.plan)
├── research.md          # Fase 0: baseline as-is y decisiones (/speckit.plan)
├── data-model.md        # Fase 1: entidades y metadatos (/speckit.plan)
├── quickstart.md        # Fase 1: guía de validación (/speckit.plan)
├── contracts/           # Fase 1: contrato del endpoint de recomendación
│   └── donde-ir.openapi.yaml
├── checklists/
│   └── requirements.md
├── spec.md              # (/speckit.specify)
└── tasks.md             # Fase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── api/
│   ├── donde_ir.py          # Router de recomendación (endpoint principal)
│   ├── recommendations.py   # Router de recomendaciones por playa
│   ├── predictions.py       # Contiene calculate_ideal_score (variante a unificar/retirar)
│   └── search.py            # nearby / best-nearby / search
├── utils/
│   ├── scoring.py           # Scoring canónico (a unificar aquí)
│   ├── recommendations.py   # Mensajes de seguridad/alertas (reutilizable)
│   ├── recommendation_engine.py  # Motor "dónde ir" (a reescribir sobre scoring canónico)
│   ├── distance.py          # Haversine
│   └── predictions.py       # Predicciones con random (a retirar de rutas de dato real)
├── models.py                # Modelo Beach (+ metadatos de observación)
├── schemas.py               # Contratos Pydantic
├── crud.py                  # Acceso a datos
├── config.py / database.py / deps.py / main.py
└── integrations/            # Clientes de fuentes (AEMET, SOCIB, CAIB, ...)

tests/
├── conftest.py
├── test_scoring.py          # Reglas de dominio del scoring canónico
├── test_recommendation.py   # Elegibilidad, exclusiones, determinismo, degradación
└── test_api_*.py            # Contratos de la API

docs/
├── PRODUCT_VISION.md        # Fuente canónica de visión y alcance
├── adr/                     # Decisiones arquitectónicas
├── OPEN_QUESTIONS.md        # Decisiones pendientes
├── API_GUIDE.md             # Guía de uso (a alinear con el ámbito Mallorca)
├── FRONTEND_INTEGRATION.md
├── CONTEXTO_MAESTRO.md      # Histórico (obsoleto)
└── PROJECT_CONTEXT.md       # Histórico (obsoleto)
```

**Structure Decision**: se mantiene el proyecto único existente (`src/` + `tests/` + `docs/`), sin
reestructuración. La lógica de dominio se consolida en `src/utils/`; los routers de `src/api/`
solo transportan.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Sin violaciones. No se añade 4º proyecto, ni patrón Repository, ni infraestructura nueva.

Dos decisiones de diseño que se documentan como ADR (no son violaciones):

| Decisión | Por qué | Alternativa descartada |
|----------|---------|------------------------|
| Modelo en dos etapas | Impide que la comodidad compense una exclusión (Principio I/III) | Suma ponderada única (permite que la comodidad gane) |
| Indicadores de presión **relativa** etiquetados | No hay capacidades oficiales fiables (Restricción de producto) | Inventar umbrales de capacidad (prohibido) |
