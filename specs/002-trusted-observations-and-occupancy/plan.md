# Implementation Plan: Observaciones fiables, procedencia y presión turística

**Branch**: `002-trusted-observations-and-occupancy` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-trusted-observations-and-occupancy/spec.md`

**Estado**: planificación. **No se implementa en esta fase** (sin migración, sin cambios de
rutas, sin integración de fuentes en producción).

## Summary

Introducir un modelo de **observaciones con procedencia y vigencia** y romper la cadena que
convierte valores por defecto en hechos: la ocupación desconocida no se mostrará como `0 %`
ni como mérito, el seed será `synthetic`, y cada valor usado en una recomendación será
trazable a una fuente, un método y un instante. Se hará con una migración **aditiva**, un
catálogo de fuentes y un protocolo de validación de heurísticos. No se cambian los pesos del
scoring ni se integran fuentes nuevas en producción durante esta fase.

## Technical Context

**Language/Version**: Python 3.11+ (entorno verificado: 3.13)

**Primary Dependencies**: FastAPI, SQLAlchemy async, Pydantic v2, Alembic, pytest, ruff.
No se añaden dependencias de infraestructura (sin Redis, sin colas, sin PostGIS).

**Storage**: PostgreSQL (producción) y SQLite en memoria (tests). Migraciones Alembic
(`0003` propuesta). Sin ENUM nativos ni JSONB (ADR 0005).

**Testing**: pytest + SQLite en memoria; tests de contrato; reloj inyectable para validez;
mocks de fuentes para degradación. No se usan datos reales en tests.

**Target Platform**: API FastAPI en contenedor (ver ADR 0004); CI con PostgreSQL 16.

**Project Type**: proyecto único (`src/`, `tests/`, `docs/`, `specs/`).

**Performance Goals**: la consulta de observaciones vigentes por playa debe resolverse con
índices; no se añade latencia perceptible a `/donde-ir/ahora` (objetivo: < 50 ms adicionales
en el conjunto actual de ~20 playas). Es un objetivo de diseño, no una medición.

**Constraints**:
- Compatibilidad de contrato: campos existentes preservados; cambios aditivos.
- Sin secretos en código; claves por entorno (`Settings`).
- Sin datos personales; solo agregados.
- Sin fuentes nuevas en producción sin licencia/permiso verificados.
- Sin cambios de pesos: `water_quality 0.30`, `sea_state 0.20`, `solar_exposure 0.15`.

**Scale/Scope**: Mallorca; ~20 playas en el seed; variables principales de la spec 001;
4 fuentes candidatas (AEMET, SOCIB, Copernicus, calidad oficial) y 1 referencia de
ocupación (Calvià) sujeta a convenio.

## Constitution Check

*GATE: debe pasar antes de implementar.* Los `✅` significan que **el plan** cumple el
principio; **no** que la implementación exista.

| Principio | Cumplimiento | Nota |
|---|---|---|
| I. Prioridad ambiental y de seguridad | ✅ | La presión no compensa exclusiones; la ocupación no es mérito. |
| II. Veracidad y no invención | ✅ | `unknown` explícito; seed `synthetic`; sin defaults que afirmen hechos. |
| III. Incertidumbre explícita | ✅ | `nature`, `validation_status`, `status`; `confidence=null` sin validación. |
| IV. Una sola implementación | ✅ | Un contrato de observación y un evaluador de vigencia; sin duplicar scoring. |
| V. Trazabilidad | ✅ | `observation_id`, `source_id`, `method_id`, `observed_at`. |
| VI. Pruebas | ✅ | Tests de contrato, validez, degradación y migración. |
| VII. Privacidad | ✅ | Agregados; prohibido `individual`. |
| VIII. Simplicidad / sin infra nueva | ✅ | Tabla + catálogos; sin colas ni servicios nuevos. |
| IX. Migraciones reversibles | ✅ | `0003` aditiva y `downgrade`; sin reconstruir tablas. |

**Sin excepciones**: no se requiere ADR de excepción. Las decisiones de diseño se registran
en `research.md` y `data-model.md`; si la implementación cambia el alcance, se abrirá ADR.

## Project Structure

### Documentation (this feature)

```text
specs/002-trusted-observations-and-occupancy/
├── spec.md
├── research.md
├── data-model.md
├── plan.md
├── tasks.md
├── quickstart.md
├── contracts/
│   ├── README.md
│   ├── observation.schema.json
│   └── donde-ir-observations.openapi.yaml
└── checklists/
    └── requirements.md
