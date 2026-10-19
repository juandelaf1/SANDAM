# SANDAM — Visión y alcance del producto

> **Documento canónico.** Esta es la fuente de verdad sobre *qué* es SANDAM y *para qué*.
> Los principios y la gobernanza están en [`.specify/memory/constitution.md`](../.specify/memory/constitution.md).
> Las reglas operativas para agentes, en [`AGENTS.md`](../AGENTS.md).

**Última revisión**: 2026-10-19

---

## 1. El problema

Mallorca recibe una presión turística elevada y muy concentrada. La concentración de visitantes en
pocas playas no se corresponde con la capacidad ecológica, física o de gestión de cada lugar.
Esto genera presión sobre ecosistemas sensibles, saturación de accesos y aparcamientos, residuos y
pérdida de calidad de la experiencia para visitantes y residentes.

Al mismo tiempo, muchas personas eligen playa sin información suficiente sobre ocupación actual,
condiciones marítimas, calidad del agua, restricciones de acceso o alternativas disponibles.
**SANDAM reduce esa asimetría de información.**

## 2. Qué construimos

Una plataforma de información y apoyo a la decisión que combina datos ambientales, presión de
visitantes, capacidad de acogida, movilidad y condiciones de uso para:

1. Detectar, estimar y visualizar la presión turística sobre las playas.
2. Identificar cuándo una playa se aproxima a niveles incompatibles con su capacidad o con una
   experiencia razonable.
3. Disuadir de forma transparente de acudir a lugares saturados o ambientalmente sensibles cuando
   existan alternativas adecuadas.
4. Proponer alternativas que equilibren conservación, seguridad, capacidad y necesidades del usuario.
5. **No trasladar el problema** a playas pequeñas, protegidas o mal preparadas.
6. Ayudar a decidir **antes** de desplazarse.
7. Aportar información útil también a residentes y gestores públicos.

## 3. Jerarquía de objetivos (prioridad)

1. **Protección ambiental y seguridad.**
2. **Reducción de la presión turística.**
3. **Calidad de la experiencia** (visitantes y residentes).
4. **Conveniencia individual.**

Las restricciones de seguridad o ambientales son **condiciones de exclusión** que ninguna ventaja de
comodidad puede compensar. Consecuencia de diseño: modelo de recomendación en **dos etapas**
(elegibilidad → comparación de alternativas elegibles), no una suma ponderada única.

## 4. Ámbito

- **Geográfico inicial: Mallorca (Illes Balears).** Ninguna expansión sin especificación y decisión
  explícita (ver [`adr/0001-ambito-mallorca.md`](adr/0001-ambito-mallorca.md)).
- **Sin** medición universal de visitantes, sin machine learning, sin autenticación, sin
  notificaciones, sin multi-región y sin migración de plataforma en el MVP actual.

## 5. Principios de producto no negociables (resumen)

El detalle vinculante está en la constitución. En corto:

- **No inventar información.** Cada dato se clasifica como observación, estimación, predicción,
  caducado o desconocido. La ausencia de datos no es una condición favorable.
- **No confundir poca afluencia con idoneidad ambiental.** Una cala vacía puede ser frágil.
- **Capacidad con fundamento.** Sin fuente defendible, la capacidad es desconocida.
- **Recomendar de forma transparente.** Explicar por qué se propone o se descarta, sin urgencia
  artificial.

## 6. Métrica de éxito

> El éxito **no** es que más personas visiten más playas. Es lograr que las decisiones de visita
> generen **menos presión ambiental y social**, sin trasladar el problema a otros lugares
> vulnerables.

Indicadores coherentes con ello: proporción de recomendaciones que evitan exclusiones; capacidad de
explicar cada decisión; ausencia de datos inventados; reproducibilidad del ranking.

## 7. Documentación relacionada

- Constitución (principios vinculantes): [`../.specify/memory/constitution.md`](../.specify/memory/constitution.md)
- Especificación 001 (recomendación sostenible): [`../specs/001-sustainable-beach-recommendation/spec.md`](../specs/001-sustainable-beach-recommendation/spec.md)
- Decisiones arquitectónicas: [`adr/`](adr/)
- Decisiones pendientes: [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md)

### Documentos históricos (no autoritativos)

Los siguientes documentos se conservan por su valor histórico pero **contradicen** el ámbito o el
estado real del sistema. **No deben usarse como fuente de verdad**:

- [`CONTEXTO_MAESTRO.md`](CONTEXTO_MAESTRO.md) — histórico (obsoleto).
- [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) — histórico (obsoleto).
