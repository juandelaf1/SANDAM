<!--
Sync Impact Report
==================
- Version change: (none) → 1.0.0  (documento inicial)
- Modified principles: n/a (creación inicial)
- Added sections: Core Principles (I–IX); Restricciones de Producto y Alcance;
  Flujo de Trabajo y Puertas de Calidad; Governance.
- Removed sections: n/a
- Follow-up TODOs:
  * TODO(CAPACITY_METHODOLOGY): definir metodología y fuentes para la capacidad de
    acogida por playa antes de usar cualquier umbral en producción.
  * TODO(DATA_SOURCES): confirmar condiciones de uso y licencias de cada fuente externa
    (AEMET, SOCIB, CAIB, platgesdebalears) antes de integrarlas.
  * Este bloque es material de revisión, no gobernanza; puede retirarse tras la revisión.
-->

# SANDAM Constitution

## Core Principles

### I. Prioridad ambiental y de seguridad (NON-NEGOTIABLE)

La seguridad y la protección ambiental están por encima de cualquier conveniencia. Las
restricciones oficiales (cierres, prohibiciones, banderas rojas), los riesgos relevantes y las
condiciones incompatibles con el uso sostenible actúan como **condiciones de exclusión**: no
pueden compensarse con ventajas de comodidad, distancia o baja afluencia. El sistema MUST poder
desaconsejar el uso de una playa aunque esté vacía.

Rationale: el objetivo del producto es reducir la presión sobre el litoral, no redistribuirla
hacia lugares más frágiles ni exponer a los usuarios a riesgos evitables.

### II. Veracidad, trazabilidad y separación del dato (NON-NEGOTIABLE)

El sistema MUST NOT presentar datos simulados, aleatorios, caducados o inferidos como
observaciones actuales. Cada dato relevante MUST clasificarse como observación válida,
estimación, predicción (con horizonte), dato caducado o dato desconocido. Cada valor MUST
conservar su procedencia (fuente) y sus referencias temporales. La ausencia de datos MUST NOT
interpretarse como una condición favorable.

Rationale: la utilidad del producto depende de que el usuario pueda distinguir lo que se sabe de
lo que no; un dato inventado es peor que un dato ausente.

### III. Modelo de decisión en dos etapas y transparencia (NON-NEGOTIABLE)

La recomendación MUST separar la **elegibilidad** (qué playas no deben recomendarse por
restricciones, riesgos o incompatibilidad ambiental) de la **comparación de alternativas
elegibles**. Ningún factor de comodidad puede superar una condición de exclusión. Toda
desaconsejación y toda propuesta de alternativa MUST poder explicarse de forma comprensible.

Rationale: una única suma ponderada permite que la conveniencia gane a la seguridad; la
explicabilidad es requisito de un producto que pretende influir en decisiones de movilidad.

### IV. Un único modelo canónico de scoring

Debe existir **un solo** comportamiento canónico de puntuación y ranking. Se prohíben
implementaciones paralelas o divergentes del mismo concepto. Cualquier cambio de pesos, umbrales
o factores MUST justificarse con una fuente, un estudio, una prueba o una decisión de producto
explícita, y MUST quedar registrado.

Rationale: hoy coexisten varias fórmulas contradictorias; la divergencia produce resultados
incoherentes y erosiona la confianza.

### V. Desarrollo guiado por especificaciones (SDD)

Todo cambio funcional relevante MUST nacer de una especificación en `specs/`, con criterios de
aceptación verificables, y seguir el flujo Spec Kit (specify → plan → tasks → implement →
converge). La implementación no puede adelantarse a la especificación aprobada.

Rationale: reduce ambigüedad, evita trabajo improvisado y hace auditable por qué existe cada
comportamiento.

### VI. Verificación automatizada, reproducibilidad y determinismo

Los criterios de aceptación MUST verificarse con pruebas automatizadas. Los recorridos críticos
MUST cubrir datos ausentes, inválidos y caducados, condiciones de exclusión y fallos de fuentes
externas. Con entradas y observaciones idénticas, el resultado MUST ser reproducible cuando el
método sea determinista. No se declara una tarea terminada porque el código compile.

