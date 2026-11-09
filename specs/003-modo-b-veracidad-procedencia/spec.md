# Spec 003 — Modo B: veracidad, procedencia y límites de capacidad/aforo

- **Estado:** borrador (guardrails). Cambios funcionales/scoring/API incompatibles requieren plan/tasks y revisión (SDD, ver `AGENTS.md`).
- **Fecha:** 2026-11-09
- **Relacionados:** `docs/OPEN_QUESTIONS.md` (Q1/Q2/Q26/Q27/Q28), `docs/OPEN_QUESTIONS_PLAN.md`, `docs/CONTRACT_NOTES.md`, constitución/`AGENTS.md` (veracidad del dato), raíz `docs/PROVENANCE_CONVENTION.md`.

## Contexto
Mientras Q1 (metodología/capacidad) y Q2 (aforo/ocupación en tiempo real) no tengan fuente verificable, SANDAM **no** puede afirmar “aforo real”, “capacidad oficial” ni “tiempo real” verificado. El producto opera en **Modo B (honesto/interino)**: indicadores relativos/estimados claramente etiquetados, o claims desactivados.

## Requisitos (guardrails, Modo B)
1. **Sin `random` ni simulación como observación** en rutas que devuelvan dato real/operativo (ya exigido por `AGENTS.md`).
2. **Etiquetado de naturaleza/procedencia** en valores relevantes: `observation | estimation | prediction | expired | unknown` (y `observado|estimado|sintético` donde aplique contrato P1). Nunca presentar seed/valor por defecto no observado como condición favorable.
3. **Capacidad (`max_capacity` seed/orientativa):** no usar como umbral oficial en recomendación; no exponer como “capacidad verificada” sin `fuente+metodologia+fecha`.
4. **Ocupación/tiempo real:** no afirmar “tiempo real” ni ocupación observada sin fuente con latencia/confiabilidad conocida; usar presión relativa/estimada etiquetada o desactivar claim.
5. **Contratos:** respuestas públicas incluyen `contract_version` y metadatos de procedencia cuando corresponda; `/health` refleja capacidades honestas (ej. `capacity_verified:false`, `occupancy_realtime_verified:false`).
6. **Cambios de esquema/comportamiento:** migración Alembic + spec/plan/tasks; tests que impidan regresión de veracidad (no filtrar “capacidad real” sin fuente).

## Criterios de aceptación
- Ningún endpoint/UI soportado por el backend afirma capacidad/aforo real o tiempo real sin procedencia verificable.
- `pytest` y revisiones de contrato pasan con guardrails de etiquetado.
- Transición a **Modo A** solo tras cerrar Q1/Q2 con fuente verificable y registrar decisión (ADR/`DECISION_LOG` transversal).