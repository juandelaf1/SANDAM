# Feature Specification: Observaciones fiables, procedencia y presión turística

**Feature Branch**: `002-trusted-observations-and-occupancy`

**Created**: 2026-10-20

**Status**: Draft (definición; **no implementada**)

**Input**: User description: "Diseñar el modelo de observaciones fiables, procedencia y
presión turística de SANDAM: distinguir observación de estimación, predicción, dato
caducado, desconocido y sintético; impedir que la ocupación desconocida se presente como
0 % o como mérito; y dejar preparada la validación de los heurísticos con datos reales."

**Depende de**: `specs/001-sustainable-beach-recommendation/` (cerrada funcionalmente, con
brechas de veracidad registradas en `convergence-audit.md`).

**No implementa**: tabla de observaciones, migración de esquema, cambios en rutas de
búsqueda, integración de fuentes en producción ni cambios de pesos del scoring.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Saber qué está observado y qué no (Priority: P1)

Una persona consulta una playa y ve, para cada valor relevante, si es una **observación**
(de una fuente y un instante concretos), una **estimación**, una **predicción**, un dato
**caducado**, **desconocido** o **sintético** (demostración). La ausencia de dato no se
presenta como “0 %”, “sin medusas”, “sin socorrista” ni “condiciones óptimas”.

**Why this priority**: sin esta distinción, cualquier recomendación puede afirmar hechos
que no se han observado. Es la base de los Principios II y V de la constitución y de
FR-003/FR-004 de la spec 001.

**Independent Test**: con una playa sembrada solo con defaults, la respuesta debe declarar
`unknown` en ocupación, medusas, sargazo y servicios no documentados; ningún texto debe
afirmar que la playa está vacía, limpia o sin medusas. Con una observación válida y
vigente, la respuesta debe mostrar su fuente y su hora.

**Acceptance Scenarios**:

1. **Dado** un registro sin observación de ocupación, **cuando** se consulta la playa,
   **entonces** la respuesta indica `occupancy_status = "unknown"` y no muestra `0 %`,
   “playa tranquila” ni una presión relativa numérica.
2. **Dado** un registro con una observación de ocupación de las 10:00 y `valid_until` a las
   10:30, **cuando** se consulta a las 11:00, **entonces** el valor se marca `stale` y no se
   usa como si fuera actual.
3. **Dado** un registro con `jellyfish_present = false` por defecto y sin observación,
   **cuando** se consulta, **entonces** se muestra `jellyfish_status = "unknown"` y no
   “sin medusas”.
4. **Dado** un registro creado por el seed, **cuando** se consulta, **entonces** se marca
   `synthetic` y no `live`.

---

### User Story 2 - No recibir una playa vacía como premio (Priority: P1)

Una persona pide una recomendación. La ocupación baja **no** se usa como mérito ni como
desempate. Si no hay observación de ocupación, la presión turística se declara
**desconocida**; nunca se presenta como “0 %” ni como “poca afluencia”. Las playas frágiles
no se promueven por estar vacías.

**Why this priority**: FR-007 y la prioridad ambiental de la constitución. El
comportamiento actual de `/recommendations` y `/search` premia la ocupación heredada por
defecto (`src/utils/recommendations.py:73-74`, `src/crud.py:240-241`).

**Independent Test**: dos playas idénticas en todo salvo la ocupación observada (5 % vs
95 %) deben obtener el mismo `score` canónico y el mismo orden; la de 5 % no debe recibir
la etiqueta “playa tranquila” si no hay observación válida. Con ocupación desconocida, la
respuesta debe incluir `pressure_status = "unknown"`.

**Acceptance Scenarios**:

1. **Dado** un conjunto de playas con la misma calidad, oleaje y UV, **cuando** se
   recomiendan, **entonces** la ocupación no altera `score` ni el orden.
2. **Dado** un `current_occupation` heredado (default `0`), **cuando** se genera la
   explicación, **entonces** no aparece “✓ Playa tranquila” ni “Ocupación menor”.
3. **Dado** un indicador de presión calculado, **cuando** se muestra, **entonces** se
   etiqueta como **relativo** y no como capacidad oficial o límite ecológico.
4. **Dado** un filtro `occupation_max`, **cuando** la ocupación es desconocida, **entonces**
   la playa no se excluye silenciosamente como si tuviera `0`; se declara que no se puede
   evaluar el filtro.

---

### User Story 3 - Trazar cada dato hasta su fuente (Priority: P2)

