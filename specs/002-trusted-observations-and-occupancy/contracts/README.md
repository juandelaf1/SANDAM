# Contratos de la spec 002

**Estado**: propuesta. **No implementado.**

Estos ficheros describen el contrato **conceptual** de observaciones y los campos aditivos
que la spec 002 propone. No modifican ni sustituyen los contratos vigentes de la spec 001
(`specs/001-sustainable-beach-recommendation/contracts/`).

| Fichero | Qué define | Uso |
|---|---|---|
| `observation.schema.json` | JSON Schema (2020-12) de una observación con procedencia, método, tiempos, vigencia, validación y privacidad | Validar altas y tests de contrato del modelo |
| `donde-ir-observations.openapi.yaml` | Fragmento OpenAPI 3.1 con los esquemas **aditivos** (`DataQuality`, `PressureIndicator`, `RecommendationItemAdditions`, `SourceStatus`, `Prediction`) | Referencia para fusionar en el contrato de la API cuando se implemente |

## Reglas de compatibilidad

1. Los campos existentes **no se eliminan**.
2. Los campos nuevos son opcionales para el cliente.
3. `unknown` no se representa con `0` ni `false` en los campos nuevos.
4. Si un campo legado (`current_occupation`, `jellyfish_present`, `has_*`) mantiene un valor
   por compatibilidad, su estado (`occupancy_status`, `jellyfish_status`, `services_status`)
   tiene prioridad semántica y la documentación debe decirlo.
5. Los cambios incompatibles, si alguna vez fueran inevitables, requieren justificación
   documentada y un periodo de transición.

## Cómo validar el JSON Schema

Ejemplo con `jsonschema` (dependencia de desarrollo, no de producción):

```bash
python -c "import json,sys; from jsonschema import Draft202012Validator; \
schema=json.load(open('specs/002-trusted-observations-and-occupancy/contracts/observation.schema.json')); \
Draft202012Validator.check_schema(schema); print('schema ok')"
```

> Nota: `jsonschema` está disponible en el entorno verificado (2026-10-20) y el esquema pasa
> `Draft202012Validator.check_schema`; si se adopta en CI, debe declararse como dependencia de
> desarrollo. La validación del contrato se hará en la fase de implementación.
