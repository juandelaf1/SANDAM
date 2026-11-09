# Plan de cierre — Open Questions (SANDAM) + viabilidad “producto real”

> Fecha: 2026-11-09. Contexto: SANDAM puede ser **autónomo vendible** (municipios/turismo/aforo-playas) y **acoplable a Poolar/GeoRisk** como señal de presión/observaciones **sin duplicar** (P2/P3). Núcleo técnico existe (FastAPI async, SQLAlchemy, scoring geo, spec-002 observaciones/procedencia en progreso), pero **no es operativo “tiempo real/real capacity” verificable** hasta cerrar Q1/Q2. Regla P1: nada se presenta como observado/real sin fuente+metodología; etiquetar `observado | estimado | sintético`.

## Principio de salida
- **Modo A (producto operativo real):** fuente verificable de aforo/capacidad + metodología → recomendaciones con procedencia `observado`/trazable.
- **Modo B (producto honesto interino):** solo **indicadores relativos/estimados** claramente etiquetados (`estimado`, sin umbrales de capacidad “oficial”); `max_capacity` del seed **no** se usa en recomendaciones. Útil para demo/piloto, no vendible como “aforo real”.

## Q1 — Metodología y fuentes de capacidad de acogida (bloquea FR-014/umbrales)
**Problema:** `max_capacity` seed es orientativo; sin metodología no hay umbral defendible.

| Opción | Procedencia | Esfuerzo/riesgo | Recomendación |
|---|---|---|---|
| 1. **Fuente oficial por playa** (planes de uso/gestión municipal, estudios de carga, ordenanzas, Protección Civil/costas) | `observado` (si documentado) | Alto (adquisición heterogénea) | **Objetivo a medio plazo** por municipios piloto; almacenar `fuente, fecha, metodologia, ambito (ecologica/fisica/acceso/servicios)`. |
| 2. **Solo presión relativa** (ranking/semaforo relativo entre playas, sin capacidad absoluta) | `estimado` (índice) | Medio | **Viable ya** como Modo B; renombrar campos/UI para que no impliquen “capacidad oficial”. |
| 3. **Proxy declarado** (superficie útil × densidad normativa) **solo si** se cita norma y se etiqueta | `estimado` (metodología explícita) | Medio | Solo con trazabilidad; nunca como “aforo real”. |

**Decisión necesaria (responsable producto):** elegir Modo A/B; si B, eliminar umbrales absolutos de recomendación y marcar todo como estimado. **Criterio de aceptación:** ningún endpoint/UI afirma capacidad real sin `fuente+metodologia` verificable.

## Q2 — Fuente de aforo/ocupación en tiempo real (bloquea US1 “tiempo real”)
| Opción | Procedencia | Esfuerzo/riesgo | Recomendación |
|---|---|---|---|
| 1. **Integración oficial** (sensores/contadores municipales, concesiones, aforo smart-city) | `observado` | Alto, depende de partners | Camino Modo A; contrato de datos + SLA + procedencia por observación. |
| 2. **Observaciones operativas validadas** (spec-002: reporte con validación/procedencia, no “sensor”) | `observado` (humano validado) / `estimado` | Medio | Alinear con spec-002; **no** etiquetar como aforo automático; mostrar confianza/fuente. |
| 3. **Señales proxy** (meteo, festivos, histórico, popularidad) → índice de presión | `estimado` | Bajo-medio | Modo B honesto; útil para ranking relativo, no para “ocupación real”. |
| 4. **Sin ocupación real** | — | Nulo | Desactivar/ocultar claims “tiempo real/ocupación”; producto = directorio + scoring estático declarado. |

**Criterio de aceptación:** “tiempo real” solo si hay fuente con latencia conocida; en caso contrario UI/API muestran `estimado` y método.

## Otras dependencias a alinear (resumen)
- **Pesos/umbrales de scoring:** documentar como configuración versionada; si dependen de Q1/Q2, operar en Modo B relativo.
- **Procedencia (spec-002):** persistir `fuente, ts, tipo_observacion, confianza, observado|estimado` en respuestas/medallion.
- **Contrato de acoplamiento (P8):** exponer señal de presión con `contract_version` + `procedencia`; consumidores (Poolar/GeoRisk) no reinterpretan como “aforo oficial”.

## Pasos ejecutables (propuestos)
1. **Decisión producto (ahora):** Modo A (piloto con fuente) o Modo B (indicador relativo). Registrar en `DECISION_LOG.md` (D9).
2. **Hardening honesto (código/docs, bajo riesgo):** asegurar que respuestas/modelos no afirmen capacidad/tiempo real sin procedencia; `max_capacity` seed marcado no-recomendación; añadir `procedencia/contract_version` al contrato público.
3. **Si Modo B:** implementar/validar índice relativo + etiquetado + OpenAPI; preparar demo.
4. **Si Modo A:** identificar **1 municipio/playa piloto** + fuente de datos (Q1/Q2), firmar/acordar acceso, ingesta bronze→silver→gold con procedencia.
5. **Calidad/CI:** tests sobre reglas de procedencia (no filtrar “capacidad real” cuando no hay fuente).

## Definición de “producto real” para SANDAM
- Modo A: recomendaciones trazables a fuente verificable + métricas validadas.
- Modo B: producto de apoyo a decisión con **transparencia total** (estimado/relativo) — vendible solo como tal, no como medición oficial.