```

### Source Code (futuro; no creado en esta fase)

```text
src/
├── models.py                     # + Observation, DataSource, Method, Variable, ...
├── schemas.py                    # + ObservationCreate/Read, DataQuality ampliado
├── crud.py                       # consultas de observaciones; sin ocupación como mérito
├── api/
│   ├── donde_ir.py               # data_quality real; pressure unknown
│   ├── recommendations.py        # sin "playa tranquila" por default
│   ├── search.py                 # sin "Ocupación menor" por default
│   ├── external_data.py          # estado de ocupación, no solo número
│   └── dashboard.py              # media solo con observaciones válidas
├── utils/
│   ├── observations.py           # (nuevo) vigencia, resolución, coverage
│   ├── recommendations.py        # estados explícitos; sin afirmaciones por default
│   ├── fallback.py               # no convertir None en False
│   ├── predictions.py            # validated=false, confidence=null
│   └── scoring.py                # sin cambios de pesos
└── integrations/
    ├── aemet_observations.py     # (nuevo) adaptador
    ├── socib_observations.py     # (nuevo) adaptador
    ├── copernicus_observations.py# (nuevo) adaptador
    └── water_quality.py          # (nuevo) adaptador oficial
alembic/versions/
└── 0003_observations.py          # (nuevo) migración aditiva
tests/
├── test_observations_model.py
├── test_observations_validity.py
├── test_unknown_not_favorable.py
├── test_occupancy_not_merit.py
├── test_provenance_contract.py
├── test_synthetic_seed.py
├── test_source_degradation.py
└── test_migration_0003.py
```

**Structure Decision**: se mantiene la estructura existente. La lógica de vigencia y
resolución vive en `src/utils/observations.py` (sin BD ni red); el acceso a datos en
`src/crud.py`; los adaptadores en `src/integrations/`; los routers solo transportan.

## Fases de implementación (futuras)

### Fase 0 — Auditoría y contrato (sin cambios de comportamiento)

- Inventario de datos y defaults; informe de filas afectadas.
- Contrato JSON Schema y pruebas de validación del contrato.
- Definición de variables, unidades y reglas de validez por variable.
- Criterio de “fuente activa” (licencia + permiso + revisión).

**Salida**: informe de auditoría, contrato aprobado, lista de fuentes bloqueadas.

### Fase 1 — Modelo y migración aditiva

- Tablas `data_sources`, `variables`, `methods`, `transformations`, `validation_records`,
  `ingestion_runs`, `observations`.
- Columnas de estado en `beaches` y `data_origin`.
- Índices y `downgrade`.
- Tests de migración en PostgreSQL y SQLite.
- Backfill conservador (seed → `synthetic`; sin origen → `unknown`).

**Salida**: esquema nuevo, sin cambios de respuesta todavía.

### Fase 2 — Dominio y contrato de respuesta

- `src/utils/observations.py`: vigencia, resolución de contradicciones, `coverage`.
- `DataQuality` ampliado; `pressure_relative` nullable.
- Tests de “desconocido no favorable” y “ocupación no es mérito”.
- Endpoints aditivos: `occupancy_status`, `jellyfish_status`, `data_quality` completo.

**Salida**: la API distingue observado/desconocido/synthetic; sigue sin fuentes nuevas.

### Fase 3 — Adaptadores (una fuente por vez)

Orden recomendado por riesgo/valor:

1. **AEMET**: meteo; API documentada; clave gratuita. Bajo riesgo.
2. **SOCIB**: oleaje/temperatura/corrientes; API documentada; revisar términos.
3. **Copernicus Marine**: contexto regional; licencia verificada; no es observación puntual.
4. **Calidad oficial**: observación estacional; PDF/posible descarga; verificar licencia.
5. **Calvià / Consell / Gemelo Digital**: solo con convenio; no raspar.

Cada adaptador: `source`, `method`, `validity`, `ingestion_run`, idempotencia, dry-run,
degradación, tests con fixtures (no datos reales).

**Salida**: observaciones reales con procedencia para las variables cubiertas.

### Fase 4 — Consumidores y limpieza

- `/donde-ir`: `data_quality` real; `pressure_relative` solo si hay observación.
- `/recommendations`: eliminar “✓ Playa tranquila” y “✓ Sin medusas” por default.
- `/search`: eliminar “Ocupación menor” si no hay observación válida.
- `/external`: exponer estado, no solo número.
- `/dashboard`: media solo con observaciones válidas; declarar cobertura.
- `fallback.py`: no convertir `None` en `False`.

**Salida**: ninguna ruta premia el desconocido.

### Fase 5 — Validación de heurísticos

- Protocolo de `research.md` §7.
- Datos de referencia (Calvià, con permiso) y línea base.
- Métricas, informe y decisión.
- Si no se valida: `validated=false`, no se usa como factor; si se valida: registrar
  `ValidationRecord` y documentar límites.

**Salida**: heurísticos validados o retirados; nunca “caja negra” con apariencia de certeza.

### Fase 6 — Compatibilidad y relajación de defaults

- Tests de contrato con clientes existentes.
- Decidir `null` vs `0` en campos legados; documentar.
- Migración posterior para retirar defaults de Python; `downgrade` reversible.
- Actualizar `docs/API_GUIDE.md`, `docs/MIGRATIONS.md` y ADR si cambia el contrato.

## Orden de dependencias

```text
Fase 0 ──▶ Fase 1 ──▶ Fase 2 ──▶ Fase 3 ──▶ Fase 4 ──▶ Fase 5 ──▶ Fase 6
                         │                         │
                         └──── tests de contrato ──┘
