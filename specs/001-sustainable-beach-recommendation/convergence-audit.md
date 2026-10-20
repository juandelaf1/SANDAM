# Auditoría de convergencia — spec 001

**Fecha**: 2026-10-20
**Alcance**: contrastar `spec.md` (FR-001…FR-016, SC-001…SC-007) y `tasks.md`
(T001…T029) con el código realmente presente en `src/`.
**Método**: lectura del código y de los tests; ejecución de `ruff check src tests seed_data.py`
y `pytest` (133 tests). No se ejecutó `/speckit.converge` como comando remoto: la
evaluación es manual y verificable.

> Este documento **no reescribe** el historial de la spec 001 ni cambia sus criterios.
> Registra el estado real para no declarar satisfecho lo que el código no cumple.
> Las brechas que requieren diseño nuevo se abordan en
> `specs/002-trusted-observations-and-occupancy/`.

## 1. Resultado por requisito

Leyenda: **Cumplido** = el contrato se cumple y hay prueba; **Parcial** = existe
implementación, pero el contrato no se cumple en todos los casos; **Limitado por datos** =
la implementación es correcta pero no hay fuente defendible; **No cumplido** = el código
contradice el requisito.

| Requisito | Estado | Evidencia / brecha |
|---|---|---|
| FR-001 Elegibilidad antes de comparar | Cumplido | `src/utils/eligibility.py`; `/donde-ir/ahora` aplica la etapa 1 antes de ordenar. Tests de elegibilidad. |
| FR-002 Condiciones no compensables | Cumplido | La elegibilidad es independiente del score; `non_compensable_exclusions` delega en `eligibility.py`. |
| FR-003 Ausencia de datos ≠ favorable/desfavorable | **Parcial** | Los campos anulables (`water_temp`, `uv_index`, `wave_height`) se tratan como desconocidos. Pero `current_occupation`, `jellyfish_present`, `sargasso_level`, `posidonia_present` y `has_*` tienen `default` en `src/models.py:71,82,85,86,92-97`, de modo que la ausencia se materializa como `0`/`False`. `src/utils/fallback.py:19-21` convierte `jellyfish_present=None` en `False`. |
| FR-004 Clasificar cada valor (observación/estimación/predicción/caducado/desconocido) | **Parcial / No cumplido en los defaults** | `data_quality` solo cubre 4 variables (`src/utils/recommendation_engine.py:255-260`). `water_quality` se etiqueta `observation` aunque su valor sea `"unknown"`; `current_occupation` se etiqueta `observation` siempre porque nunca es `None`. No se etiquetan `flag_color`, `jellyfish_present`, `sargasso_level` ni servicios. `source` es siempre `None`. |
| FR-005 No presentar aleatorios/simulados como reales | **Parcial** | `src/utils/predictions.py` ya no usa `random` y declara `validated=False`. Pero `seed_data.py:536` marca los registros del seed como `DataStatus.live`; el seed son valores estáticos sin fuente ni instante de observación. Además, `BeachCreate.data_status` tiene `default=DataStatus.live` (`src/schemas.py:44`), de modo que un alta por API también nace como “live” sin observación. `/external/sources` declara fuentes `active`/`partial` (`src/api/external_data.py:123-139`). |
| FR-006 Explicación por recomendación/descarte | Cumplido | `generar_explicacion` y `explanation` en cada recomendación; tests de explicaciones. Limitación: la explicación puede citar ocupación heredada por defecto. |
| FR-007 La baja afluencia no promueve por sí sola | **Parcial** | `/donde-ir` no usa ocupación como mérito (score canónico). Siguen usándola como mérito: `src/utils/recommendations.py:47-51,73-74` (`✓ Playa tranquila`), `src/crud.py:240-241` (`Ocupación menor`), y `/external` expone la ocupación sin estado. |
| FR-008 Reproducibilidad | Cumplido | Tests deterministas, incluido el control de hora (`4a7729c`). |
| FR-009 Fallo de fuente sin invención | **Parcial** | `/weather` devuelve `{"error": …}` sin inventar (`src/api/weather.py`). Pero `src/integrations/alerts_system.py` fabrica un estado “todas las playas operan” con fuente “112 Catalunya”, y `src/integrations/scraper_scrapling.py` usa `50` como ocupación por defecto cuando falla el parseo. `alerts_system` no está importado por `src/main.py`; los scrapers sí se exponen en `/scraper/*` (`src/main.py:18`, `src/api/scraper_endpoints.py`). |
| FR-010 Compatibilidad del contrato | Cumplido | Campos aditivos en `/donde-ir`; contratos en `contracts/`. |
| FR-011 Horizonte temporal y llegada/luz | **Parcial** | `travel_time_is_estimate: true` y `sol_restante_min`. No hay `valid_until` por observación; `hora_llegada` usa `datetime.now()` local (`recommendation_engine.py:218`), no una referencia temporal explícita. |
| FR-012 `insufficient_data` / `no_suitable_alternatives` | Cumplido | `status` global; tests Caso B. |
| FR-013 Distancia ≠ tiempo de viaje | Cumplido | `distancia_km` y `tiempo_viaje_min` separados; estimación declarada. |
| FR-014 Incertidumbre de capacidad / presión relativa | **Parcial / Limitado por datos** | `relative_pressure` se etiqueta como relativa, pero se calcula con `current_occupation` por defecto `0`, produciendo `0.0` cuando no hay observación. `max_capacity` del seed no tiene metodología (Q1). No se usa como límite ecológico (correcto). |
| FR-015 Procedencia de cada valor usado | **Parcial** | `data_quality.source` es `None` en todas las variables. No existe registro de observaciones ni `observed_at`/`fetched_at`. No hay trazabilidad valor → fuente. |
| FR-016 Un único scoring canónico | Cumplido en la API | `src/utils/scoring.py` es la única implementación usada por rutas. `notebooks/dashboard_sandam_2026.py` (sin seguimiento) contiene una copia propia; queda fuera del código desplegado, pero no debe tomarse como referencia. |

