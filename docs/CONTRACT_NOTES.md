# Notas de contrato y procedencia (borrador, SANDAM)

> Alineado con P1/P8 y `docs/PROVENANCE_CONVENTION.md` (raíz workspace). Complementa `docs/OPEN_QUESTIONS.md` y `docs/OPEN_QUESTIONS_PLAN.md`. Cualquier cambio funcional/API debe seguir `AGENTS.md` (SDD/spec, veracidad del dato, sin `random` en rutas reales).

## Contrato público (objetivo)
- **Versionado:** añadir `contract_version` (p.ej. `sandam-pressure/0.1`) y `procedencia` a respuestas de recomendación/estado cuando se formalice la API estable (OpenAPI en `/docs`).
- **Procedencia por valor:** distinguir `observado | estimado | prediccion | caducado | desconocido` (con `fuente`, `ts`, `confianza`/`validated` cuando aplique). *Nunca* presentar seed/simulado como observación.
- **Capacidad/ocupación:** mientras Q1/Q2 estén abiertas, no exponer umbrales de “capacidad oficial” ni “tiempo real” sin fuente; usar Modo B (indicador relativo) etiquetado o desactivar claim.
- **Acoplamiento (Poolar/GeoRisk/Parada Viva):** exponer señal de presión como capacidad consumible con procedencia; consumidores no reinterpretan.

## Backlog contrato
- [ ] Campo `procedencia`/`nature` homogéneo en schemas de respuesta.
- [ ] `contract_version` + `capabilities` en `/health` (manteniendo liveness).
- [ ] Tests que impidan afirmar capacidad/tiempo real sin procedencia/fuente (P1).
- [ ] Spec en `specs/` para cambios incompatibles.