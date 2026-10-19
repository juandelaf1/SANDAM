# ADR 0003 — Migraciones de esquema con Alembic

- **Estado**: Aceptada
- **Fecha**: 2026-10-19
- **Decisores**: propietario del producto

## Contexto

El proyecto usa `create_all()` (en `src/database.py::init_db`, invocado desde el `lifespan` de
`src/main.py`) y no tiene migraciones, pese a que `alembic` figura en `requirements.txt`. La spec
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
- Mientras Alembic no esté operativo, **no se introducen cambios de esquema**.
- El CI incorpora un test que aplica las migraciones sobre una base limpia.
