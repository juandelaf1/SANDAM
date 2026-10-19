# ADR 0003 — Migraciones de esquema con Alembic

- **Estado**: Aceptada
- **Fecha**: 2026-10-19
- **Decisores**: propietario del producto

## Contexto

El proyecto usaba `create_all()` (en `src/database.py::init_db`, invocado desde el `lifespan` de
`src/main.py`) y no tenía migraciones, pese a que `alembic` figuraba en `requirements.txt`. La spec
001 necesita nuevos campos y entidades (trazabilidad, capacidad, observaciones, predicciones), lo
que implica cambios de esquema. Sin migraciones, los cambios no son reproducibles ni reversibles, y
`create_all()` no altera tablas existentes.

## Alternativas

1. **Alembic** (estándar para SQLAlchemy) — versionado, reproducible, reversible.
2. **`create_all()` + cambios manuales** — no reproducible; riesgo de divergencia entre entornos.
   Descartada (viola el Principio VII).
3. **Recrear la BD en cada despliegue** — inviable con datos reales.

## Decisión

Adoptar **Alembic** con una migración inicial que refleje el esquema actual, y migraciones
sucesivas para los cambios de la spec 001. `create_all()` deja de ser el mecanismo de evolución del
esquema.

## Justificación

La evolución del modelo debe ser auditable, reproducible y reversible (Principio VII). Alembic es
la herramienta estándar del stack y ya está declarada como dependencia.

## Consecuencias

- Se añade `alembic.ini` y `alembic/` (env + `versions/`).
- La migración inicial debe contrastarse con el esquema real antes de aplicarse.
- Cada migración incluye plan de reversión.
- `create_all()` deja de usarse en el arranque de la aplicación (solo los tests lo usan).
- El CI **debe** incorporar un test que aplique las migraciones sobre una base limpia (pendiente: T028).

## Estado de implementación

- **Implementado (2026-10-19, tarea T003)**: `alembic.ini`, `alembic/env.py` (asíncrono, URL desde
  `Settings`/`DATABASE_URL`, sin credenciales versionadas), `alembic/versions/0001_initial.py`
  (esquema actual de `beaches`), `alembic/script.py.mako` y `docs/MIGRATIONS.md`. Retirado
  `create_all()` del arranque de la aplicación.
- **Verificado sobre SQLite**: migración idéntica a los modelos (30 columnas, 5 índices),
  `alembic check` sin operaciones pendientes, `downgrade base` y `stamp head` correctos.
- **No verificado contra PostgreSQL real**: el daemon de Docker no estaba disponible en el entorno;
  sí se generó y revisó el SQL offline con dialecto PostgreSQL.

