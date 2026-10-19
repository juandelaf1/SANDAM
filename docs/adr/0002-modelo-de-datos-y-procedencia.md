# ADR 0002 — Separación de datos observados, estimaciones y predicciones

- **Estado**: Aceptada
- **Fecha**: 2026-10-19
- **Decisores**: propietario del producto

## Contexto

Hoy el modelo `Beach` mezcla datos de naturaleza distinta en una sola fila: valores del `seed`
estático, valores potencialmente reales (p. ej. de AEMET) y predicciones. Existe `data_status`
(`live`/`estimated`/`unavailable`) y `last_updated`, pero `data_status` **no se usa** en la lógica
de recomendación, y no hay campo de **fuente** ni de **hora de observación** separada de la de
obtención. Además, `src/utils/predictions.py` genera datos con `random` que se exponen como
predicciones reales.

## Alternativas

1. **Envoltura de calidad solo en la respuesta** (sin cambiar el modelo) — rápido, pero no
   persistente ni auditable.
2. **Entidades separadas** (`Observation`, `Prediction`) con metadatos — trazable y auditable, pero
   requiere migración.
3. **Ignorar la distinción** — incumple el Principio II de la constitución. Descartada.

## Decisión

Separar los conceptos en el modelo de datos (ver `data-model.md` de la spec 001): datos estáticos de
la playa, `Observation` (fuente + `observed_at` + `fetched_at` + validez + estado), `Prediction`
(horizonte + método + entradas) e indicadores derivados (presión **relativa**). Toda respuesta
etiqueta cada valor como observación / estimación / predicción / caducado / desconocido.

## Justificación

Es requisito de los Principios II (veracidad, trazabilidad y separación) y III, y condición para
cumplir SC-002/SC-003 de la spec 001. Sin esto, la recomendación no puede distinguir lo que sabe de
lo que no.

## Consecuencias

- Requiere migración (ver ADR 0003).
- Se prohíbe `random` en rutas que devuelvan datos que parezcan reales.
- La ausencia de un dato se propaga como "desconocido", nunca como favorable.
- Las predicciones deben declarar método y horizonte; si no, se etiquetan como estimación o se
  retiran.