## 2. Resultado por criterio de éxito

| Criterio | Estado | Comentario |
|---|---|---|
| SC-001 Elegibilidad y motivo en cada playa | Cumplido | `eligible` + `eligibility_conditions`. |
| SC-002 100 % de valores etiquetados por naturaleza | **No cumplido** | Solo 4 variables y con etiquetas incorrectas para defaults (FR-004). |
| SC-003 0 % de valores inventados con fuente caída | **Parcial** | El camino principal y `/weather` degradan. Persisten valores fabricados en integraciones no conectadas al camino principal y en el seed marcado `live`. |
| SC-004 Orden reproducible | Cumplido | Test determinista. |
| SC-005 0 % de falsos positivos de elegibilidad | Cumplido para las condiciones derivables | Solo se emiten condiciones derivables; las no verificables quedan como `insufficient_data`. |
| SC-006 Explicación comprensible | Cumplido | `explanation.reason` + `factors`. |
| SC-007 Ausencia de alternativas/datos explícita | Cumplido | `status` y tests. |

## 3. Estado real de las tareas de cierre

| Tarea | Estado real | Matiz |
|---|---|---|
| T021 — etiquetado de calidad y procedencia | Implementada **con defecto** | Existe `data_quality`, pero etiqueta defaults como observación y no incluye `source`. No satisface FR-004/FR-015 en todos los casos. |
| T023 — degradación de fuentes externas | Implementada **con alcance limitado** | Correcta en `/weather` y en el camino principal. La afirmación “en `src/integrations/*`” es más amplia que lo verificado: hay integraciones con datos fabricados y defaults. |
| T024 — README/API_GUIDE | Cumplida | `docs/API_GUIDE.md` sección 9 documenta el comportamiento real. |
| T025 — ADR 0002/0004/0005 | Cumplida | ADRs coherentes; no se añadieron ADR redundantes. |
| T026 — OPEN_QUESTIONS | Cumplida | Q26–Q28 añadidas. |
| T027 — quickstart | Cumplida | Comandos verificados. |
| T028 — CI con PostgreSQL/Alembic | Cumplida por inspección | Configuración válida; **no ejecutada en GitHub Actions** en este entorno. |
| T029 — convergencia | Cumplida como análisis | Este documento es el registro de brechas; no convierte las brechas en cumplimientos. |

## 4. Brechas que pasan a la spec 002

1. **Valores por defecto que afirman un hecho** (`current_occupation=0`, `has_*=False`,
   `jellyfish_present=False`, `sargasso_level=0`) y su uso como señal favorable.
2. **Procedencia ausente**: no hay `source`, `observed_at`, `fetched_at`, `valid_until`
   ni identificador de observación.
3. **`data_quality` incompleto e incorrecto** para valores desconocidos.
4. **Ocupación como mérito** en `/recommendations`, `/search` y `/external`.
5. **Seed y datos simulados presentados como `live`**.
6. **Integraciones con datos fabricados o defaults** (`alerts_system`, `scraper_scrapling`).
7. **Inexistencia de validación** de los heurísticos de ocupación/medusas.

## 5. Conclusión

La spec 001 está **funcionalmente cerrada en su alcance de recomendación** (elegibilidad,
scoring canónico, explicaciones, estados de incertidumbre y determinismo), pero **no está
plenamente satisfecha en veracidad y procedencia del dato** (FR-003/FR-004/FR-007/FR-014/
FR-015). Las tareas T021 y T023 no deben interpretarse como una garantía global mientras
existan los defectos anteriores. La spec 002 define el trabajo necesario para cerrarlos.
