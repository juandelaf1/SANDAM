# Feature Specification: Recomendación de playas consciente de la presión turística y la capacidad de acogida

**Feature Branch**: `001-sustainable-beach-recommendation`

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "Recomendación de playas consciente de la presión turística y la capacidad de acogida para el endpoint /donde-ir y el scoring canónico"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Decidir a qué playa ir ahora sin trasladar la presión (Priority: P1)

Una persona que está en Mallorca quiere decidir a qué playa desplazarse ahora mismo. Indica su
ubicación y recibe una lista de playas **elegibles**, ordenada, con el tiempo estimado de llegada
y una explicación breve de por qué se propone cada una. Las playas con restricciones oficiales o
condiciones incompatibles no aparecen como alternativas normales. La recomendación no empuja a
ocupar una playa frágil solo porque esté vacía.

**Why this priority**: es el valor central del producto: ayudar a tomar una decisión informada que
reduzca la presión y evite desplazamientos inútiles. Sin esto no hay SANDAM.

**Independent Test**: con un conjunto de playas de condiciones conocidas (una saturada, una
cerrada, una frágil poco concurrida y una adecuada), el resultado debe ordenar las elegibles y
excluir las no elegibles, con una explicación por playa.

**Acceptance Scenarios**:

1. **Given** una playa con una restricción oficial vigente incompatible con la visita, **When** se
   calculan alternativas, **Then** esa playa no se propone como alternativa normal y se indica el
   motivo.
2. **Given** una playa poco concurrida pero clasificada como vulnerable o sin capacidad
   justificada para absorber más visitantes, **When** se calculan alternativas, **Then** no se
   promueve automáticamente por su baja afluencia.
3. **Given** dos playas igualmente elegibles con distinta presión relativa, **When** se ordenan,
   **Then** la de menor presión se propone antes, siempre que las condiciones de seguridad y
   elegibilidad se mantengan.

---

### User Story 2 - Entender por qué se desaconseja una playa (Priority: P2)

Un usuario ve que una playa concreta no aparece o aparece desaconsejada y quiere saber por qué.
El sistema explica el motivo en lenguaje comprensible (restricción, riesgo, presión elevada, falta
de datos fiables o existencia de una alternativa mejor).

**Why this priority**: la transparencia es lo que distingue una recomendación fiable de una caja
negra; sin explicación, el usuario no confía ni cambia de decisión.

**Independent Test**: solicitar la evaluación de una playa cerrada y de una saturada y comprobar
que cada respuesta incluye un motivo distinto y legible.

**Acceptance Scenarios**:

1. **Given** una playa descartada por restricción, **When** se consulta su evaluación, **Then** la
   respuesta indica que existe una restricción incompatible con la visita.
2. **Given** una playa descartada por falta de datos fiables, **When** se consulta su evaluación,
   **Then** la respuesta lo indica y **no** la presenta como segura.

---

### User Story 3 - Reconocer la incertidumbre y no recomendar a ciegas (Priority: P3)

Cuando no hay información suficiente y fiable para una playa, el sistema lo declara en lugar de
inventar un valor. Si no existe ninguna alternativa adecuada, lo comunica en vez de forzar una
recomendación.

**Why this priority**: evita decisiones engañosas y protege al usuario y al ecosistema; es la
traducción directa del principio de veracidad del dato.

**Independent Test**: con observaciones ausentes o caducadas, comprobar que la respuesta marca el
estado del dato y no produce una recomendación favorable por defecto.

**Acceptance Scenarios**:

1. **Given** una playa sin observaciones válidas de una variable relevante, **When** se evalúa,
   **Then** el estado de esa variable es "desconocido" y no se trata como favorable.
2. **Given** que ninguna playa cumple los criterios de elegibilidad y adecuación, **When** se
   piden recomendaciones, **Then** el sistema indica que no hay alternativas adecuadas.

---

### Edge Cases

- ¿Qué ocurre si una fuente externa no responde o devuelve un error? → El sistema debe seguir
  funcionando con los datos disponibles, marcar lo desconocido y no inventar valores.
- ¿Qué ocurre si dos fuentes contradicen un mismo dato? → Debe existir una política explícita de
  resolución (prioridad y marca de procedencia); nunca presentar ambos como si fueran igual de
  fiables.
- ¿Qué ocurre si una observación es antigua pero la única disponible? → Se marca como caducada
  según su regla de validez y no se usa como si fuera actual.
- ¿Qué ocurre si el usuario está muy lejos o no queda suficiente luz natural? → La alternativa
  debe descartarse o marcarse como no viable por tiempo, explicando el motivo.
- ¿Qué ocurre si una playa cumple criterios de seguridad pero no tiene capacidad de referencia
  conocida? → Se reconoce la incertidumbre; no se le atribuye una capacidad inexistente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST clasificar cada playa como **elegible** o **no elegible** antes de
  compararla con otras, aplicando condiciones de exclusión (restricciones oficiales, riesgos
  relevantes o incompatibilidad ambiental documentada).
- **FR-002**: El sistema MUST NOT permitir que factores de comodidad (distancia, tiempo de viaje,
  baja ocupación, servicios) neutralicen una condición de exclusión.
- **FR-003**: El sistema MUST NOT tratar la ausencia de datos como una condición favorable ni como
  una condición desfavorable: la trata como desconocida.
