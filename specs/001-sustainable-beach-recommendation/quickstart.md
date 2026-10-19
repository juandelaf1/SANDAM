# Quickstart — Validación de la feature 001

Guía para validar de extremo a extremo, cuando se implemente, que la recomendación cumple la
especificación. **No contiene código de implementación** (eso vive en `tasks.md`).

## Prerrequisitos

- Python 3.11+ y dependencias instaladas (`pip install -r requirements.txt`).
- Base de datos lista (PostgreSQL vía `docker compose up -d postgres`) **o** los tests con SQLite.
- Datos de ejemplo: `python seed_data.py`.
- API en marcha: `uvicorn src.main:app --reload` (`http://localhost:8000`).

## Verificaciones automatizadas

```bash
pytest                      # suite completa (SQLite en memoria)
pytest tests/test_scoring.py -q          # reglas de dominio del scoring canónico
pytest tests/test_recommendation.py -q   # elegibilidad, exclusiones, determinismo, degradación
ruff check src tests seed_data.py
```

Resultado esperado: todo en verde y `ruff` sin errores.

## Escenarios de validación manual

Usar `/docs` o `curl`. Sustituir `lat`/`lon` por coordenadas de Mallorca (p. ej. 39.57, 2.65).

1. **Elegibilidad por restricción (FR-001, SC-005)**
   - Preparar una playa con una restricción oficial vigente.
   - `GET /api/v1/donde-ir/ahora?lat=39.57&lon=2.65`
   - Esperado: esa playa **no** aparece como alternativa normal; si se consulta su evaluación, se
     indica el motivo.

2. **No premiar la playa vacía frágil (FR-007)**
   - Marcar una playa poco concurrida como vulnerable/sin capacidad justificada.
   - Esperado: no se promueve por estar vacía; aparece explicación si se descarta.

3. **Datos ausentes/desconocidos no son favorables (FR-003, SC-003)**
   - Vaciar una variable relevante (p. ej. `flag_color`) dejándola en `unknown`.
   - Esperado: el estado del dato es `unknown`; **no** se interpreta como seguro.

4. **Degradación ante fallo de fuente (FR-009, SC-003)**
   - Simular caída de la fuente (sin red o mock de error).
   - Esperado: la API sigue respondiendo; **cero** valores inventados; estado `insufficient_data`
     si aplica.

5. **Determinismo (FR-008, SC-004)**
   - Dos llamadas idénticas con las mismas observaciones.
   - Esperado: mismo orden de alternativas.

6. **Sin alternativas adecuadas (FR-012, SC-007)**
   - Escenario donde todas las playas son no elegibles o inadecuadas.
   - Esperado: `status = no_suitable_alternatives` y `recomendaciones` vacía; sin recomendación forzada.

## Criterios de aceptación cubiertos

- [ ] Restricciones oficiales excluyen (FR-001, FR-002, SC-005)
- [ ] Comodidad no compensa exclusiones (FR-002)
- [ ] Ausencia de datos ≠ favorable (FR-003, SC-003)
- [ ] Datos etiquetados por naturaleza y procedencia (FR-004, FR-015, SC-002)
- [ ] Sin `random` presentado como real (FR-005)
- [ ] Explicaciones presentes (FR-006, SC-001, SC-006)
- [ ] No se promueve la baja afluencia por sí sola (FR-007)
- [ ] Determinismo (FR-008, SC-004)
- [ ] Degradación sin invención (FR-009, SC-003)
- [ ] Compatibilidad de contrato (FR-010, `contracts/`)
- [ ] Horizonte temporal / luz restante etiquetados (FR-011)
- [ ] Declara incertidumbre y ausencia de alternativas (FR-012, SC-007)
- [ ] Distancia ≠ tiempo de viaje (FR-013)
- [ ] Capacidad con fundamento o incertidumbre explícita (FR-014)
- [ ] Scoring canónico único (FR-016)