Rationale: sin verificación reproducible no hay garantía de que el producto cumpla lo acordado.

### VII. Migraciones explícitas y reproducibles

Todo cambio de esquema MUST realizarse mediante una migración explícita, versionada y reversible
(Alembic). `create_all()` no sustituye a una migración. Los cambios de esquema sin migración
MUST considerarse incompletos.

Rationale: la evolución del modelo de datos debe ser auditable y desplegable sin sorpresas.

### VIII. Protección de secretos, privacidad y minimización

Ningún secreto MUST versionarse, registrarse en logs ni incluirse en documentación o informes.
Las credenciales se gestionan por configuración (variables de entorno). Los datos personales MUST
minimizarse; los recuentos de visitantes MUST agregarse siempre que sea posible y no se almacenan
ubicaciones individuales cuando no sea necesario. Se prohíben soluciones intrusivas por defecto
(reconocimiento facial, seguimiento individual persistente).

Rationale: reducir la presión turística no justifica vigilancia indiscriminada ni exposición de
credenciales.

### IX. Simplicidad, contratos explícitos y rechazo de complejidad injustificada

La arquitectura MUST permanecer simple y modular, con límites claros entre capas y contratos de
API explícitos. No se incorporan dependencias, servicios gestionados ni patrones complejos
(Redis, PostGIS, colas, edge) sin un requisito documentado y verificado. Las decisiones
arquitectónicas relevantes se registran como ADR.

Rationale: la deuda actual proviene en parte de sumar herramientas sin justificar; el coste de
operar y mantener crece más rápido que el valor.

## Restricciones de Producto y Alcance

- **Alcance geográfico inicial: Mallorca (Illes Balears).** Cualquier expansión territorial exige
  una especificación y una decisión explícita.
- **Capacidad de acogida**: no se inventan cifras. Cuando no exista una capacidad de referencia
  defendible, el sistema MUST reconocer la incertidumbre y usar, si acaso, indicadores de presión
  relativa etiquetados como tales.
- **Sin medición universal de visitantes**, sin modelo de machine learning, sin autenticación, sin
  notificaciones, sin multi-región y sin migración de plataforma en el alcance del MVP actual.
- **Recursos y fuentes**: solo se integran fuentes legítimas, con condiciones de uso revisadas.
  Si una fuente requiere evaluación jurídica, técnica o de privacidad, se documenta antes de
  integrarla.

## Flujo de Trabajo y Puertas de Calidad

- Constitución: se establece una vez y se revisa cuando cambian los principios estructurales.
  Cada funcionalidad relevante sigue su propio ciclo SDD.
- Antes de implementar: especificación con criterios de aceptación; antes de cerrar: verificación
  de dichos criterios.
- Tests unitarios de reglas de dominio, tests de contrato de la API, pruebas de datos
  ausentes/inválidos/caducados, de exclusiones, de determinismo y de fallo de fuentes.
- Las excepciones a estos principios se registran como ADR con justificación y plan de reversión.
- Reglas operativas para agentes en `AGENTS.md`; visión y alcance en `docs/PRODUCT_VISION.md`.

## Governance

- Esta constitución prevalece sobre cualquier otra práctica del repositorio. Las especificaciones
  y los planes MUST ser coherentes con ella; `/speckit.analyze` y `/speckit.converge` verifican
  esa coherencia.
- **Enmiendas**: requieren justificación escrita, revisión y registro. Un cambio MAJOR elimina o
  redefine principios; MINOR añade o expande; PATCH aclara sin cambiar el significado.
- **Versionado**: semántico (`MAJOR.MINOR.PATCH`), con fecha de ratificación y de última enmienda
  en formato ISO `YYYY-MM-DD`.
- **Cumplimiento**: toda revisión debe comprobar la conformidad con los principios. Una violación
  no justificada bloquea la fusión; una justificada se documenta como ADR.

**Version**: 1.0.0 | **Ratified**: 2026-10-19 | **Last Amended**: 2026-10-19
