# Tasks: Recomendación de playas consciente de la presión turística y la capacidad de acogida

**Input**: Design documents from `/specs/001-sustainable-beach-recommendation/`

**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Incluidos — la constitución (Principio VI) y los criterios de aceptación exigen
verificación automatizada (SC-001..SC-007).

**Organization**: Tareas agrupadas por historia de usuario para permitir implementación y prueba
independientes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: US1, US2, US3
- Todas las tareas incluyen rutas de archivo exactas.

## Path Conventions

- Proyecto único: `src/`, `tests/`, `docs/`, `specs/` en la raíz del repositorio.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirmar la línea base y unificar la documentación autoritativa.

- [x] T001 Verificar y registrar la línea base real: ejecutar `pytest` y `ruff check src tests seed_data.py` y anotar resultados (sin cambios de código).
  - _Completada en la adopción SDD: `ruff` OK; 32 tests OK (2026-10-19)._
- [x] T002 [P] Unificar la fuente de verdad documental: crear `docs/PRODUCT_VISION.md` y añadir banner de "histórico/obsoleto" a `docs/CONTEXTO_MAESTRO.md` y `docs/PROJECT_CONTEXT.md`; alinear ámbito a Mallorca en `docs/API_GUIDE.md`.
  - _Completada en la adopción SDD (commit `docs(spec-001)`)._

**Checkpoint**: línea base conocida y documentación alineada.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura y consolidación que MUST estar lista antes de cualquier historia.

**⚠️ CRITICAL**: ninguna historia puede empezar hasta terminar esta fase.

- [x] T003 Introducir Alembic y una migración inicial segura del esquema actual: `alembic.ini`, `alembic/env.py`, `alembic/versions/0001_initial.py` (ver `docs/adr/0003-migraciones-alembic.md`).
  - **Definición de terminado (T003)**: `alembic upgrade head` crea el esquema en una BD nueva; el
    esquema coincide con `src/models.py` (`alembic check` sin operaciones pendientes); `alembic
    downgrade base` revierte el esquema; `create_all()` retirado del arranque (solo lo usan los
    tests); documentado el alta de BD nueva y la adopción de BD existente (`docs/MIGRATIONS.md`);
    lint y tests en verde.
  - **Evidencia (2026-10-19)**: migración aplicada en SQLite idéntica a los modelos (30 columnas,
    5 índices); `alembic check` → "No new upgrade operations detected"; `downgrade base` OK;
    `stamp head` + `upgrade` no-op OK; SQL offline PostgreSQL válido; `ruff` OK; 32 tests OK.
  - **Evidencia PostgreSQL (2026-10-19)**: contra PostgreSQL 16.13 real, en base dedicada y
    desechable (`sandam_t003_test`): `upgrade head` → `0001 (head)`; tipos nativos correctos
    (`uuid`, `varchar`, `double precision`, `boolean`, `timestamp without time zone`); 30 columnas,
    PK `beaches_pkey`, índice único `ix_beaches_name` y 4 índices; `alembic check` sin operaciones
    pendientes; `downgrade base` + re-`upgrade` OK; adopción (`stamp head` + `upgrade` no-op) OK;
    FastAPI `/health/ready` → `ready: true` y consulta ORM OK.
  - **Definición de terminado**: **satisfecha**, incluida la confirmación en PostgreSQL real.
    Límite restante: automatizar la comprobación en CI (tarea **T028**).