Una persona responsable de datos puede registrar una observación con su variable, valor,
unidad, fuente, método, instante de observación, instante de obtención, validez, resolución
espacial y estado de validación. Puede consultar qué observaciones sustentan una
recomendación y detectar contradicciones entre fuentes.

**Why this priority**: FR-015 y el Principio V. Sin trazas no se puede auditar una
recomendación ni retirar un dato defectuoso.

**Independent Test**: registrar dos observaciones de la misma variable con fuentes
distintas y comprobar que (a) cada respuesta puede enlazar con su observación, (b) la
política de prioridad es explícita y (c) no se mezclan valores en silencio.

**Acceptance Scenarios**:

1. **Dado** un alta de observación, **cuando** falta `source`, `method` u `observed_at`,
   **entonces** se rechaza o se marca como no válida para decisiones.
2. **Dada** una recomendación, **cuando** se consulta su traza, **entonces** cada valor
   usado referencia un `observation_id` (o declara `unknown`).
3. **Dadas** dos fuentes contradictorias, **cuando** se resuelve, **entonces** se aplica
   una prioridad documentada y se conserva la fuente descartada como evidencia.
4. **Dada** una observación con licencia o condiciones de uso no verificadas, **cuando** se
   intenta usar en producción, **entonces** el sistema la rechaza.

---

### User Story 4 - No confundir demostración con realidad (Priority: P2)

Quien opera el sistema puede distinguir datos de demostración (seed, fixtures, valores
introducidos a mano) de observaciones reales. Los datos sintéticos nunca se presentan como
observaciones ni se usan para recomendaciones de producción sin una etiqueta visible.

**Why this priority**: el seed actual se marca `DataStatus.live` (`seed_data.py:536`), lo
que contradice FR-005 y la prohibición de presentar simulaciones como datos reales.

**Independent Test**: ejecutar el seed y consultar `/donde-ir/ahora`; la respuesta debe
marcar las playas sembradas como `synthetic` (o excluirlas de producción) y no como
`live`.

**Acceptance Scenarios**:

1. **Dado** un registro del seed, **cuando** se expone en la API, **entonces** su naturaleza
   es `synthetic` y su procedencia es `seed`.
2. **Dado** un entorno de producción sin observaciones reales, **cuando** se pide una
   recomendación, **entonces** el sistema responde `insufficient_data` antes que recomendar
   con datos sintéticos.
3. **Dado** un fixture de test, **cuando** se ejecutan los tests, **entonces** no se
   confunde con una observación de producción.

---

### User Story 5 - Validar o retirar los heurísticos (Priority: P3)

Un equipo de datos puede contrastar los heurísticos de ocupación y medusas con una fuente de
referencia (por ejemplo, aforos de un municipio o actualizaciones de socorristas), medir su
error y decidir si se mantienen, se ajustan o se retiran.

**Why this priority**: Q28. Un test verde no demuestra exactitud; sin validación, un
heurístico solo puede etiquetarse como predicción no validada y sin confianza.

**Independent Test**: ejecutar el protocolo con un conjunto de referencia y obtener
métricas reproducibles (MAE/RMSE/sesgo para ocupación; precisión/recall/F1 y matriz de
confusión para medusas), con la línea base y el tamaño de muestra declarados.

**Acceptance Scenarios**:

1. **Dado** un heurístico sin validar, **cuando** se expone, **entonces** declara
   `validated = false`, `method` y `horizon`, y no declara confianza.
2. **Dado** un conjunto de referencia, **cuando** se evalúa, **entonces** se reportan
   métricas, cobertura, sesgo y limitaciones; no se eligen umbrales después de ver los
   resultados.
3. **Dado** un heurístico que no supera la línea base acordada, **cuando** se cierra la
   validación, **entonces** se retira o se mantiene solo como informativo, nunca como
   factor de recomendación.

---

### Edge Cases

- **Fuente caída**: se conserva el último dato válido solo si se etiqueta `stale`; si no,
  se declara `unknown`. Nunca se rellena con un valor por defecto.
- **Dos fuentes contradictorias**: prioridad documentada + `observed_at`; se conserva la
  fuente descartada. No se promedian valores sin declararlo.
- **Observación sin hora**: no puede ser `current`; se trata como no válida para decisión.
- **Observación futura o reloj inconsistente**: se rechaza o se marca `invalid` con motivo.
- **Unidad distinta** (°C vs K, m vs cm): se normaliza con una transformación identificada;
  nunca se compara sin unidad.
- **Resolución espacial distinta**: una observación regional (p. ej. modelo marino) no se
  presenta como medición puntual de la playa; se declara la resolución.
