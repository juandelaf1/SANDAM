# Phase 1 — Data Model: observaciones fiables y presión

**Feature**: 002-trusted-observations-and-occupancy
**Fecha**: 2026-10-20
**Estado**: diseño conceptual. **No implementado**; no hay migración en esta fase.

Este documento refina la entidad `Observation` ya esbozada en
`specs/001-sustainable-beach-recommendation/data-model.md` §2 y corrige sus ambigüedades:
allí `status` mezclaba naturaleza y disponibilidad, y no había validación ni resolución
espacial. Aquí se separan las dimensiones.

## 1. Principios del modelo

1. **Una observación es un hecho con contexto**, no un número suelto.
2. **Naturaleza ≠ validación ≠ vigencia.** Se modelan por separado.
3. **Lo desconocido no se almacena como valor.** Se almacena la ausencia de observación
   utilizable; la API lo expone como `unknown`.
4. **Nada se sobrescribe sin traza.** Las correcciones crean una observación nueva y marcan
   la anterior como `superseded` o `rejected`.
5. **Portabilidad.** Sin ENUM nativos ni JSONB (ADR 0005); tipos SQL estándar.
6. **Privacidad por diseño.** Solo agregados; sin identificadores personales.

## 2. Entidades

### 2.1 `data_sources` (catálogo)

| Campo | Tipo | Regla |
|---|---|---|
| `id` | UUID / slug | PK; identificador estable |
| `name` | VARCHAR(255) | NOT NULL |
| `kind` | VARCHAR(50) | `official`, `research`, `community`, `commercial`, `internal` |
| `uri` | TEXT | nullable; endpoint o página |
| `license` | VARCHAR(100) | nullable; `CC-BY`, `CMEMS`, `AEMET`, `unknown`… |
| `license_url` | TEXT | nullable |
| `terms_reviewed_at` | DATE | nullable; fecha de revisión legal |
| `terms_reviewed_by` | VARCHAR(100) | nullable |
| `priority` | INTEGER | orden de resolución de contradicciones |
| `status` | VARCHAR(20) | `active`, `paused`, `blocked`, `retired` |
| `contact` | VARCHAR(255) | nullable; responsable |
| `notes` | TEXT | nullable |

**Regla**: una fuente con `license = unknown` o `terms_reviewed_at = NULL` no puede estar
`active` para producción (FR-015).

### 2.2 `variables` (catálogo)

| Campo | Tipo | Regla |
|---|---|---|
| `code` | VARCHAR(50) | PK; p. ej. `occupation`, `water_quality`, `wave_height` |
| `unit` | VARCHAR(20) | unidad canónica; `%`, `count`, `m`, `s`, `°C`, `enum`, `bool` |
| `value_type` | VARCHAR(20) | `number`, `boolean`, `category`, `text` |
| `allowed_values` | TEXT | nullable; lista separada por comas para categorías |
| `default_validity_minutes` | INTEGER | nullable; regla por defecto |
| `is_pressure_indicator` | BOOLEAN | `occupation` = true |
| `description` | TEXT | — |

**Regla**: `default_validity_minutes` debe ser explícito; no hay una validez universal.

### 2.3 `observations`

| Campo | Tipo | Regla |
|---|---|---|
| `id` | UUID | PK |
| `beach_id` | UUID FK → `beaches.id` | NOT NULL, indexado |
| `variable_code` | VARCHAR(50) FK → `variables.code` | NOT NULL |
| `value_num` | FLOAT | nullable; si el tipo es numérico |
| `value_bool` | BOOLEAN | nullable; si el tipo es booleano |
| `value_text` | VARCHAR(255) | nullable; categorías/texto |
| `value_enum` | VARCHAR(50) | nullable; categorías controladas |
| `unit` | VARCHAR(20) | NOT NULL para numéricos; copia de la unidad canónica |
| `nature` | VARCHAR(20) | `observation`, `user_report`, `estimate`, `prediction`, `historical`, `synthetic`, `unknown` |
| `source_id` | UUID FK → `data_sources.id` | NOT NULL salvo `unknown`/`synthetic` interno |
| `method_id` | UUID FK → `methods.id` | NOT NULL salvo `unknown` |
| `observed_at` | DATETIME | nullable; obligatorio para `current` |
| `fetched_at` | DATETIME | NOT NULL |
| `valid_from` | DATETIME | nullable; por defecto `observed_at` |
| `valid_until` | DATETIME | nullable; si es NULL, se aplica la regla de la variable |
| `spatial_resolution_m` | FLOAT | nullable; 0 = puntual; >0 = agregado/modelo |
| `uncertainty` | FLOAT | nullable |
| `uncertainty_unit` | VARCHAR(20) | nullable |
| `validation_status` | VARCHAR(20) | `unvalidated`, `validated`, `rejected` |
| `validation_id` | UUID FK → `validation_records.id` | nullable |
| `transformation_id` | UUID FK → `transformations.id` | nullable |
| `privacy_level` | VARCHAR(20) | `aggregate`, `public`; nunca `individual` |
| `status` | VARCHAR(20) | `current`, `stale`, `superseded`, `invalid` |
| `created_at` | DATETIME | automático |

