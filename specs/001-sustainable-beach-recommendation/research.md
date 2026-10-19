# Phase 0 — Research: baseline as-is y decisiones

**Feature**: 001-sustainable-beach-recommendation
**Date**: 2026-10-19

Este documento registra (a) el comportamiento **real** del sistema actual, verificado sobre el
código, y (b) las decisiones técnicas que resuelven los vacíos, con alternativas evaluadas.
Sustituye a cualquier descripción contradictoria de la documentación histórica.

## Baseline as-is (verificado en código)

### `GET /api/v1/donde-ir/ahora` (`src/api/donde_ir.py` + `src/utils/recommendation_engine.py`)

1. Carga **todas** las playas de la BD (`select(Beach)`).
2. Convierte cada playa a dict con un subconjunto de campos (`_beach_to_dict`).
3. Calcula `score = calculate_overall_score(playa)` (`src/utils/scoring.py`).
4. `donde_ir_ahora(...)` recorre las playas y, para cada una:
   - distancia = Haversine;
   - tipo de vía = `determinar_tipo_carretera(distancia)` (heurística por distancia: <20 autopista,
     <50 comarcal, resto montaña);
   - tiempo de viaje = `distancia/60 * factor * 60` minutos (velocidad asumida 60 km/h);
   - status temporal comparando el tiempo de viaje con `sol_restante_min - 60` (buffer): "recomendada"
     / "marginal" / "no_merece";
   - `score_final = score * max(0.5, 1 - distancia/100)`.
5. Descarta las "no_merece" (salvo `incluir_marginales=true`) y ordena por `score_final` desc.

**Problemas detectados**:

- El atardecer es una **tabla fija mes→hora** (`ATARDECER_MALLORCA`), no un cálculo, y se etiqueta
  en la respuesta como si fuera un dato (`hora_atardecer`).
- El tiempo de viaje se presenta como minutos exactos derivados de la distancia en línea recta y
  una clasificación de vía inventada por distancia (no hay proveedor de rutas).
- El ranking **premia la baja ocupación** (ver scoring), lo que puede empujar visitantes a calas
  frágiles o vacías — conflicto directo con el objetivo de distribuir la presión.

### Scoring: tres implementaciones divergentes

| Implementación | Ubicación | Pesos | Ocupación |
|----------------|-----------|-------|-----------|
| A | `src/utils/scoring.py::calculate_overall_score` | bandera 30, ocupación 25, calidad 20, medusas 15, UV 5, oleaje 5 | `<=30% → 100 pts` (menos = mejor) |
| B | `src/api/predictions.py::calculate_ideal_score` | ocupación 30, bandera 30, medusas 20, calidad 10, sostenibilidad 10 | `(100 - ocupación) * 0.30` (menos = mejor) |
| C | Documentación | `docs/PROJECT_CONTEXT.md`: bandera 30/ocupación 25/calidad 20/medusas 15/UV 5/oleaje 5 (≈A); `docs/CONTEXTO_MAESTRO.md`: ocupación 30/bandera 30/medusas 20/calidad 10/sostenibilidad 10 (≈B) | — |

Además, `calculate_ideal_score` (B) está **definida dentro de un router** y no se comparte.

### Recomendaciones por playa (`src/api/recommendations.py` + `src/utils/recommendations.py`)

Genera mensajes y alertas por reglas (bandera, medusas, UV, oleaje, calidad, ocupación, socorrista,
sargazo). No usa el scoring ni distingue procedencia del dato. Reutilizable como base de las
explicaciones.

### Aleatoriedad (`src/utils/predictions.py`)

`generate_forecast` y `calculate_shade_availability` usan `random` (ocupación, temperatura, clima,
viento, sombra por acantilado/vegetación). Se exponen en `/predictions/forecast/{name}` y
`/predictions/shade/{name}`. **Presentan resultados aleatorios como predicciones.**

### Datos y procedencia

- `seed_data.py` carga 20 playas de Mallorca con valores **estáticos** (no observaciones).
- El modelo tiene `data_status` (`live`/`estimated`/`unavailable`) y `last_updated`, pero
  `data_status` **no se usa** en la lógica de recomendación.