- [x] T004 [P] Añadir campos de trazabilidad/capacidad a `src/models.py` (`protection_status`, `access_restrictions`, `capacity_reference`, `capacity_method`, `vulnerability_level`) y su migración `alembic/versions/0002_metadata_fields.py`. Regla: `capacity_reference` sin `capacity_method` es inválido.
  - **Definición de terminado (T004)**: los cinco campos existen en `src/models.py`; la migración
    `0002` (dependiente de `0001`) los añade sin reconstruir `beaches` ni perder filas; son
    anulables y sin defaults (`NULL` = desconocido); la regla `capacity_reference ⇒ capacity_method`
    se aplica y está probada; el contrato de la API no cambia; `alembic check` sin operaciones
    pendientes; lint y tests en verde.
  - **Evidencia (2026-10-19)**: `0002` aplicada en PostgreSQL 16.13 real (base dedicada y desechable
    `sandam_t004_test`): `0001 → 0002`, 35 columnas, 5 nuevas anulables con tipos nativos
    (`character varying`/`text`) y sin defaults; fila previa a T004 conservada con metadatos `NULL`
    (no inventados); actualización posterior con valores explícitos OK; `downgrade -1` elimina solo
    las 5 columnas conservando la fila, y el `upgrade head` posterior la restaura; `alembic check`
    sin operaciones pendientes; FastAPI arranca sin alterar el esquema y consulta la base; la regla
    del modelo rechaza `capacity_reference` sin `capacity_method` en PostgreSQL
    (`CapacityProvenanceError`).
  - **Evidencia en CI (SQLite)**: 9 tests nuevos (`tests/test_beach_metadata.py`,
    `tests/test_migrations.py`) → 41 tests OK; `ruff` OK.
  - **Decisión de diseño**: ADR 0005 (tipos portables, `NULL` = desconocido, `capacity_reference`
    como identificador textual de procedencia, regla como invariante del ORM en lugar de `CHECK` de
    BD). Limitación asumida: la regla no se garantiza para escrituras por SQL crudo.
