# Tasks: Observaciones fiables, procedencia y presión turística

**Input**: Design documents from `/specs/002-trusted-observations-and-occupancy/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: incluidos. La constitución (Principio VI) y la spec exigen verificación
automatizada (SC-001…SC-009).

**Estado**: **ninguna tarea está implementada**. Todas las casillas están sin marcar a
propósito. Este documento es planificación; la implementación empieza con `/speckit.implement`
tras revisión.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: US1 (saber qué está observado), US2 (no premiar el vacío), US3 (procedencia),
  US4 (synthetic), US5 (validación de heurísticos)
- Rutas de archivo exactas en cada tarea.

## Path Conventions

Proyecto único: `src/`, `tests/`, `docs/`, `specs/`, `alembic/` en la raíz.

---

## Phase 1: Setup

**Purpose**: confirmar la línea base y cerrar la auditoría previa.

- [ ] T001 Verificar la línea base antes de tocar nada: `ruff check src tests seed_data.py` y `pytest` (debe estar en verde, 133 tests) y registrar el resultado.
- [ ] T002 [P] Escribir una consulta/informe de auditoría de solo lectura sobre `beaches` (filas por `data_status`, valores iguales a defaults, playas sin observación) en `docs/DATA_AUDIT_OCCUPANCY.md`. **No modifica datos.**
- [ ] T003 [P] Fijar el catálogo de variables con unidad, tipo y `default_validity_minutes` por variable en `specs/002-trusted-observations-and-occupancy/data-model.md` §2.2 (y volcarlo al catálogo cuando se implemente).
- [ ] T004 [P] Revisar y registrar licencia/permiso de cada fuente candidata (AEMET, SOCIB, Copernicus, calidad oficial, Calvià, Consell, Gemelo Digital) en `docs/OPEN_QUESTIONS.md`; marcar como `blocked` lo no verificado.

**Checkpoint**: línea base verde y fuentes clasificadas.

---

## Phase 2: Foundational (bloquea todas las historias)

**Purpose**: modelo, migración aditiva y dominio común.

- [ ] T005 Cerrar y validar el JSON Schema del contrato en `specs/002-trusted-observations-and-occupancy/contracts/observation.schema.json` (Draft 2020-12, `check_schema` + casos válidos/ inválidos).
- [ ] T006 [P] Añadir los modelos ORM `Observation`, `DataSource`, `Method`, `Variable`, `Transformation`, `ValidationRecord`, `IngestionRun` en `src/models.py` (tipos portables; sin ENUM nativo ni JSONB).
- [ ] T007 Crear la migración aditiva `alembic/versions/0003_observations.py` con las tablas de T006 y su `downgrade`.
- [ ] T008 Añadir a `beaches` las columnas de estado (`occupancy_status`, `jellyfish_status`, `sargasso_status`, `posidonia_status`) y `data_origin` en `src/models.py` + migración `0003`.
- [ ] T009 Añadir índices `(beach_id, variable_code, observed_at)`, `(status, valid_until)`, `(source_id, fetched_at)` en `src/models.py` + migración `0003`.
- [ ] T010 [P] Escribir `tests/test_migration_0003.py`: `upgrade head`/`downgrade 0002` en SQLite en memoria y verificación de columnas/índices.
- [ ] T011 Implementar el backfill conservador en `seed_data.py` (o script de migración): seed → `data_origin="seed"`, `data_status="synthetic"`; filas sin origen → `unknown`. **Sin crear observaciones sin fuente.**
- [ ] T012 [P] Implementar `src/utils/observations.py` (dominio puro, sin BD ni red): vigencia (`valid_until`), resolución de contradicciones por prioridad, `coverage` real y `unknown` explícito. Tests en `tests/test_observations_validity.py`.
- [ ] T013 Cargar el catálogo inicial de `data_sources` con `status` `active`/`blocked` según T004 (ninguna fuente no verificada puede quedar `active`).

**Checkpoint**: esquema y dominio listos; la API todavía no cambia.

---

## Phase 3: User Story 1 — Saber qué está observado (P1)

**Goal**: cada valor declara naturaleza y vigencia; el desconocido no es favorable.

**Independent Test**: playa solo con defaults → `unknown` en ocupación/medusas/servicios; con observación válida → fuente y hora.

### Tests

- [ ] T014 [P] [US1] `tests/test_unknown_not_favorable.py`: default de ocupación/medusas/servicios no produce `0`, `false`, “playa tranquila”, “sin medusas” ni “condiciones óptimas”.
- [ ] T015 [US1] `tests/test_data_quality_contract.py`: `data_quality` no etiqueta como `observation` un valor desconocido ni un default; `coverage` no cuenta defaults.

### Implementación

- [ ] T016 [US1] Ampliar `DataQuality`/`DataQualityEntry` en `src/schemas.py` (naturaleza, validación, vigencia, fuente, `observed_at`, `valid_until`, `observation_id`).
- [ ] T017 [US1] Reescribir el cálculo de `data_quality` en `src/utils/recommendation_engine.py` para leer observaciones reales (no `is not None`) y cubrir `flag_color`, medusas, sargazo y servicios.
- [ ] T018 [US1] Actualizar `src/api/donde_ir.py` para exponer `occupancy_status`, `pressure_relative` nullable y `data_quality` real, manteniendo los campos existentes.
- [ ] T019 [US1] Exponer el estado del dato en `src/api/beaches.py` y `src/api/recommendations.py` (campos aditivos) sin romper `response_model` existentes.
- [ ] T020 [US1] Corregir `src/utils/fallback.py`: `jellyfish_present=None` **no** se convierte en `False`; el estado queda `unknown`.
- [ ] T021 [US1] Documentar los estados y su semántica en `docs/API_GUIDE.md` (sección nueva), sin prometer tiempo real.

**Checkpoint**: US1 verificable de forma independiente.

---

## Phase 4: User Story 2 — No premiar el vacío (P1)

**Goal**: la ocupación no es mérito ni desempate; el desconocido no es “0 %”.

**Independent Test**: dos playas idénticas salvo ocupación (5 % vs 95 %) → mismo score y mismo orden; sin observación → `pressure_status = unknown`.

### Tests

- [ ] T022 [P] [US2] `tests/test_occupancy_not_merit.py`: la ocupación no altera `score` ni el orden; no aparecen “✓ Playa tranquila” ni “Ocupación menor”.
- [ ] T023 [P] [US2] `tests/test_pressure_unknown.py`: ocupación desconocida → `relative_pressure = null`, nunca `0.0`.

### Implementación

- [ ] T024 [US2] Reescribir `src/utils/recommendations.py`: eliminar “✓ Playa tranquila”, “✓ Sin medusas” y “Condiciones óptimas” cuando el estado sea desconocido; usar estados explícitos.
- [ ] T025 [US2] Corregir `src/crud.py::search_beach_with_alternatives`: “Ocupación menor” solo si **ambas** observaciones son válidas y vigentes; sin afirmación si es desconocida.
- [ ] T026 [US2] Corregir los filtros `occupation_min`/`occupation_max` en `src/crud.py` para no tratar `unknown` como `0`.
- [ ] T027 [US2] Actualizar `src/api/external_data.py` (`/compare`, `/sources`) para exponer estado de ocupación y fuentes reales.
- [ ] T028 [US2] Actualizar `src/api/dashboard.py`: media solo con observaciones válidas; declarar cobertura y excluir `synthetic`.
- [ ] T029 [US2] Ajustar `src/utils/recommendation_engine.py` para que `pressure_relative` y `flags.ocupacion` viajen con estado.

**Checkpoint**: US2 verificable; ninguna ruta premia el desconocido.

---

## Phase 5: User Story 3 — Trazar cada dato (P2)

**Goal**: registrar y consultar observaciones con fuente, método, tiempos y validación.

**Independent Test**: dos observaciones de la misma variable con fuentes distintas → traza de ambas, prioridad explícita, sin mezcla.

### Tests

- [ ] T030 [P] [US3] `tests/test_provenance_contract.py`: alta válida, alta sin `source`/`method`/`observed_at` rechazada o no utilizable; respuesta con `observation_id`.
- [ ] T031 [P] [US3] `tests/test_contradiction_resolution.py`: prioridad documentada, sin promedio silencioso, fuente descartada conservada.

### Implementación

- [ ] T032 [US3] Implementar el repositorio de observaciones en `src/crud.py` (crear, consultar vigentes, marcar `stale`/`superseded`).
- [ ] T033 [US3] Implementar la resolución de contradicciones y la traza en `src/utils/observations.py` (consumida por `crud`).
- [ ] T034 [US3] Exponer la procedencia por playa (consulta o endpoint aditivo) en `src/api/beaches.py`.
- [ ] T035 [US3] Añadir un comando/CLI de alta de observación para operadores (`scripts/` o comando documentado) con validación de contrato.
- [ ] T036 [US3] Conectar `/donde-ir` con la traza: cada valor usado referencia `observation_id` o declara `unknown`.

**Checkpoint**: trazabilidad de extremo a extremo.

---

## Phase 6: User Story 4 — No confundir demostración con realidad (P2)

**Goal**: el seed y los fixtures son `synthetic` y no se usan en producción.

**Independent Test**: ejecutar el seed y consultar → `synthetic`, no `live`.

### Tests

- [ ] T037 [P] [US4] `tests/test_synthetic_seed.py`: el seed no produce `data_status="live"`; en producción no se recomienda con él.
- [ ] T038 [P] [US4] `tests/test_sources_status.py`: `/external/sources` no declara `active` una fuente `blocked`/sin licencia.

### Implementación

- [ ] T039 [US4] Añadir `synthetic` a `DataStatus` (`src/models.py`), cambiar `seed_data.py:536` para marcar `synthetic`/`data_origin="seed"`, y `BeachCreate.data_status` (`src/schemas.py:44`) para no nacer como `live` sin observación; ajustar el mensaje/fixtures.
- [ ] T040 [US4] Añadir el bloqueo de `nature/synthetic` en producción en `src/utils/observations.py` y en la selección de `/donde-ir`.
- [ ] T041 [US4] Reescribir `src/api/external_data.py::get_data_sources` para leer del catálogo real (estado, licencia, última ingesta).

**Checkpoint**: US3 y US4 independientemente verificables.

---

## Phase 7: User Story 5 — Validar o retirar heurísticos (P3)

**Goal**: validar ocupación/medusas contra datos de referencia o retirarlos.

**Independent Test**: ejecutar el protocolo → métricas reproducibles con línea base y cobertura.

### Implementación

- [ ] T042 [P] [US5] Escribir el protocolo reproducible en `docs/HEURISTIC_VALIDATION.md` (datos, ventana, partición, métricas, umbral acordado antes de evaluar).
- [ ] T043 [US5] Implementar el cargador de datos de referencia en `scripts/validation/reference_data.py` (solo con permiso; sin datos en el repo si son sensibles).
- [ ] T044 [US5] Implementar la evaluación de ocupación (`scripts/validation/evaluate_occupation.py`): MAE, RMSE, sesgo, correlación, línea base de persistencia, cobertura.
- [ ] T045 [US5] Implementar la evaluación de medusas (`scripts/validation/evaluate_jellyfish.py`): precisión, recall, F1, prevalencia, matriz de confusión.
- [ ] T046 [US5] Registrar el resultado como `ValidationRecord` y aplicar la puerta: sin validación, `validated=false` y sin uso como factor (`src/utils/predictions.py`, `src/utils/recommendation_engine.py`).
- [ ] T047 [US5] Publicar el informe de validación con limitaciones y decisión (`docs/HEURISTIC_VALIDATION_REPORT.md`).

**Checkpoint**: heurísticos validados, ajustados o retirados con evidencia.

---

## Phase 8: Adaptadores de fuentes

**Purpose**: incorporar observaciones reales, una fuente por vez, sin activar lo no verificado.

- [ ] T048 [P] Adaptador AEMET en `src/integrations/aemet_observations.py` + tests con fixtures (estación→playa como transformación declarada).
- [ ] T049 [P] Adaptador SOCIB en `src/integrations/socib_observations.py` + tests (resolución de plataforma, no puntual).
- [ ] T050 [P] Adaptador Copernicus Marine en `src/integrations/copernicus_observations.py` + tests (contexto regional, atribución y DOI).
- [ ] T051 [P] Adaptador de calidad oficial del agua en `src/integrations/water_quality.py` + tests (validez estacional).
- [ ] T052 Implementar `IngestionRun` con idempotencia y dry-run en `src/integrations/` y un comando de ingesta.
- [ ] T053 Documentar límites, latencia y atribución de cada fuente en `docs/API_GUIDE.md` y `docs/DATA_SOURCES.md`.

**Checkpoint**: observaciones reales con procedencia para las variables cubiertas.

---

## Phase 9: Polish y cierre

- [ ] T054 Actualizar `docs/API_GUIDE.md`, `docs/MIGRATIONS.md` y `README.md` con el modelo de observaciones y la compatibilidad.
- [ ] T055 [P] Ampliar `.github/workflows/ci.yml` con `alembic upgrade head`, tests de contrato y validación del JSON Schema.
- [ ] T056 [P] Actualizar `docs/OPEN_QUESTIONS.md`: umbral de “tiempo real”, margen de validación y política de `null` en campos legados.
- [ ] T057 Escribir `tests/test_contract_compatibility.py` con las respuestas actuales y las aditivas.
- [ ] T058 Decidir y documentar la política de `null` vs `0` en campos legados; preparar la migración posterior de relajación de defaults.
- [ ] T059 Escribir un ADR en `docs/adr/` si el contrato cambia de forma incompatible (si no, documentar por qué no hace falta).
- [ ] T060 Ejecutar `quickstart.md` completo y actualizar `specs/002-.../tasks.md` con evidencia.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sin dependencias.
- **Foundational (Fase 2)**: depende de Setup — **bloquea** todas las historias.
- **US1/US2 (P1)**: dependen de Foundational; pueden ir en paralelo entre sí.
- **US3/US4 (P2)**: dependen de Foundational; US3 depende de parte de US1 (esquemas).
- **US5 (P3)**: requiere datos de referencia y permiso; puede quedar bloqueada sin bloquear a las demás.
- **Adaptadores (Fase 8)**: dependen de Foundational (T012/T013) y de la revisión de licencias (T004).
- **Polish (Fase 9)**: depende de las historias completadas.

### Parallel Opportunities

- T002, T003, T004 en paralelo.
- T006, T010, T012 en paralelo tras T005.
- T014/T015 y T016 en secuencia mínima.
- T022/T023 en paralelo.
- T030/T031 en paralelo.
- T037/T038 en paralelo.
- T048–T051 en paralelo (adaptadores distintos), tras T004 y T013.

## Implementation Strategy

### MVP (US1 + US2)

1. Setup + Foundational.
2. US1 (estados y `data_quality` real).
3. US2 (ocupación no es mérito).
4. **Parar y validar** con `quickstart.md` escenarios 1, 2, 3, 4, 5, 9.
5. Demostrar con datos sintéticos etiquetados.

### Entrega incremental

1. Foundational → esquema listo.
2. US1 → distinción observado/desconocido.
3. US2 → presión honesta.
4. US3 → trazabilidad.
5. US4 → seed sintético y fuentes reales.
6. Adaptadores → datos reales.
7. US5 → validación.
8. Polish → compatibilidad documentada.

## Notes

- [P] = archivos distintos, sin dependencias.
- Verificar que los tests fallan antes de implementar.
- Un commit local por tarea o grupo lógico; **sin push**.
- No cambiar los pesos del scoring ni introducir la ocupación en el score.
- Prohibido usar datos reales de fuentes sin licencia/permiso verificados.
- Prohibido `random` en rutas que devuelvan lo que parezca un dato real.
