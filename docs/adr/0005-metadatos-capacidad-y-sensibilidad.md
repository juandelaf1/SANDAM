# ADR 0005 — Metadatos documentados de capacidad y sensibilidad de la playa

- **Estado**: Aceptada
- **Fecha**: 2026-10-19
- **Decisores**: propietario del producto

## Contexto

La tarea **T004** incorpora a `beaches` cinco campos de metadatos documentados:

`protection_status`, `access_restrictions`, `capacity_reference`, `capacity_method`,
`vulnerability_level`.

Tres cuestiones no estaban cerradas por los artefactos previos:

1. **Tipos.** `data-model.md` proponía `String/Enum`, `Text/JSON`, `Integer` y `String/Enum`.
   El uso de `ENUM` nativo de PostgreSQL o de `JSON/JSONB` ataría el esquema a un motor y
   complicaría las migraciones y los tests (que corren sobre SQLite).
2. **Semántica de `capacity_reference`.** El brief de T004 lo describe como el campo que permite
   **identificar la referencia o procedencia** de la información de capacidad, mientras que
   `data-model.md` lo tipaba como `Integer` ("capacidad de referencia"). Son dos lecturas
   incompatibles: un identificador de procedencia no es un número.
3. **Regla `capacity_reference ⇒ capacity_method`.** "`capacity_reference` sin `capacity_method`
   es inválido" debe aplicarse en algún punto verificable.

Además, la constitución (Principios II/III) y ADR 0002 exigen que la ausencia de un dato se
propague como **desconocido**, nunca como un valor favorable.

Restricción de la tarea: la migración `0002` **no** puede reconstruir la tabla `beaches`.

## Alternativas

1. **Tipos nativos / enriquecidos**: `ENUM` de PostgreSQL para `protection_status` y
   `vulnerability_level`, `JSONB` para `access_restrictions`.
   *Descartada*: no existen catálogos de valores validados que justifiquen un `ENUM` (inventarlos
   iría contra la veracidad del dato) y `JSON/JSONB` añade dependencia de motor y complejidad no
   exigida por T004.
2. **`capacity_reference` como `Integer`** (lectura literal de `data-model.md`).
   *Descartada*: un entero no puede "identificar la referencia o procedencia"; además ya existe
   `max_capacity` (Integer) para la cifra, y una cifra de capacidad suelta se confundiría con una
   capacidad oficial validada, que es exactamente lo que FR-014 prohíbe. La cifra no debe
   confundirse con su fuente.
3. **`CHECK` de base de datos** para la regla `capacity_reference ⇒ capacity_method`.
   *Descartada*: SQLite no admite `ALTER TABLE ... ADD CONSTRAINT` (habría que reconstruir la
   tabla, prohibido por T004) y una columna referenciada por un `CHECK` tampoco se puede eliminar
   sin reconstruir. Sería una dependencia de PostgreSQL en la migración.
4. **Invariante del modelo (ORM)** para la regla, en el *flush*.
   *Elegida*: independiente del motor, cubre altas y actualizaciones parciales sin reconstruir
   tablas.

## Decisión

- Los cinco campos se añaden como columnas **anulables**, con tipos SQL portables:
  `protection_status VARCHAR(100)`, `access_restrictions TEXT`,
  `capacity_reference VARCHAR(255)`, `capacity_method VARCHAR(255)`,
  `vulnerability_level VARCHAR(50)`.
- **`NULL` significa "desconocido / no documentado"**. No se define ningún valor por defecto
  (ni de servidor ni de cliente): la ausencia de información no afirma que la playa no esté
  protegida, no tenga restricciones o presente riesgo bajo (ADR 0002, FR-003/FR-014).
- **`capacity_reference` es un identificador textual** de la referencia/fuente que respalda la
  información de capacidad; la cifra, si existe, vive en `max_capacity`. Se mantiene la regla:
  sin `capacity_method` no se admite `capacity_reference`.
- La regla se aplica como **invariante del modelo** en `src/models.py`
  (`before_flush` sobre `Session`, excepción `CapacityProvenanceError`), no como `CHECK` de BD.
- No se introducen `ENUM` nativos, `JSON`/`JSONB` ni defaults de servidor.
- Los campos **no** se exponen todavía en los esquemas Pydantic ni en la API: T004 es modelo +
  migración. Exponerlos se decidirá junto con la elegibilidad y la trazabilidad (T005+), sin
  presentarlos nunca como datos en tiempo real.

## Justificación

- Los tipos portables permiten aplicar la misma migración en PostgreSQL (producción) y SQLite
  (tests) sin ramas por motor y sin reconstruir tablas.
- Representar la procedencia como texto evita que un número sin fuente se interprete como
  capacidad validada (FR-014) y hace explícito el estado desconocido con `NULL`.
- El invariante en el *flush* es el único punto que valida correctamente tanto la creación como
  las actualizaciones parciales sin recurrir a un `CHECK` (que exigiría reconstruir la tabla).
- No inventar catálogos de protección/vulnerabilidad mantiene la coherencia con
  `docs/OPEN_QUESTIONS.md` (metodología de capacidad pendiente): el estado sigue siendo
  desconocido hasta que exista una clasificación defendible.

## Consecuencias

- `data-model.md` de la spec 001 se actualiza: `capacity_reference` pasa de `Integer` a texto
  (identificador de procedencia) y se documentan los centinelas `NULL`.
- La migración `0002_metadata_fields.py` solo hace `ALTER TABLE ... ADD COLUMN` de las cinco
  columnas; su `downgrade` las elimina y no toca el resto del esquema.
- **Limitación asumida**: la regla `capacity_reference ⇒ capacity_method` se garantiza para
  escrituras a través del ORM (el camino de la aplicación). Una escritura por SQL crudo podría
  saltársela. Si en el futuro se exige garantía a nivel de BD, la vía sería una migración con
  `batch_alter_table` (reconstruye la tabla en SQLite) o un `CHECK` solo para PostgreSQL; ninguna
  de las dos se adopta en T004.
- Requiere migración → cubierta por el procedimiento de ADR 0003 y `docs/MIGRATIONS.md`.

## Plan de reversión

`alembic downgrade -1` elimina las cinco columnas (revisión `0002 → 0001`). Como los campos son
nuevos y anulables, la reversión no pierde información preexistente; solo se pierde lo que se
hubiera escrito en ellos.