- [x] T005 [P] Definir esquemas aditivos de respuesta en `src/schemas.py` (`DataQuality`, `Explanation`, `Recommendation`, `DondeIrResponse`) según `specs/001-sustainable-beach-recommendation/contracts/donde-ir.openapi.yaml`.
  - **Definición de terminado (T005)**: los esquemas existen en `src/schemas.py` con los
    nombres del contrato; los campos existentes se preservan y los aditivos son opcionales;
    los enums coinciden con el contrato (`DataNature`, `PlayStatus`, `ResponseStatus`);
    `nature`/`reason`/`type` son obligatorios y lo desconocido se representa con
    `nature=unknown` (nunca por omisión de un valor favorable); el endpoint **no** cambia
    (el cableado es T014/T018); tests de contrato en verde; lint y tests en verde.
  - **Evidencia (2026-10-19)**: `src/schemas.py` con `DataNature`, `DataQuality`,
    `Explanation`, `EligibilityCondition`, `PlayStatus`, `ResponseStatus`, `UserLocation`,
    `Recommendation` y `DondeIrResponse`; 23 tests nuevos en `tests/test_donde_ir_schemas.py`
    (validación, enums, nulos, paridad modelo↔contrato, aditivos opcionales, `unknown` no
    favorable, serialización coherente con `exclude_none`, y la respuesta **actual** de
    `/api/v1/donde-ir/ahora` validando contra `DondeIrResponse`); `ruff` OK; **64 tests OK**
    (antes 41).
  - **Cambio de contrato (justificado)**: se hicieron explícitos los `required` de los
    esquemas (campos preservados de `Recommendation`/`DondeIrResponse`, más `nature`, `reason`,
    `type`), coherente con FR-004/FR-006 y con la nota del propio contrato ("los campos
    existentes se conservan; los nuevos son aditivos"); `source` pasa a
    `[string, "null"]` (un valor desconocido no tiene procedencia que citar, FR-003); se
    extrajo `EligibilityCondition` como esquema con nombre. Los campos aditivos siguen
    opcionales. No cambia el comportamiento del endpoint. Versión del contrato: 0.2.0.
- [x] T006 Implementar el **scoring canónico único** en `src/utils/scoring.py` (una sola implementación; documentar cada peso/umbral con su justificación).
  - **Definición de terminado (T006)**: existe **una única** implementación canónica de la
    puntuación de playa en `src/utils/scoring.py`; las variantes divergentes que viven **dentro de
    ese módulo** y en sus exportaciones (`src/utils/__init__.py`) se retiran. La variante divergente
    `calculate_ideal_score` de `src/api/predictions.py` **no** forma parte de T006 y se retira en
    **T008** (alcance declarado, no ocultado). Cada peso y
    umbral está documentado con su justificación (Principio IV) y registrado en `research.md`
    (D2-bis); se respetan el modelo en dos etapas (D1) y la no compensabilidad de las exclusiones
    (FR-002); lo desconocido no se representa como favorable (FR-003); la baja ocupación no se trata
    como mérito (D3/FR-007/FR-014); el cálculo es determinista (FR-008); el contrato de la API no
    cambia; lint y tests en verde.
  - **Evidencia (2026-10-19)**: `src/utils/scoring.py` reescrito como módulo canónico:
    `CANONICAL_WEIGHTS` (calidad 0.30, oleaje 0.20, presión relativa 0.20, UV 0.15, servicios 0.15,
    suma 1.0), `MIN_DATA_COVERAGE = 0.5`, `PRESSURE_LABEL`, bandas documentadas de oleaje/UV,
    `BeachScore`, `evaluate_beach()`, `calculate_overall_score()`, `relative_pressure()`,
    `non_compensable_exclusions()`. Se retiraron `calculate_flag_score`, `calculate_jellyfish_score`,
    `calculate_safety_score`, `calculate_comfort_score`, `calculate_uv_score`, `calculate_wave_score`
    y `calculate_occupation_score` (implementaciones divergentes o absorbidas por el canónico), y se
    actualizó `src/utils/__init__.py` en consecuencia. Los cuatro consumidores reales
    (`src/api/donde_ir.py`, `src/utils/recommendation_engine.py`, `src/crud.py`) siguen funcionando:
    el tipo de retorno pasa a `Optional[float]` y `None` (desconocido) **no** se sustituye por un
    valor inventado; en el motor esas playas no se ordenan ni se recomiendan (FR-003/FR-012) y en
    `crud` van al final del orden (mismo criterio). Verificado: `ruff` OK; **102 tests OK**
    (antes 64); `pyyaml` no aplica aquí. El contrato de la API no cambia (`/donde-ir/ahora` conserva
    la forma de su respuesta; sólo cambian los valores del score, que ya visiblemente son una
    estimación de idoneidad).
  - **Registro de decisión**: `specs/001-.../research.md` §D2-bis (pesos, umbral de cobertura,
    justificación y alternativas descartadas).
  - **Puente explícito hacia T012**: las condiciones de seguridad de la propia playa (bandera roja,
    medusas) se aplican aquí como exclusiones **no compensables** en un único lugar; la etapa de
    elegibilidad completa (restricciones oficiales, incompatibilidad ambiental, datos insuficientes,
    capacidad/vulnerabilidad) y su exposición en `eligibility_conditions` pertenecen a T012. El
    término `services` arrastra una limitación conocida (el modelo no distingue "no disponible" de
    "no documentado"); se registra en `docs/OPEN_QUESTIONS.md` (Q26).
  - **Alcance declarado (lo que T006 NO hace)**: siguen existiendo dos copias divergentes que no se
    tocan aquí: `calculate_ideal_score` en `src/api/predictions.py` (se retira en **T008**) y una
    copia en el notebook no versionado `notebooks/dashboard_sandam_2026.py` (fuera del repositorio
    versionado). Hasta T008 no puede afirmarse que *todo* el repositorio tenga una sola fórmula; sí
    que el **sistema canónico** (`src/utils/scoring.py` y sus consumidores) tiene una sola.
- [x] T007 [P] Implementar tests unitarios del scoring canónico en `tests/test_scoring.py` (determinismo, límites, datos ausentes).
  - **Definición de terminado (T007)**: hay tests unitarios del scoring canónico que cubren
    determinismo, límites (bandas y rango 0..100) y datos ausentes; no se suprimen pruebas
    existentes para que pasen; lint y tests en verde.
  - **Evidencia (2026-10-19)**: `tests/test_scoring.py` nuevo (38 casos: 13 funciones + 20
    parametrizados de bandas + 5 de servicios/presión), incluyendo determinismo (50 repeticiones con
    el mismo resultado), rango acotado sobre una rejilla de entradas, `None` para calidad/oleaje/UV
    desconocidos y para cobertura insuficiente, exclusión no compensable de bandera roja incluso en
    una playa "perfecta" y con ocupación 0, bandas de oleaje/UV en sus límites exactos, y presión
    relativa desconocida ≠ 0. En `tests/test_utils.py` se adaptaron las 4 pruebas de scoring al
    comportamiento canónico (bandera roja y medusas como exclusiones; calidad `unknown` → `None`;
    score acotado en lugar del valor exacto 100). Fixtures sintéticas, etiquetadas como tales.
    Verificado: `ruff` OK; **102 tests OK** (antes 64).
- [ ] T008 Retirar la variante divergente `calculate_ideal_score` de `src/api/predictions.py` y eliminar `random` en `src/utils/predictions.py` (o marcar esas rutas como no-fiables y excluirlas de dato real).
- [ ] T009 [P] Implementar tests que garanticen ausencia de aleatoriedad en rutas de dato en `tests/test_no_random.py`.

**Checkpoint**: scoring único, migraciones operativas, sin aleatoriedad presentada como real.

---

## Phase 3: User Story 1 - Decidir a qué playa ir ahora sin trasladar la presión (Priority: P1) 🎯 MVP

**Goal**: Recomendación en dos etapas (elegibilidad → comparación) con scoring canónico.

**Independent Test**: conjunto de playas conocidas (cerrada, frágil-vacía, saturada, adecuada) →
se ordenan las elegibles y se excluyen las no elegibles, con explicación por playa.

### Tests for User Story 1

- [ ] T010 [P] [US1] Contract test del endpoint en `tests/test_api_donde_ir.py` (forma de la respuesta conforme a `contracts/donde-ir.openapi.yaml`, compatibilidad de campos existentes).
- [ ] T011 [P] [US1] Integration test de elegibilidad, no-compensación por comodidad y no-promoción de la baja afluencia en `tests/test_recommendation.py`.

### Implementation for User Story 1

- [ ] T012 [US1] Implementar la etapa de elegibilidad (condiciones de exclusión) en `src/utils/eligibility.py`.
- [ ] T013 [US1] Reescribir `src/utils/recommendation_engine.py` sobre el scoring canónico: eliminar la lógica "menos ocupación = mejor" y añadir presión relativa etiquetada (FR-007, FR-014).
- [ ] T014 [US1] Actualizar `src/api/donde_ir.py` para usar el motor en dos etapas y exponer los campos aditivos (`eligible`, `pressure_relative`, `data_quality`, `travel_time_is_estimate`).
- [ ] T015 [US1] Añadir validación y manejo de errores en `src/api/donde_ir.py` (parámetros inválidos, BD sin datos).

**Checkpoint**: US1 funcional y probable de forma independiente → MVP.

---

## Phase 4: User Story 2 - Entender por qué se desaconseja una playa (Priority: P2)

**Goal**: Explicaciones legibles por recomendación y por desaconsejación.

**Independent Test**: evaluar una playa cerrada y una saturada → cada respuesta incluye un motivo distinto y legible.

### Tests for User Story 2

- [ ] T016 [P] [US2] Tests de explicaciones en `tests/test_explanations.py` (motivo por exclusión, por incertidumbre y por propuesta).

### Implementation for User Story 2

- [ ] T017 [US2] Extender `src/utils/recommendations.py` para producir explicaciones estructuradas (reutilizando las reglas de seguridad/alertas existentes).
- [ ] T018 [US2] Exponer las explicaciones en `src/api/donde_ir.py` (`/ahora` y `/evaluar-playa/{name}`) según el contrato.

**Checkpoint**: US1 y US2 funcionales de forma independiente.

---

## Phase 5: User Story 3 - Reconocer la incertidumbre y no recomendar a ciegas (Priority: P3)

**Goal**: Etiquetado de datos, estados de incertidumbre y degradación sin invención.

**Independent Test**: con observaciones ausentes/caducadas y con fuente caída, la respuesta marca el estado y no produce recomendación favorable por defecto.

### Tests for User Story 3

- [ ] T019 [P] [US3] Tests de datos ausentes, inválidos y caducados en `tests/test_data_quality.py`.
- [ ] T020 [P] [US3] Test de degradación ante fallo de fuente (mock de error) en `tests/test_degradation.py`.

### Implementation for User Story 3

- [ ] T021 [US3] Implementar el etiquetado de calidad del dato y la procedencia (FR-004, FR-015) en `src/crud.py` y `src/utils/recommendation_engine.py` (lectura de metadatos desde observaciones).
- [ ] T022 [US3] Implementar los estados `insufficient_data` y `no_suitable_alternatives` (FR-012) en `src/api/donde_ir.py` y su reflejo en `src/schemas.py`.
- [ ] T023 [US3] Implementar degradación explícita ante fallo de fuentes externas (FR-009) en `src/integrations/*` y `src/api/weather.py`.

**Checkpoint**: las tres historias son independientemente funcionales.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Alineación documental, ADRs y validación final.

- [ ] T024 [P] Alinear `README.md` y `docs/API_GUIDE.md` con el contrato y el ámbito Mallorca.
- [ ] T025 [P] Redactar ADR `docs/adr/0002-modelo-de-datos-y-procedencia.md` y `docs/adr/0004-plataforma-de-despliegue.md`.
- [ ] T026 [P] Actualizar `docs/OPEN_QUESTIONS.md` con decisiones pendientes (capacidad, aforo, rutas).
- [ ] T027 Ejecutar `specs/001-sustainable-beach-recommendation/quickstart.md` y verificar todos los criterios.
- [ ] T028 [P] Ajustar `.github/workflows/ci.yml` para incluir test de migraciones Alembic.
- [ ] T029 Ejecutar `/speckit.converge` y resolver las brechas restantes.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias.
- **Foundational (Phase 2)**: depende de Setup — **bloquea** todas las historias.
- **User Stories (Phase 3+)**: dependen de Foundational; luego pueden ir en paralelo o por prioridad.
- **Polish (Phase 6)**: depende de las historias completadas.

### User Story Dependencies

- **US1 (P1)**: tras Foundational; sin dependencias de otras historias.
- **US2 (P2)**: tras Foundational; reutiliza el motor de US1 pero es probable por sí sola.
- **US3 (P3)**: tras Foundational; puede probarse con datos ausentes sin US1/US2.

### Within Each User Story

- Tests antes de implementación (deben fallar primero).
- Modelos/esquemas → servicios (utils) → endpoints.

### Parallel Opportunities

- T004, T005, T007, T009 en paralelo (archivos distintos).
- T010 y T011 en paralelo.
- T016, T019, T020 en paralelo.
- T024, T025, T026, T028 en paralelo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup.
2. Phase 2: Foundational (**crítico**).
3. Phase 3: US1.
4. **PARAR y VALIDAR**: probar US1 de forma independiente con `quickstart.md`.
5. Demo/deploy si procede.

### Incremental Delivery

1. Setup + Foundational → base lista.
2. US1 → validar → MVP.
3. US2 → validar → explicaciones.
4. US3 → validar → incertidumbre.
5. Polish → alineación y convergencia.

## Notes

- [P] = archivos distintos, sin dependencias.
- Verificar que los tests fallan antes de implementar.
- Commit tras cada tarea o grupo lógico.
- No implementar en esta fase del SDD (solo planificación); la implementación empieza con `/speckit.implement` tras revisión.
