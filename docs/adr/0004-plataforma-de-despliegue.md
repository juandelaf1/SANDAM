# ADR 0004 — Plataforma de despliegue

- **Estado**: Propuesta (decisión pendiente)
- **Fecha**: 2026-10-19
- **Decisores**: propietario del producto

## Contexto

SANDAM ya tiene `Dockerfile` y `docker-compose.yml` (API + PostgreSQL) y CI. Para tener un MVP
"desplegado y verificable" hay que elegir plataforma. Se evalúan dos enfoques, sin preferencia por
moda.

## Alternativas

1. **Contenedor + PostgreSQL gestionado** (p. ej. Fly.io, Render, Railway) — compatible con el stack
   actual (FastAPI async + asyncpg), mínima fricción, sin reescritura.
2. **Cloudflare Workers (Python) + PostgreSQL** — menor latencia/edge, pero requiere verificar
   compatibilidad de dependencias (asyncpg, SQLAlchemy async, `requests`) y del modelo de ejecución;
   puede forzar reescritura o adaptadores.
3. **Servidor propio / VM** — control total, más coste operativo.

## Decisión (propuesta)

**No decidida.** Se recomienda evaluar primero la opción 1 (contenedor + PostgreSQL gestionado) por
compatibilidad directa con el stack, y validar técnicamente la opción 2 (Workers) **solo** si se
demuestra compatible con las dependencias reales y con un requisito medido que la justifique.

## Justificación

El Principio IX exige no introducir complejidad ni plataformas sin requisito documentado. La opción
1 no añade reescritura; la opción 2 debe demostrarse antes de adoptarse.

## Consecuencias

- Queda registrado como decisión pendiente en `docs/OPEN_QUESTIONS.md`.
- No se realiza migración de plataforma dentro del alcance de la spec 001.
- Cualquier decisión final se documentará actualizando este ADR (estado → Aceptada).