**Restricciones conceptuales**:

- Exactamente uno de `value_num`, `value_bool`, `value_text`, `value_enum` es no nulo
  (según `value_type`).
- `nature = observation` ⇒ `source_id` y `method_id` no nulos y `observed_at` no nulo.
- `nature = prediction` ⇒ `valid_until` no nulo y `method_id` no nulo.
- `validation_status = validated` ⇒ `validation_id` no nulo.
- `status = current` ⇒ `valid_until` nulo o futuro, y `observed_at` no futuro.
- `privacy_level = individual` prohibido.

### 2.4 `methods`

| Campo | Tipo | Regla |
|---|---|---|
| `id` | UUID | PK |
| `code` | VARCHAR(50) | único |
| `name` | VARCHAR(255) | — |
| `kind` | VARCHAR(20) | `measurement`, `estimate`, `prediction`, `rule`, `aggregation` |
| `version` | VARCHAR(20) | — |
| `description` | TEXT | — |
| `validated` | BOOLEAN | `false` por defecto |
| `validation_id` | UUID | nullable |

### 2.5 `validation_records`

| Campo | Tipo | Regla |
|---|---|---|
| `id` | UUID | PK |
| `method_id` | UUID | NOT NULL |
| `reference_source_id` | UUID | NOT NULL |
| `period_start`, `period_end` | DATE | NOT NULL |
| `sample_size` | INTEGER | NOT NULL |
| `coverage` | FLOAT | 0..1 |
| `metrics` | TEXT | JSON serializado como texto (portable); MAE/RMSE/bias o precision/recall/F1 |
| `baseline` | VARCHAR(255) | descripción de la línea base |
| `decision` | VARCHAR(20) | `accepted`, `rejected`, `inconclusive` |
| `decided_at` | DATETIME | — |
| `decided_by` | VARCHAR(100) | — |
| `notes` | TEXT | limitaciones y sesgos |

### 2.6 `transformations`

| Campo | Tipo | Regla |
|---|---|---|
| `id` | UUID | PK |
| `code` | VARCHAR(50) | p. ej. `aemet_station_to_beach`, `socib_grid_to_point` |
| `description` | TEXT | — |
| `version` | VARCHAR(20) | — |
| `input_units`, `output_units` | VARCHAR(20) | — |

### 2.7 `ingestion_runs`

| Campo | Tipo | Regla |
|---|---|---|
| `id` | UUID | PK |
| `source_id` | UUID | NOT NULL |
| `started_at`, `finished_at` | DATETIME | — |
| `status` | VARCHAR(20) | `success`, `partial`, `failed` |
| `rows_read`, `rows_written`, `rows_rejected` | INTEGER | — |
| `error` | TEXT | nullable |
| `idempotency_key` | VARCHAR(100) | único por fuente+ventana |

## 3. Estados y transiciones

### 3.1 Ciclo de vida de una observación

```text
                    ┌─────────────┐
  fuente ──────────▶│  unvalidated│
                    └──────┬──────┘
                           │ validación
              ┌────────────┴────────────┐
              ▼                         ▼
        ┌───────────┐             ┌───────────┐
        │ validated │             │ rejected  │
        └─────┬─────┘             └───────────┘
              │ corrección / nueva observación
              ▼
        ┌───────────┐
        │ superseded│
        └───────────┘

  valid_until < now()  ⇒  stale  (no se borra)
  dato incoherente      ⇒  invalid (con motivo)
```

