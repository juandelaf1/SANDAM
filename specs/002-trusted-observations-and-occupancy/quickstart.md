# Quickstart — Validación de la spec 002

Guía para validar, **cuando se implemente**, que las observaciones son fiables, que la
procedencia es trazable y que el desconocido no se presenta como favorable. **No contiene
código de implementación** (eso vivirá en `tasks.md`).

> Hoy esta guía **no se puede ejecutar**: la spec 002 no está implementada. Los comandos y
> rutas nuevos se indican como objetivo.

## Prerrequisitos (cuando exista la implementación)

- Python 3.11+ y dependencias instaladas.
- Base de datos con migraciones al día: `alembic upgrade head`.
- Datos de ejemplo etiquetados como sintéticos: `python seed_data.py`.
- API en marcha: `uvicorn src.main:app --reload` (`http://localhost:8000`).

## Verificaciones automatizadas (objetivo)

```bash
pytest                                          # suite completa
pytest tests/test_unknown_not_favorable.py -q   # el desconocido no es favorable
pytest tests/test_occupancy_not_merit.py -q     # la ocupación no es mérito
pytest tests/test_observations_validity.py -q   # vigencia y caducidad
pytest tests/test_provenance_contract.py -q     # trazabilidad y contrato
pytest tests/test_synthetic_seed.py -q          # seed = synthetic
pytest tests/test_migration_0003.py -q          # migración y downgrade
ruff check src tests seed_data.py
```

Resultado esperado: todo en verde; `ruff` sin errores; migración reversible.

## Escenarios de validación manual

Usar `/docs` o `curl`. Sustituir `lat`/`lon` por coordenadas de Mallorca (p. ej. 39.57, 2.65).

1. **Ocupación desconocida no es 0 % ni “playa tranquila” (FR-005, FR-008)**
   - Partir de una playa sin observación de ocupación.
   - `GET /api/v1/donde-ir/ahora?lat=39.57&lon=2.65`
   - Esperado: `occupancy_status = "unknown"`; `pressure_relative = null`; **no** aparece
     `0 %`, “playa tranquila” ni “poca afluencia”.

2. **Observación caducada no se usa como actual (FR-004)**
   - Insertar una observación con `valid_until` en el pasado.
   - Esperado: estado `stale`; no cuenta para `coverage`; no sustenta una decisión como dato
     actual.

3. **Medusas desconocidas ≠ “sin medusas” (FR-006)**
   - Playa con `jellyfish_status = "unknown"`.
   - Esperado: no aparece “✓ Sin medusas”; se indica que no hay dato.

4. **Servicios no documentados ≠ “sin socorrista” (FR-006)**
   - Playa sin documentación de servicios.
   - Esperado: `services_status.lifeguard = "unknown"`; no se afirma ausencia.

5. **Seed es sintético (FR-011, FR-005)**
   - Ejecutar `seed_data.py` y consultar.
   - Esperado: `data_origin = "seed"`, `data_status = "synthetic"`; **no** `live`; en
     producción no se usa para recomendar.

6. **Trazabilidad de un valor (FR-001, FR-018)**
   - Consultar una recomendación con datos observados.
   - Esperado: cada valor relevante tiene `observation_id`, `source` y `observed_at`; si no
     hay observación, `nature = "unknown"`.

7. **Contradicción entre fuentes (FR-013)**
   - Cargar dos observaciones de la misma variable con fuentes distintas.
   - Esperado: se aplica la prioridad documentada; no se mezclan; la fuente descartada queda
     como evidencia.

8. **Fallo de fuente (FR-012)**
   - Simular error/timeout del adaptador.
   - Esperado: `unknown`/`stale`/`unavailable`; cero valores inventados; la API responde.

9. **Ocupación no altera el orden (FR-007)**
   - Dos playas idénticas salvo la ocupación observada (5 % vs 95 %).
   - Esperado: mismo `score`; el orden no cambia por la ocupación.

10. **Predicción sin validar (FR-010)**
    - Consultar un heurístico.
    - Esperado: `validated = false`, `confidence = null`, `method` y `horizon` declarados; no
      se usa como factor de recomendación.

11. **Compatibilidad de contrato (FR-014)**
    - Cliente antiguo que lee `current_occupation` y `jellyfish_present`.
    - Esperado: los campos siguen existiendo; los nuevos son aditivos; la documentación
      advierte que el campo legado no debe interpretarse como hecho sin su estado.

12. **“Tiempo real” con umbral (FR-020)**
    - Medir la latencia de una fuente.
    - Esperado: solo se usa “tiempo real” si cumple el umbral declarado y verificado.

## Criterios de aceptación cubiertos

- [ ] El 100 % de los valores relevantes declara naturaleza y vigencia (SC-001)
- [ ] La ocupación desconocida no aparece como 0 % ni como mérito (SC-002)
- [ ] Ninguna observación caducada se usa como actual (SC-003)
- [ ] Cada valor usado es trazable a fuente/método/hora (SC-004)
- [ ] La migración no inventa procedencia (SC-005)
- [ ] El seed no se presenta como `live` (SC-006)
- [ ] Todo heurístico declara `validated`; sin validación, `confidence` es null (SC-007)
- [ ] La suite de contrato pasa sin eliminar campos (SC-008)
- [ ] La validación de heurísticos produce métricas reproducibles (SC-009)
