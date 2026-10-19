# ADR 0001 — Ámbito geográfico inicial: Mallorca

- **Estado**: Aceptada
- **Fecha**: 2026-10-19
- **Decisores**: propietario del producto

## Contexto

La documentación del repositorio es contradictoria: `docs/PROJECT_CONTEXT.md` describe Cataluña
(con ejemplos de la Barceloneta y `region: Cataluña/Valencia/Andalucía`), mientras que
`docs/CONTEXTO_MAESTRO.md`, `seed_data.py` y el README describen Mallorca (20 playas con
coordenadas reales). Esta contradicción afecta al alcance del MVP (qué datos, qué fuentes, qué
reglas y qué se documenta como válido).

## Alternativas

1. **Mallorca** — datos ya presentes (seed, AEMET en Mallorca, SOCIB/CAIB), visión coherente.
2. **Cataluña** — mencionada solo en documentación antigua; sin datos reales en el repo.
3. **Todas las Baleares / multi-región** — mayor alcance; sin datos ni fuentes preparadas.

## Decisión

El ámbito inicial es **Mallorca (Illes Balears)**. La región canónica es `"Mallorca"`. Cualquier
expansión territorial requiere una especificación y una decisión explícita.

## Justificación

Es el único ámbito con datos reales en el repositorio y coherente con la visión de producto. La
documentación de Cataluña es un residuo de una versión anterior y no corresponde al sistema real.

## Consecuencias

- Se marca `docs/PROJECT_CONTEXT.md` y `docs/CONTEXTO_MAESTRO.md` como **históricos (obsoletos)**.
- `docs/API_GUIDE.md` se alinea a Mallorca.
- Los endpoints y el seed operan sobre Mallorca; no se añaden regiones peninsulares.
- La fuente canónica de visión pasa a ser `docs/PRODUCT_VISION.md`.