- `stale` no es un valor; es un estado de vigencia.
- Una observación `stale` puede seguir mostrándose si se etiqueta, pero no cuenta para
  `coverage` ni para una decisión como dato actual.

### 3.2 Resolución de contradicciones

```text
para una (beach, variable, instante):
  1. descartar status ∈ {invalid, rejected}
  2. descartar nature = synthetic en producción
  3. ordenar por priority de source (mayor primero)
  4. a igual prioridad, observed_at más reciente
  5. si siguen empatadas y los valores difieren → marcar conflicto y no elegir
```

Nunca se promedian valores de fuentes distintas sin una transformación declarada.

## 4. Derivados: presión y calidad del dato

### 4.1 `PressureIndicator` (no persistido necesariamente)

| Campo | Tipo | Regla |
|---|---|---|
| `beach_id` | UUID | — |
| `occupancy_value` | FLOAT | nullable |
| `occupancy_unit` | VARCHAR(20) | `%` o `count` |
| `status` | VARCHAR(20) | `observed`, `estimated`, `stale`, `unknown`, `synthetic` |
| `relative_pressure` | FLOAT 0..1 | nullable; solo si hay valor y referencia |
| `reference` | VARCHAR(255) | nullable; capacidad o referencia usada |
| `reference_is_validated` | BOOLEAN | `false` por defecto |
| `inputs` | TEXT | IDs de observaciones usadas |
| `label` | VARCHAR(100) | “presión relativa”, nunca “capacidad oficial” |

**Regla**: si `status = unknown`, `relative_pressure` es `null`. No se emite `0.0`.

### 4.2 `DataQuality` (respuesta)

| Campo | Tipo | Regla |
|---|---|---|
| `variable` | VARCHAR(50) | — |
| `nature` | VARCHAR(20) | del vocabulario |
| `validation_status` | VARCHAR(20) | — |
| `status` | VARCHAR(20) | `current`, `stale`, `unknown`, `synthetic` |
| `source` | VARCHAR(255) | nullable |
| `observed_at` | DATETIME | nullable |
| `valid_until` | DATETIME | nullable |
| `spatial_resolution_m` | FLOAT | nullable |
| `observation_id` | UUID | nullable |

`coverage` se calcula como `variables_con_observación_válida / variables_requeridas`. Un
default no cuenta.

## 5. Compatibilidad con el modelo actual

| Campo actual | Destino | Compatibilidad |
|---|---|---|
| `current_occupation` | Se mantiene; se añade `occupancy_status` y `occupancy_observed_at` | Aditiva; cliente antiguo sigue leyendo el entero; cliente nuevo usa el estado |
| `jellyfish_present` | Se mantiene; se añade `jellyfish_status` (`present/absent/unknown`) | Aditiva |
| `sargasso_level` | Se mantiene; se añade `sargasso_status` | Aditiva |
| `posidonia_present` | Se mantiene; se añade `posidonia_status` | Aditiva |
| `has_*` | Se mantienen; se añade `services_status` (mapa servicio→estado) | Aditiva |
| `data_status` | Se mantiene; se añade `data_origin` (`seed/imported/observed/api`) y `synthetic` | Aditiva; el seed pasa a `synthetic` |
| `last_updated` | Se mantiene como metadato del registro | No confundir con `observed_at` |
| `flag_color`, `water_quality` | Se mantienen; se enlazan a observaciones | Aditiva |

**Fase de transición**: durante una versión, un valor desconocido puede seguir viajando como
`0`/`false` en el campo legado **solo si** el campo de estado dice `unknown`. La UI y la
documentación deben usar el estado, no el valor legado. La fase final propone `null` en el
campo legado; se decidirá con pruebas de contrato y clientes conocidos.

## 6. Migración (propuesta, no ejecutada)

### 6.1 Fases

1. **Auditoría de datos** (solo lectura):
   - contar filas por `data_status`, `data_origin` si existe, y valores iguales a defaults;
   - listar playas sin ninguna observación;
   - detectar filas con `capacity_reference` sin `capacity_method` (ya cubierto por ORM).