- **Ocupación como porcentaje o como conteo**: se conserva la unidad; no se convierte sin
  `capacity` defendible.
- **Playas con `max_capacity` del seed**: no se usa como capacidad oficial; si se usa para
  presión relativa, se etiqueta como referencia no validada.
- **Datos personales**: no se almacenan ubicaciones individuales ni identificadores de
  personas; solo agregados.
- **Cambio de licencia o retirada de una fuente**: se debe poder dejar de usar y purgar sus
  observaciones sin romper el histórico.

---

## Clarifications (resueltas en esta fase)

- **C1 — Ocupación**: sigue siendo un indicador de **presión relativa**, nunca un mérito ni
  un límite ecológico. No se cambia su peso porque no está en el scoring (FR-007 de la spec
  001). El campo existente se conserva por compatibilidad; se añade un estado explícito
  (`observed / estimated / stale / unknown / synthetic`).
- **C2 — Defaults heredados**: el objetivo es que `NULL`/`unknown` sea explícito. La
  migración será **aditiva y por fases**: primero columnas de estado y procedencia, luego
  relajación de defaults; no se reconstruye la tabla ni se borran datos.
- **C3 — Seed**: se clasifica como `synthetic`. No se usa para recomendaciones de
  producción; en desarrollo se muestra con etiqueta.
- **C4 — Esquema**: cualquier cambio exige migración Alembic reversible (ADR 0003). Esta
  especificación **no** la implementa.
- **C5 — Fuentes**: solo se integra lo que tenga acceso documentado y condiciones de uso
  verificadas. No se raspa una web sin permiso ni se eluden autenticaciones.
- **C6 — Heurísticos**: no se declaran exactos ni se les asigna confianza sin protocolo de
  validación. Mientras tanto, `validated = false`.
- **C7 — Tiempo**: `observed_at`, `fetched_at` y `valid_until` en UTC; la API los expone en
  ISO 8601 con zona. La validez se evalúa contra un reloj inyectable en tests.
- **C8 — Compatibilidad**: los campos actuales se mantienen; los nuevos son aditivos. Un
  cambio incompatible se documenta en `contracts/` y se justifica.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Toda observación MUST registrar: `observation_id`, entidad/playa, variable,
  valor, unidad, `source_id`, `method_id`, `observed_at`, `fetched_at`, `valid_until`,
  resolución espacial, naturaleza, estado de validación y, si aplica, incertidumbre.
- **FR-002**: El sistema MUST usar un vocabulario cerrado de naturaleza: `observation`,
  `user_report`, `estimate`, `prediction`, `historical`, `synthetic`, `unknown`.
- **FR-003**: Naturaleza, estado de validación y vigencia MUST ser dimensiones separadas;
  una observación puede ser real y estar caducada, o ser una estimación validada.
- **FR-004**: Solo las observaciones **válidas y vigentes** pueden sustentar una decisión
  como dato actual. Las caducadas MUST marcarse `stale` y no usarse como actuales.
- **FR-005**: La ausencia de observación MUST NOT convertirse en `0`, `false`, cadena vacía,
  “sin riesgo” ni “condiciones óptimas”.
- **FR-006**: El sistema MUST distinguir “ausencia confirmada” de “desconocido” (p. ej.
  `jellyfish_status = absent` frente a `unknown`; `has_lifeguard = false` documentado
  frente a `unknown`).
- **FR-007**: La ocupación MUST NOT ser un mérito, desempate ni factor de score. Una
  ocupación baja no puede promover una playa.
- **FR-008**: Si la ocupación es desconocida, la presión MUST presentarse como `unknown`;
  MUST NOT mostrarse `0 %` ni una `pressure_relative` numérica.
- **FR-009**: La cobertura de datos (`coverage`) MUST contar solo valores con observación
  válida y procedencia; un default no cuenta como cobertura.
- **FR-010**: Toda estimación o predicción MUST declarar `method`, versión, `horizon`,
  entradas y `validated`; sin validación, `confidence` MUST ser `null`.
- **FR-011**: Los datos de demostración, seed y fixtures MUST clasificarse `synthetic` y
  MUST NOT presentarse como `live` ni usarse en recomendaciones de producción.
- **FR-012**: Ante fallo de una fuente, el sistema MUST degradar explícitamente: `unknown`,
  `stale` o `unavailable`, sin inventar valores ni mantener una apariencia de actualidad.
- **FR-013**: Ante contradicción entre fuentes, MUST existir una política documentada de
  prioridad y una traza de ambas observaciones; no se mezclan en silencio.