- **FR-004**: Cada valor relevante en la respuesta MUST estar clasificado como observación,
  estimación, predicción (con horizonte) o dato caducado/desconocido.
- **FR-005**: El sistema MUST NOT presentar resultados aleatorios o simulados como predicciones
  reales. Las predicciones solo se etiquetan como tales si proceden de un método definido.
- **FR-006**: Cada recomendación MUST incluir una explicación del motivo por el que se propone,
  y cada desaconsejación el motivo por el que se descarta.
- **FR-007**: El sistema MUST NOT promover una playa como alternativa basándose únicamente en su
  baja afluencia cuando exista una vulnerabilidad, restricción o capacidad no justificada.
- **FR-008**: Para entradas y observaciones idénticas, el resultado MUST ser reproducible cuando el
  método sea determinista.
- **FR-009**: Los fallos de fuentes externas MUST NOT provocar la invención de datos ni resultados
  engañosos; el sistema degrada de forma explícita.
- **FR-010**: El comportamiento de recomendación MUST preservar el contrato de la API existente
  siempre que sea posible; cualquier cambio incompatible MUST justificarse y documentarse.
- **FR-011**: La respuesta MUST tener en cuenta el horizonte temporal de las observaciones y, para
  la conveniencia, el tiempo estimado de llegada y el tiempo de luz natural restante, etiquetando
  claramente toda estimación.
- **FR-012**: El sistema MUST poder declarar que **no dispone de información suficiente** para una
  recomendación fiable, y MUST poder declarar que **no hay alternativas adecuadas**.
- **FR-013**: El sistema MUST distinguir explícitamente la distancia geográfica de la estimación de
  tiempo de viaje por carretera, y MUST NOT atribuir a la estimación una precisión de la que carece.
- **FR-014**: Cuando no exista una capacidad de acogida de referencia defendible, el sistema MUST
  reconocer la incertidumbre y, si usa indicadores de presión, MUST etiquetarlos como relativos y
  no como límites ecológicos oficiales.
- **FR-015**: El sistema MUST registrar la procedencia (fuente) de cada valor usado en una
  recomendación para permitir su trazabilidad.
- **FR-016**: Debe existir **un único** comportamiento canónico de puntuación y ranking; no se
  admiten implementaciones divergentes del mismo concepto.

### Key Entities *(include if feature involves data)*

- **Playa**: identidad y datos relativamente estáticos (nombre, ubicación, región, servicios,
  sensibilidad ecológica, restricciones documentadas, capacidad de referencia si existe).
- **Observación**: valor obtenido de una fuente externa o medición legítima, con fuente, referencia
  temporal de observación y de obtención, y regla de validez.
- **Predicción**: resultado calculado para un horizonte definido, con método identificado, entradas
  relevantes y limitaciones declaradas.
- **Indicador de presión relativa**: métrica derivada, etiquetada como relativa, sin pretensión de
  umbral ecológico.
- **Recomendación**: resultado para un usuario (playas elegibles ordenadas) con sus explicaciones.
- **Restricción / condición de exclusión**: hecho documentado que impide recomendar una playa.
- **Fuente de datos**: origen legítimo de datos, con condiciones de uso y licencias conocidas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las respuestas de recomendación identifican, para cada playa mostrada u
  omitida, si es elegible y, si no lo es, el motivo.
- **SC-002**: El 100% de los valores relevantes de la respuesta están etiquetados según su
  naturaleza (observación/estimación/predicción/caducado/desconocido).
- **SC-003**: En una prueba con fuente externa caída, el 0% de las respuestas contiene valores
  inventados y el sistema sigue respondiendo.
- **SC-004**: Dada la misma entrada y las mismas observaciones, dos ejecuciones producen el mismo
  orden de alternativas (100% de coincidencia).
- **SC-005**: Ningún caso de prueba con restricción oficial vigente produce esa playa como
  alternativa normal (0% de falsos positivos de elegibilidad).
- **SC-006**: Un usuario puede explicar, a partir de la respuesta, por qué se le propone o descarta
  una playa en al menos un caso de prueba guiado.
- **SC-007**: Cuando no hay alternativas adecuadas o datos suficientes, el 100% de esos casos lo
  comunica de forma explícita en lugar de devolver una recomendación forzada.

## Assumptions

- El ámbito inicial es Mallorca; no se asume disponibilidad de datos fuera de ese ámbito.
- No se asume la existencia de un sistema fiable de medición de visitantes en tiempo real para
  todas las playas; la presión puede requerir estimación y debe etiquetarse como tal.
- No se asume la existencia de capacidades de acogida oficiales por playa; se tratarán como
  desconocidas si no hay una fuente defendible (`TODO(CAPACITY_METHODOLOGY)`).
- No se asume disponibilidad de un proveedor de rutas por carretera; el tiempo de viaje se tratará
  como estimación etiquetada mientras no exista una fuente fiable.
- Se reutiliza el contrato actual de la API de recomendación para preservar compatibilidad; los
  cambios incompatibles se documentarán en `contracts/`.
- La meteorología real disponible (p. ej. AEMET) puede usarse como observación, siempre etiquetada
  con su hora y su procedencia.
- Están fuera de alcance: medición universal de visitantes, machine learning, autenticación,
  notificaciones push, multi-región y migración de plataforma.