2. **Migración `0003`** (aditiva):
   - `data_sources`, `variables`, `methods`, `transformations`, `validation_records`,
     `ingestion_runs`, `observations`;
   - columnas de estado en `beaches` (`occupancy_status`, `jellyfish_status`,
     `sargasso_status`, `posidonia_status`, `data_origin`);
   - índices: `(beach_id, variable_code, observed_at)`, `(status, valid_until)`,
     `(source_id, fetched_at)`.
3. **Backfill conservador**:
   - seed → `data_origin = 'seed'`, `data_status = 'synthetic'`, estados `unknown` (o
     `synthetic` cuando el valor venga del seed);
   - filas sin origen demostrable → `data_origin = 'unknown'`, estados `unknown`;
   - no se crea ninguna observación “real” sin fuente.
4. **Adaptadores** (una fuente por vez):
   - AEMET (meteo), SOCIB/Copernicus (mar), calidad oficial (agua), CAIB (contexto);
   - cada uno con `data_source`, `method`, `validity`, `ingestion_run` e idempotencia.
5. **Consumidores**:
   - `data_quality` real; `coverage` real; `pressure_relative` solo si hay observación;
   - `/recommendations`, `/search`, `/external`, `/dashboard` dejan de premiar la ocupación.
6. **Relajación de defaults** (migración posterior, solo tras compatibilidad):
   - `NULL` permitido; defaults de Python retirados;
   - tests de contrato actualizados.

### 6.2 Reversión

- `alembic downgrade -1` elimina las tablas/columnas nuevas. Las tablas nuevas no contienen
  datos preexistentes; el `downgrade` no toca `beaches` salvo las columnas añadidas.
- El backfill de `data_status`/`data_origin` es reversible si se guarda el valor anterior en
  una tabla de auditoría o se documenta el valor por defecto. **No** se propone borrar datos.

## 7. Invariantes verificables

1. `observation.nature = observation` ⇒ `source_id`, `method_id`, `observed_at` no nulos.
2. `observation.status = current` ⇒ `valid_until` nulo o futuro.
3. `observation.value_*` exactamente uno no nulo.
4. `source.status = active` ⇒ `license != unknown` y `terms_reviewed_at` no nulo.
5. `pressure.relative_pressure != null` ⇒ `occupancy` con estado `observed` o `estimated`.
6. `data_quality.nature = observation` ⇒ `observation_id` no nulo y `source` no nulo.
7. `seed` ⇒ `data_origin = seed` y `data_status = synthetic`.
8. `migration` no crea observaciones sin fuente.

## 8. Ejemplos

### 8.1 Ocupación observada (Calvià, con convenio)

```json
{
  "beach_id": "…",
  "variable_code": "occupation",
  "value_num": 62,
  "unit": "%",
  "nature": "observation",
  "source_id": "calvia_aforo",
  "method_id": "camera_estimate_v1",
  "observed_at": "2026-08-10T11:15:00Z",
  "fetched_at": "2026-08-10T11:16:10Z",
  "valid_until": "2026-08-10T11:30:00Z",
  "spatial_resolution_m": 50,
  "validation_status": "unvalidated",
  "status": "current",
  "privacy_level": "aggregate"
}
```

### 8.2 Ocupación desconocida

No se crea una observación con `value_num = 0`. La respuesta declara:

```json
{
  "occupancy_status": "unknown",
  "pressure_relative": null,
  "data_quality": {
    "occupation": {
      "nature": "unknown",
      "status": "unknown",
      "source": null,
      "observation_id": null
    }
  }
}
```

### 8.3 Predicción no validada

```json
{
  "variable_code": "occupation",
  "value_num": 70,
  "unit": "%",
  "nature": "prediction",
  "source_id": "sandam_heuristic",
  "method_id": "occupation_rule_v1",
  "valid_until": "2026-08-10T14:00:00Z",
  "validation_status": "unvalidated",
  "status": "current"
}
```

La respuesta debe añadir `validated: false`, `confidence: null` y no usar la predicción como
factor de recomendación.

### 8.4 Seed

```json
{
  "data_origin": "seed",
  "data_status": "synthetic",
  "occupancy_status": "unknown",
  "jellyfish_status": "unknown",
  "services_status": {
    "lifeguard": "unknown",
    "parking": "unknown"
  }
}
```
