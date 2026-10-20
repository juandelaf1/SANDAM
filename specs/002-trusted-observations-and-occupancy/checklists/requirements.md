# Requirements Quality Checklist: Observaciones fiables, procedencia y presión turística

**Purpose**: revisión de la **calidad de los requisitos** de la spec 002 (claridad, cobertura,
testabilidad, no invención), no del trabajo de implementación.
**Created**: 2026-10-20
**Feature**: [spec.md](./spec.md) · [plan.md](./plan.md) · [research.md](./research.md) · [data-model.md](./data-model.md)

**Note**: checklist generado a mano siguiendo el formato de `.specify/templates/checklist-template.md`.
**Review Ownership**: artefacto de revisión del responsable de requisitos. Marcar `[x]` solo
cuando el criterio de calidad esté satisfecho.
**Marker Semantics**: `[x]` = criterio revisado y satisfecho para la calidad del requisito. No
significa que la implementación esté hecha.

## Claridad y ausencia de ambigüedad

- [ ] CHK001 La distinción entre `nature`, `validation_status` y `status` está definida sin ambigüedad (FR-002/FR-003)
- [ ] CHK002 “Desconocido” tiene una definición única y no se usa como sinónimo de “sin riesgo” (FR-005/FR-006)
- [ ] CHK003 Cada requisito usa términos con una sola lectura posible (MUST/MUST NOT)
- [ ] CHK004 El alcance de “no implementado en esta fase” está explícito y es verificable

## Cobertura y completitud

- [ ] CHK005 Hay requisito para cada caso de la cadena de defaults (ocupación, medusas, sargazo, servicios, data_status)
- [ ] CHK006 Se cubre la ausencia confirmada frente a la desconocida (FR-006)
- [ ] CHK007 Se cubre la degradación ante fallo de fuente sin invención (FR-012)
- [ ] CHK008 Se cubre la contradicción entre fuentes con política explícita (FR-013)
- [ ] CHK009 Se cubre la licencia/condiciones de uso como condición previa (FR-015)
- [ ] CHK010 Se cubre la privacidad y la no identificación individual (FR-016)
- [ ] CHK011 Se cubre la migración y la clasificación de registros existentes (FR-017)
- [ ] CHK012 Se cubre la trazabilidad de cada valor usado (FR-018)
- [ ] CHK013 Se cubre el uso de “tiempo real” con umbral verificable (FR-020)
- [ ] CHK014 Se cubre la validación de heurísticos y la ausencia de confianza sin validar (FR-010)

## Testabilidad y criterios de éxito

- [ ] CHK015 Cada SC es medible (porcentaje, existencia o resultado binario)
- [ ] CHK016 Los escenarios de `quickstart.md` permiten verificar cada SC
- [ ] CHK017 Existe una prueba prevista para “ocupación desconocida ≠ 0 %”
- [ ] CHK018 Existe una prueba prevista para “seed ≠ live”
- [ ] CHK019 Existe una prueba prevista de contrato y compatibilidad

## No invención y veracidad

- [ ] CHK020 Ninguna fuente se declara accesible/licenciada sin evidencia registrada
- [ ] CHK021 Los huecos de información se marcan como “no verificado” en la investigación
- [ ] CHK022 Los datos de referencia para validar heurísticos están identificados y requieren permiso
- [ ] CHK023 No se fijan umbrales numéricos de exactitud sin base o decisión de producto
- [ ] CHK024 No se presenta la presión relativa como capacidad oficial (FR-007/FR-014 de la spec 001)

## Alcance y límites

- [ ] CHK025 Se mantienen los pesos del scoring y la ocupación fuera del score
- [ ] CHK026 Se excluyen explícitamente los proveedores de rutas y el machine learning
- [ ] CHK027 Se declara que no se implementa migración, tabla ni integración en esta fase
- [ ] CHK028 Se respeta la compatibilidad de contrato o se documenta la excepción

## Trazabilidad

- [ ] CHK029 Cada FR es rastreable a un escenario o a un criterio de éxito
- [ ] CHK030 Las brechas de la spec 001 (`convergence-audit.md`) quedan cubiertas o declaradas fuera de alcance
- [ ] CHK031 Las decisiones de investigación (D1–D8) son coherentes con `spec.md` y `plan.md`
- [ ] CHK032 Las preguntas abiertas están registradas en `docs/OPEN_QUESTIONS.md`

## Notes

- Marcar `[x]` solo tras revisión; dejar sin marcar lo que requiera aclaración.
- `/speckit.implement` leerá estos marcadores como puerta y no debe modificarlos.
- Hallazgos pendientes de decisión de producto: umbral de “tiempo real”, margen de mejora
  frente a la línea base de validación y política de `null` en campos legados.
