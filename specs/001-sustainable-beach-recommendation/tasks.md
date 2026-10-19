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

- [ ] T001 Verificar y registrar la línea base real: ejecutar `pytest` y `ruff check src tests seed_data.py` y anotar resultados (sin cambios de código).
- [ ] T002 [P] Unificar la fuente de verdad documental: crear `docs/PRODUCT_VISION.md` y añadir banner de "histórico/obsoleto" a `docs/CONTEXTO_MAESTRO.md` y `docs/PROJECT_CONTEXT.md`; alinear ámbito a Mallorca en `docs/API_GUIDE.md`.

**Checkpoint**: línea base conocida y documentación alineada.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura y consolidación que MUST estar lista antes de cualquier historia.

**⚠️ CRITICAL**: ninguna historia puede empezar hasta terminar esta fase.

- [ ] T003 Introducir Alembic y una migración inicial segura del esquema actual: `alembic.ini`, `alembic/env.py`, `alembic/versions/0001_initial.py` (ver `docs/adr/0003-migraciones-alembic.md`).
- [ ] T004 [P] Añadir campos de trazabilidad/capacidad a `src/models.py` (`protection_status`, `access_restrictions`, `capacity_reference`, `capacity_method`, `vulnerability_level`) y su migración `alembic/versions/0002_metadata_fields.py`. Regla: `capacity_reference` sin `capacity_method` es inválido.
- [ ] T005 [P] Definir esquemas aditivos de respuesta en `src/schemas.py` (`DataQuality`, `Explanation`, `Recommendation`, `DondeIrResponse`) según `specs/001-sustainable-beach-recommendation/contracts/donde-ir.openapi.yaml`.
- [ ] T006 Implementar el **scoring canónico único** en `src/utils/scoring.py` (una sola implementación; documentar cada peso/umbral con su justificación).
- [ ] T007 [P] Implementar tests unitarios del scoring canónico en `tests/test_scoring.py` (determinismo, límites, datos ausentes).
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

- [ ] T021 [US3] Implementar el etiquetado de calidad del dato y la procedencia (FR-004, FR-015) en `src/utils/donde_ir`/`src/crud.py` (lectura de metadatos).
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