- **FR-014**: Los cambios de contrato MUST ser aditivos siempre que sea posible; los campos
  existentes se preservan. Cualquier cambio incompatible se documenta y se justifica.
- **FR-015**: Ninguna fuente puede usarse en producción si su licencia o condiciones de uso
  no están verificadas y registradas.
- **FR-016**: El sistema MUST NOT almacenar datos personales ni ubicaciones individuales;
  las observaciones de afluencia MUST ser agregadas.
- **FR-017**: La migración de registros existentes MUST clasificar su procedencia. Si no se
  puede demostrar el origen, se marca `unknown`/`synthetic`; MUST NOT inventarse una fuente.
- **FR-018**: Cada valor usado en una recomendación MUST ser trazable a una observación o
  declarar explícitamente `unknown`.
- **FR-019**: Las marcas temporales MUST tener una zona/UTC declarada y una regla de validez
  por variable; la evaluación MUST ser determinista con un reloj inyectable.
- **FR-020**: El sistema MUST NOT usar la expresión “tiempo real” si la latencia de la
  fuente no cumple un umbral declarado y verificable.

### Key Entities

- **Observation**: valor de una variable para una playa, con fuente, método, tiempos,
  validez, resolución, naturaleza y validación.
- **Source**: origen legítimo (nombre, URI, licencia, condiciones, prioridad, estado,
  contacto responsable).
- **Method**: procedimiento de medición/estimación/predicción, con versión y referencias.
- **Variable**: catálogo de variables, unidad canónica, tipo, cadencia esperada y regla de
  validez por defecto.
- **ValidityRule**: ventana de validez y criterios de caducidad por variable/fuente.
- **ValidationRecord**: resultado de validar un método contra un conjunto de referencia
  (métricas, muestra, fecha, responsable).
- **PressureIndicator**: indicador derivado de ocupación, etiquetado como relativo, con
  `status` y observaciones de entrada.
- **ProvenanceClass**: `observed / reported / estimated / predicted / synthetic / unknown`.
- **IngestionRun**: ejecución de ingesta (fuente, inicio, fin, resultado, errores, filas).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de los valores relevantes de una recomendación declara su naturaleza
  y su estado de vigencia (`current`/`stale`/`unknown`/`synthetic`).
- **SC-002**: El 0 % de las respuestas presenta una ocupación desconocida como `0 %`,
  “playa tranquila”, “poca afluencia” o `pressure_relative = 0`.
- **SC-003**: El 0 % de las observaciones caducadas se usa como dato actual.
- **SC-004**: El 100 % de las observaciones usadas en una recomendación es trazable a
  `source_id`, `method_id`, `observed_at` y `observation_id`.
- **SC-005**: El 0 % de los registros migrados recibe una procedencia inventada; los no
  demostrables quedan `unknown`/`synthetic`.
- **SC-006**: El 0 % del seed se presenta como `live` u observación real.
- **SC-007**: Todo heurístico expuesto declara `validated`; sin validación, `confidence` es
  `null` y no se usa como factor de recomendación.
- **SC-008**: La suite de contrato pasa sin eliminar campos existentes; las pruebas de
  compatibilidad cubren `/donde-ir`, `/recommendations`, `/search` y `/external`.
- **SC-009**: La validación de un heurístico produce métricas reproducibles con línea base,
  cobertura y limitaciones; el resultado es auditable.

---

## Assumptions

- El ámbito sigue siendo **Mallorca**; no se asume disponibilidad de datos homogénea en
  todas las playas.
- No existe todavía una fuente universal de aforo en tiempo real; la ocupación será
  observación en pocas playas, estimación en otras y desconocida en la mayoría.
- No se asume una capacidad de acogida oficial por playa (Q1); `max_capacity` del seed no es
  una capacidad validada.
- Se prioriza la compatibilidad del contrato actual y la migración aditiva.
- La verificación de licencias y condiciones de uso es un requisito previo, no un supuesto.
- Quedan fuera de alcance: reparto adaptativo de demanda, clusterización, machine learning,
  integración de nuevos proveedores en producción, reescritura de las rutas de búsqueda y
  cambio de pesos del scoring.

---

## Out of Scope

- Implementar la tabla de observaciones o la migración en esta fase.
- Conectar fuentes nuevas en producción.
- Cambiar los pesos canónicos (`water_quality 0.30`, `sea_state 0.20`,
  `solar_exposure 0.15`) o introducir la ocupación en el score.
- Resolver la metodología de capacidad de acogida (Q1).
- Medición universal de visitantes o identificación individual.
- Publicar una predicción con confianza sin validación.