```

- La Fase 3 no bloquea la Fase 2; se puede empezar con una fuente.
- La Fase 5 requiere datos de referencia y permiso; puede quedar bloqueada sin afectar a
  las fases 1–4.
- La Fase 6 requiere decisión de producto sobre compatibilidad.

## Riesgos y mitigaciones

| Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|
| Migración rompe SQLite o PostgreSQL | Media | Alto | Tipos portables; tests en ambos; `downgrade` probado |
| Clientes dependen de `0`/`false` | Media | Medio | Campos aditivos; fase de transición; tests de contrato |
| Fuente sin licencia | Alta | Alto | Catálogo con `terms_reviewed_at`; bloqueo si falta |
| Datos de referencia insuficientes | Alta | Medio | No validar; mantener `validated=false`; no inventar |
| Coste/latencia de adaptadores | Media | Medio | Ingesta por lotes; caché en BD; sin llamadas en request |
| Confusión “tiempo real” | Media | Alto | Umbral de latencia declarado; etiqueta `stale` |
| Privacidad en aforos | Baja | Alto | Solo agregados; prohibido individual |

## Complexity Tracking

No hay violaciones de la constitución. La complejidad añadida (7 tablas) se justifica por
la necesidad de trazabilidad y vigencia; se evita JSONB/ENUM y se mantiene un solo módulo
de dominio. Si en la implementación se comprueba que `methods`/`transformations` pueden
plegarse en `data_sources`, se simplificará antes de la migración.

## Rollback

- `alembic downgrade 0002` elimina las tablas/columnas nuevas.
- El backfill no borra información; si se modifica `data_status`, se guarda el valor previo
  en una tabla de auditoría o se documenta el valor original.
- Los cambios de consumidores son reversibles por commit; no hay borrado de datos.
- Las fuentes nuevas se pueden desactivar (`status = paused`) sin borrar observaciones.

## Out of Scope (confirmado)

- Implementar en esta fase.
- Cambiar pesos o introducir ocupación en el score.
- Resolver Q1 (capacidad) o Q11/Q14 (catálogos).
- Integrar Google/TomTom o cualquier proveedor de rutas.
- Machine learning o modelos predictivos nuevos.
- Reescritura de las rutas de búsqueda.