- `src/integrations/aemet_client.py` sí consulta AEMET real (usado por `/weather`). SOCIB/CAIB/
  Govern/scrapers existen pero **no los usa la app** (solo scripts sueltos).
- No hay campos de **fuente** ni de **hora de observación** separada de la de obtención.

## Decisiones

### D1 — Modelo de decisión en dos etapas

**Decisión**: la recomendación se divide en (1) elegibilidad (exclusiones: restricciones oficiales,
riesgos relevantes, incompatibilidad ambiental) y (2) comparación de alternativas elegibles.
**Rationale**: garantiza el Principio I/III; una suma ponderada única permite que la comodidad
compense una exclusión.
**Alternativas**: (a) suma ponderada única con pesos grandes a seguridad — descartada: sigue siendo
compensable; (b) reglas ad-hoc dispersas — descartada: no explicable ni testeable.

### D2 — Scoring canónico único

**Decisión**: un solo comportamiento canónico en `src/utils/scoring.py`. `calculate_ideal_score` de
`src/api/predictions.py` se retira o se reemplaza por el canónico; `docs/*` dejan de describir
fórmulas propias.
**Rationale**: Principio IV. Hoy hay resultados incoherentes entre endpoints.
**Alternativas**: mantener dos fórmulas con documentación cruzada — descartada: no resuelve la
divergencia.

### D3 — La baja ocupación no es un mérito por sí mismo

**Decisión**: la ocupación se trata como **indicador de presión relativa**, no como "cuanto menos,
mejor". Una playa vacía puede desaconsejarse por vulnerabilidad, restricción o capacidad no
justificada (FR-007).
**Rationale**: Principio I y objetivo de producto; evita trasladar la presión.
**Alternativas**: mantener `100 - ocupación` como bonus — descartada por contradecir el objetivo.

### D4 — Etiquetado y procedencia del dato (mínimo viable)

**Decisión**: separar observación/estimación/predicción/caducado/desconocido y añadir metadatos
mínimos de trazabilidad (fuente, hora de observación, hora de obtención, regla/validez). Se
implementará **tras** disponer de migración (ADR 0003).
**Rationale**: Principio II; sin ello no se puede cumplir SC-002/SC-003.
**Alternativas**: envolver sin cambiar el modelo (solo respuesta) — insuficiente para trazabilidad
persistente; se admite como paso intermedio si el esquema se congela.

### D5 — Distancia ≠ tiempo de viaje

**Decisión**: exponer la distancia geográfica como dato y el tiempo de viaje como **estimación
etiquetada**; no atribuir precisión de carretera (FR-013).
**Rationale**: Principio II; hoy se presenta `distancia/60*factor` como minutos exactos.
**Alternativas**: integrar un proveedor de rutas — fuera de alcance del MVP; se registra como
posible evolución en `docs/OPEN_QUESTIONS.md`.

### D6 — Horizonte solar como estimación

**Decisión**: la hora de atardecer se mantiene como estimación etiquetada (tabla) o se calcula, pero
en ningún caso se presenta como observación.
**Rationale**: Principio II.

### D7 — Fuentes externas: revisar condiciones antes de integrar

**Decisión**: no se añaden nuevas fuentes (aforo, corrientes, etc.) sin revisar condiciones de uso,
licencias y privacidad.
**Rationale**: Principio VIII y Restricciones de Producto.
**TODO**: `TODO(DATA_SOURCES)` en la constitución.

### D8 — Sin infraestructura nueva

**Decisión**: no se introducen Redis, PostGIS, colas ni edge para este MVP.
**Rationale**: Principio IX. La escala (20 playas) no lo justifica.
**Alternativas**: caché/geoespacial avanzado — reevaluar solo con un requisito medido.

## Resumen de NEEDS CLARIFICATION resueltos

No quedaron `[NEEDS CLARIFICATION]` en la spec; los vacíos se resolvieron como supuestos (spec) o
como decisiones (D1–D8). Las decisiones que **no** pueden resolverse responsablemente con la
información disponible (metodología de capacidad, fuentes de aforo, plataforma de despliegue) se
trasladan a `docs/OPEN_QUESTIONS.md`.
