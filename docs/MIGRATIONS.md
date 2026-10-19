# Migraciones de base de datos (Alembic)

> **Regla**: el esquema lo posee **Alembic**. La aplicación **no** crea ni altera tablas al
> arrancar (`create_all()` se ha retirado del arranque). Aplicar migraciones es siempre un paso
> **explícito y documentado** antes de desplegar código que las requiera.

- Configuración: [`alembic.ini`](../alembic.ini) y [`alembic/env.py`](../alembic/env.py).
- Revisiones: [`alembic/versions/`](../alembic/versions/).
- Decisión registrada: [ADR 0003](adr/0003-migraciones-alembic.md).

La URL de conexión se lee de `DATABASE_URL` (o `.env`) a través de `src/config.py`. **No** se
versiona ninguna credencial y la URL **no** se imprime en logs.

---

## 1. Aplicar migraciones (uso habitual)

Desde la raíz del repositorio, con el entorno y la configuración cargados:

```bash
alembic current        # revisión aplicada actualmente
alembic upgrade head   # aplica todas las migraciones pendientes
alembic history        # historial de revisiones
alembic downgrade -1   # revierte la última revisión (ver §5)
```

## 2. Base de datos **nueva**

1. Crear la base de datos (p. ej. con `docker compose up -d postgres`).
2. Configurar `DATABASE_URL` (ver `.env.example`).
3. Aplicar el esquema:

   ```bash
   alembic upgrade head
   ```

4. (Opcional, datos de ejemplo) `python seed_data.py` — ahora **exige** que el esquema exista y
   falla con un mensaje claro si no se han aplicado las migraciones.

Con `docker compose`, tras `docker compose up --build -d`:

```bash
docker compose exec api alembic upgrade head
docker compose exec api python seed_data.py
```

## 3. Base de datos **existente** (creada antes de Alembic con `create_all()`)

Una base de datos que ya tiene la tabla `beaches` **no** debe recibir `alembic upgrade head` a
ciegas: la revisión `0001` intentaría **crear** una tabla que ya existe y fallaría.

Procedimiento seguro:

1. **Comprobar equivalencia**, sin modificar la base existente. Comparar su esquema real
   (tablas, columnas, nulabilidad, índices) con el que produce la revisión `0001` en una base
   limpia y desechable:

   ```bash
   # base limpia y desechable que representa la revisión inicial
   DATABASE_URL="sqlite+aiosqlite:///./_schema_from_migration.db" alembic upgrade head
   ```

   Y comparar con el esquema real de la base existente.

   > **Aviso**: `alembic check` **no** sirve para esta comparación previa. Exige que la base esté
   > marcada como al día y responde `Target database is not up to date` mientras no exista
   > `alembic_version`. Compara los esquemas directamente (catálogo del motor) antes de decidir.

2. **Si los esquemas son equivalentes** → marcar la base como ya migrada, sin recrear tablas:

   ```bash
   alembic stamp head
   ```

3. **Si NO son equivalentes** → **no** usar `alembic stamp`. Diferencias posibles: la base tiene
   columnas/índices de más, de menos, o de otro tipo. En ese caso hay que:
   - escribir una migración que lleve esa base desde su estado real hasta el esperado, o
   - migrar los datos manualmente a una base nueva creada con `alembic upgrade head`.

   `alembic stamp` **no** debe usarse para ocultar diferencias entre modelos, migración y base de
   datos.

## 4. Despliegue

Orden correcto, siempre:

1. Aplicar migraciones (`alembic upgrade head`) contra la base del entorno.
2. Verificar (`alembic current`).
3. Desplegar el código nuevo.

La aplicación **nunca** ejecuta migraciones en el arranque de FastAPI. Si la base no tiene el
esquema esperado, la API arranca en modo degradado (`/health` responde; `/health/ready` informa
`ready: false`).

## 5. Reversión (rollback)

Cada revisión implementa `downgrade` de forma simétrica a `upgrade`.

```bash
alembic downgrade -1    # una revisión atrás
alembic downgrade base  # deshace todas las revisiones
```

> `alembic downgrade base` sobre la revisión `0001` **elimina la tabla `beaches` y sus datos**.
> Es una operación destructiva: úsala solo en entornos de prueba o con copia de seguridad.

## 6. Verificación

- El esquema creado por `alembic upgrade head` debe coincidir con el declarado en `src/models.py`.
- `alembic downgrade base` debe dejar la base vacía de objetos de la revisión.
- Automatizar esta comparación en CI es la tarea **T028** del plan; todavía pendiente.

### Estado de verificación (2026-10-19)

Comprobado contra **PostgreSQL 16.13** real, en una base dedicada y desechable
(`sandam_t003_test`, eliminada tras las pruebas):

- `alembic upgrade head` → revisión `0001 (head)`; tabla `beaches` con 30 columnas y tipos nativos
  (`uuid`, `varchar`, `double precision`, `boolean`, `timestamp without time zone`), PK
  `beaches_pkey`, índice único `ix_beaches_name` y 4 índices; sin claves foráneas.
- `alembic check` → *No new upgrade operations detected*.
- `alembic downgrade base` → elimina `beaches`; el `upgrade head` posterior la restaura.
- Adopción de esquema existente: `create_all` → `alembic stamp head` → `upgrade head` no-op.
  (Una divergencia introducida a propósito —columna de más— **sí** es detectada por `alembic check`.)
- FastAPI arranca contra la base migrada: `/health/ready` → `ready: true` y consulta ORM correcta,
  sin crear ni alterar el esquema desde el ciclo de vida de la aplicación.

## 7. Crear una nueva migración

```bash
alembic revision --autogenerate -m "descripcion corta"
```

**Revisar siempre** el archivo generado: el autogenerate puede omitir o proponer cambios
indeseados (tipos específicos de PostgreSQL, renombrados, `server_default`, etc.). Ajustar a mano
si es necesario y comprobar `upgrade`/`downgrade`.
