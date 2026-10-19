# Phase 1 — Data Model: Recomendación sostenible de playas

**Feature**: 001-sustainable-beach-recommendation
**Date**: 2026-10-19

Este documento describe las entidades del dominio, los campos necesarios y sus reglas de
validación. Distingue **existente** (ya en `src/models.py`) de **nuevo** (requiere migración
Alembic — ADR 0003). No se implementa en esta fase.

## 1. Playa (Beach) — datos relativamente estáticos

**Existente** (`src/models.py::Beach`):

| Campo | Tipo | Regla |
|-------|------|-------|
| `id` | UUID | PK |
| `name` | String(255) | NOT NULL, único, indexado |
| `region` | String(100) | NOT NULL (`"Mallorca"`) |
| `latitude` | Float | NOT NULL, -90..90 |
| `longitude` | Float | NOT NULL, -180..180 |
| `max_capacity` | Integer | nullable (ver regla de capacidad) |
| `has_kiosk` / `has_shade` / `has_showers` / `has_parking` / `has_accessibility` / `has_lifeguard` | Boolean | servicios disponibles |
| `created_at` / `last_updated` | DateTime | automáticos |

**Nuevo** (para elegibilidad y capacidad con fundamento):

| Campo | Tipo | Regla |
|-------|------|-------|
| `protection_status` | String | nullable; régimen de protección/sensibilidad documentado |
| `access_restrictions` | Text/JSON | nullable; restricciones de acceso/uso documentadas |
| `capacity_reference` | Integer | nullable; capacidad de referencia **solo si existe fuente** |
| `capacity_method` | String | nullable; metodología/fuente de `capacity_reference` |
| `vulnerability_level` | String/Enum | nullable; vulnerabilidad estimada documentada |

**Reglas**:

- `capacity_reference` MUST NOT rellenarse sin `capacity_method`. Si no hay fuente defendible, ambos
  quedan nulos y el sistema reconoce la incertidumbre (FR-014).
- `region` MUST ser `"Mallorca"` en el alcance actual (Principio de alcance).

## 2. Observación (Observation) — **nuevo**

Representa un valor de una fuente externa o medición legítima, con trazabilidad.

| Campo | Tipo | Regla |
|-------|------|-------|
| `id` | UUID | PK |
| `beach_id` | FK → Beach | NOT NULL, indexado |
| `variable` | String | NOT NULL (p. ej. `water_temp`, `flag_color`, `occupation`) |
| `value` | String/JSON | NOT NULL; valor serializado |
| `source` | String | NOT NULL; identificador de la fuente |
| `observed_at` | DateTime | nullable; cuándo ocurrió la observación |
| `fetched_at` | DateTime | NOT NULL; cuándo se obtuvo |
| `valid_until` | DateTime | nullable; fin de validez |
| `status` | Enum `DataStatus` | `live` / `estimated` / `unavailable` |

**Reglas**:

- Una observación sin `observed_at` no puede clasificarse como `live`.
- Si `valid_until < now()`, la observación se considera **caducada** (no actual).
- Ante datos contradictorios de dos fuentes, prevalece la de mayor prioridad documentada y se
  conserva `source` (FR-015).

## 3. Predicción (Prediction) — **nuevo (o envoltura)**

| Campo | Tipo | Regla |
|-------|------|-------|
| `id` | UUID | PK |
| `beach_id` | FK → Beach | NOT NULL |
| `variable` | String | NOT NULL |
| `value` | String/JSON | NOT NULL |
| `horizon` | String/Duration | NOT NULL (definido: p. ej. "+3h", "+1d") |
| `method` | String | NOT NULL; método identificable |
| `inputs` | JSON | entradas relevantes |
| `created_at` | DateTime | automático |

**Reglas**:

- Toda predicción MUST declarar `horizon` y `method` (FR-004, FR-005).
- Prohibido generar predicciones con `random`.

## 4. Indicador de presión relativa (PressureIndicator) — **derivado, no persistido necesariamente**

| Campo | Tipo | Regla |
|-------|------|-------|
| `beach_id` | — | referencia |
| `pressure_relative` | Float 0..1 | métrica derivada |
| `label` | String | MUST indicar que es **relativa**, no un límite ecológico oficial |
| `inputs` | JSON | de qué se derivó (observaciones usadas) |

**Reglas**: nunca presentar `pressure_relative` como capacidad oficial (FR-014).

## 5. Restricción / condición de exclusión (EligibilityCondition) — **nuevo o derivado**

| Campo | Tipo | Regla |
|-------|------|-------|
| `beach_id` | — | referencia |
| `type` | Enum | `official_closure` / `official_restriction` / `safety_risk` / `environmental_incompatibility` / `insufficient_data` |
| `reason` | String | texto legible |
| `source` | String | procedencia de la restricción |

**Reglas**: presencia de cualquier condición (salvo `insufficient_data`, que limita en lugar de
excluir) → la playa no es elegible (FR-001).

## 6. Recomendación (resultado, no persistido) — contrato en `contracts/`

Entidad de salida: playas elegibles ordenadas + explicación + estado del dato. Ver
`contracts/donde-ir.openapi.yaml`.

## Transiciones de estado del dato

```text
desconocido ──(llega observación)──▶ observación(live)
observación(live) ──(pasa valid_until | nueva observación)──▶ caducado
observación/estimación ──(método con horizonte)──▶ predicción
predicción ──(pasa horizonte)──▶ caducado/desconocido
```

- Una playa pasa de **elegible** a **no elegible** cuando aparece una condición de exclusión, y
  viceversa cuando la condición deja de estar vigente.
