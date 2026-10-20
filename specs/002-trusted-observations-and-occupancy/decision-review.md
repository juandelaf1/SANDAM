# Revisión de decisiones previas a la implementación (Q29–Q34)

**Feature**: `002-trusted-observations-and-occupancy`
**Fecha**: 2026-10-20
**Estado**: análisis y preparación de decisiones. **No se ha implementado** la migración
`0003`, no se ha cambiado el esquema, no se han conectado fuentes y no se ha modificado el
scoring.
**Alcance**: revisar Q29–Q34 de `docs/OPEN_QUESTIONS.md` antes de escribir la primera
migración de la spec 002.

Este documento no cierra preguntas por sí solo. Distingue:

- **hechos verificados** en el repositorio;
- **inferencias** que el código permite hacer;
- **decisiones que requieren aprobación expresa** del propietario;
- **preguntas que pueden seguir abiertas** sin bloquear el modelo genérico.

---

## 1. Estado inicial verificado

| Elemento | Estado comprobado |
|---|---|
| Rama | `sdd-adoption` |
| `HEAD` | `644e011` — `docs(spec-002): definir observaciones fiables, procedencia y presion turistica` |
| Commits recientes | `6d72b7f`, `644e011` (y anteriores de la spec 001) |
| Remoto | `origin` = `https://github.com/juandelaf1/SANDAM.git` |
| Upstream de la rama | **No configurado**; la rama no se ha publicado |
| Árbol versionado | Limpio |
| Archivos sin seguimiento | **38**, preservados; no se han tocado |
| Migraciones | Solo `0001_initial.py` y `0002_metadata_fields.py`; **no existe `0003`** |
| Base de datos local | Intento de lectura agregada: `ConnectionRefusedError`; **no se pudo consultar** |
| Base de datos de producción | **No consultada**; no se afirma nada sobre sus filas |
| SOCIB | Q5: credencial en el historial, tratada como comprometida; **no se ha impreso ni verificado su valor**; no hay evidencia de rotación |
| Fuentes externas | No se ejecutaron scrapers ni adaptadores; no se usaron credenciales en esta fase |
| Documentos revisados | `AGENTS.md`, constitución, spec 002, `research.md`, `data-model.md`, `plan.md`, `tasks.md`, contratos y `OPEN_QUESTIONS.md` |

**Limitación importante**: al no poder leer la base local, las conclusiones sobre “qué
registros existen” se basan en el código, las migraciones, el seed y los tests. No se
extrapolan a producción. Cualquier recuento real exige ejecutar la auditoría de solo lectura
en un entorno autorizado.

---

## 2. Q29 — Unidad y base de ocupación

### 2.1 Evidencia disponible

| Evidencia | Ubicación | Qué demuestra | Qué **no** demuestra |
|---|---|---|---|
| Columna `current_occupation` entera y anulable en la migración inicial | `alembic/versions/0001_initial.py:41` | El esquema admite enteros y `NULL` | No define unidad, denominador ni superficie |
| `Column(Integer, default=0)` | `src/models.py:71` | El ORM rellena `0` si no se indica valor | El `0` no es una observación; es un default de Python |
| `current_occupation: int = Field(default=0, ge=0, le=100)` | `src/schemas.py:15` | La API acepta solo enteros entre 0 y 100 | No demuestra que sea un porcentaje |
| Filtros `occupation_min`/`occupation_max` entre 0 y 100 | `src/api/beaches.py:32-33`; `src/crud.py:51-54` | El filtro está construido sobre la escala 0–100 | No define qué significa el número |
| `relative_pressure` divide por 100 y recorta a `[0, 1]` | `src/utils/scoring.py:169-179` | El código **interpreta** el valor como porcentaje | No hay fuente ni base documentada que lo respalde |
| Seed: 20 pares `max_capacity`/`current_occupation` | `seed_data.py:11-514` | Valores de ocupación entre **20 y 92**, media 54,5; capacidades entre **1.500 y 20.000** | No son observaciones; son literales de demostración |
| Si se interpretara como porcentaje, el seed implicaría entre 300 y 14.400 personas | Cálculo sobre el seed | La magnitud es plausible como porcentaje de capacidad | No prueba que el denominador sea el `max_capacity` del seed |
| Documentación de API: “Ocupación mínima/máxima (%)” | `docs/API_GUIDE.md:113-114` | La documentación actual la presenta como porcentaje | Es documentación interna, no una ficha de fuente |
| `PROJECT_CONTEXT.md`: “occupation (0-100%)” | `docs/PROJECT_CONTEXT.md:41` | Refuerza la convención de porcentaje | No define la superficie de referencia |
| `CONTEXTO_MAESTRO.md`: “Ocupación real - No %, sino m² disponibles” | `docs/CONTEXTO_MAESTRO.md:64` | Existe una contradicción de producto: se pide otra magnitud | No hay implementación de m² ni capacidad física validada |
| `CONTEXTO_MAESTRO.md` también usa “% espacio libre” en el scoring | `docs/CONTEXTO_MAESTRO.md:126` | La propia documentación mezcla porcentaje y superficie | No resuelve la semántica |
| Scrapers extraen el primer entero y usan `0` o `50` por defecto | `src/integrations/scraper.py:204-209, 436-442`; `src/integrations/scraper_scrapling.py:61-67`; `src/integrations/real_data_client.py:90-91` | Los importadores no capturan unidad ni fuente; pueden guardar un número sin significado | No se ejecutaron; no se sabe qué publica realmente cada página |
| No hay tabla de observaciones ni campo de unidad | `src/models.py`; migraciones 0001/0002 | La procedencia y la unidad no están modeladas | — |
| Base local inaccesible | Intento de lectura de esta sesión | No hay recuento real | No se puede afirmar cuántas filas tienen `0`, `NULL` o valores reales |

### 2.2 Conclusión defendible

1. **La escala 0–100 está implantada** en la API, los filtros y la presión relativa.
2. **El código y la documentación la interpretan como porcentaje**, pero esa interpretación
   es una convención interna, no una medición verificada.
3. **No hay evidencia de la superficie de referencia**: no se sabe si el denominador es la
   arena, el dominio público, la capacidad total, un aforo municipal o una capacidad
   inventada.
4. **No hay evidencia de que sea un conteo de personas**. Los scrapers podrían estar
   capturando tanto un porcentaje como un número absoluto; no se ejecutaron.
5. **`max_capacity` del seed no es una capacidad oficial** (Q1). Aunque la ocupación fuera un
   porcentaje, el denominador seguiría sin estar validado.
6. Por tanto, **no se puede adoptar “porcentaje” como unidad canónica** ni calcular una
   `pressure_relative` defendible con los datos actuales.

> La afirmación “es un porcentaje” no se deduce de que un consumidor lo muestre con `%`.
> Lo único que se deduce es que el consumidor **asume** esa convención.

### 2.3 Alternativas evaluadas

| Alternativa | Contrato de API | Base de datos | Filtros | Presión relativa | Compatibilidad |
|---|---|---|---|---|---|
| **A. Campo legado opaco + observación nueva con unidad y referencia** | `current_occupation` se conserva; se añade `occupancy`/`occupancy_status` con `unit` y `reference_type` | Se añaden columnas de referencia en `observations`; no se reinterpreta el campo legado | Los filtros solo se aplican a observaciones con unidad/referencia; el desconocido se declara, no se trata como 0 | Solo si hay unidad `%` y referencia explícita; si no, `null` | Aditiva; la más segura |
| **B. Estandarizar “porcentaje de capacidad oficial”** | `current_occupation` sigue siendo `%`; se documenta el denominador | Requiere capacidad oficial por playa y metodología | Comparables entre playas solo si la capacidad es homogénea | Posible, pero solo con capacidad validada | Rompe la semántica si no hay capacidad oficial; Q1 sigue abierta |
| **C. Estandarizar conteo de personas + capacidad** | Nuevo `occupancy_count` y `capacity_reference`; el porcentaje se deriva | Requiere conteo y capacidad; el campo legado no se puede reinterpretar | Los filtros actuales (0–100) dejan de ser válidos | Posible con capacidad validada; si no, `null` | Cambio incompatible para clientes que lean `current_occupation` como 0–100 |
| **D. Índice sin unidad** | Se mantiene un número 0–100 sin unidad | No requiere cambios | Se mantiene, pero no es comparable ni interpretable | **No** debe emitirse | Parece compatible, pero perpetúa la ambigüedad; descartada |

### 2.4 Recomendación

**Alternativa A, con una decisión canónica aplazada.**

- Mantener `current_occupation` como **campo legado** durante la transición. No borrarlo, no
  reinterpretarlo y **no escribir en él nuevas observaciones** mientras Q29 no esté resuelta.
- Añadir al contrato de observación:
  - `unit`: `%`, `count`, u otra unidad declarada;
  - `reference_type`: `sand_area`, `total_area`, `official_capacity`, `unknown`;
  - `reference_value` y `reference_unit` (por ejemplo, `m2` o `people`);
  - `reference_source_id` y `reference_is_validated` (booleano, `false` por defecto).
- Exponer `occupancy_status` (`observed`, `estimated`, `stale`, `unknown`, `synthetic`) y,
  cuando exista, `occupancy.unit`/`occupancy.reference_type`.
- **No emitir `pressure_relative`** si:
  - la ocupación es desconocida;
  - la unidad no está declarada;
  - la referencia es `unknown`;
  - el valor es un conteo sin capacidad validada.
- Si se emite, etiquetarla como **presión relativa**, nunca como capacidad oficial ni límite
  ecológico.
- Los filtros `occupation_min`/`occupation_max` **no deben comparar el desconocido como 0**.
  Deben aplicar solo a valores con unidad/referencia compatibles y declarar cuántos registros
  quedaron fuera por no poder evaluarse. Ese metadato es aditivo y requiere decisión de
  contrato.

**Decisión que sigue pendiente**: si el propietario quiere una unidad canónica única
(`%` o `count`) y qué superficie/capacidad la respalda. Hasta entonces, el modelo puede
soportar ambas, pero no debe producir una comparación numérica entre playas.

### 2.5 Incertidumbres que no se resuelven con el código

- ¿El `0` del seed significa “vacía” o “sin dato”? El código no lo distingue.
- ¿El denominador es la arena o el total? Calvià publica aforo de la zona de arena; el
  Consell y el Gemelo Digital no detallan la base.
- ¿La cifra es una estimación por cámaras, un conteo de socorristas o un aforo municipal?
  Depende de la fuente y no está registrado.
- ¿Los valores del seed son realistas? No son observaciones; no se usan como evidencia.

### 2.6 Pruebas de contrato propuestas

1. `current_occupation = 0` + `occupancy_status = "unknown"` no produce `pressure_relative`
   ni “0 %” ni “playa tranquila”.
2. Observación numérica sin `unit` → rechazada o no utilizable para decisiones.
3. Observación con `unit = "%"` y `reference_type = "unknown"` → `pressure_relative = null`.
4. Observación con `unit = "count"` y sin capacidad validada → `pressure_relative = null`.
5. Observación con `unit = "%"` y referencia explícita → presión calculada y etiquetada como
   relativa, con `reference_is_validated` visible.
6. Filtro `occupation_max=50` con una playa desconocida: no se compara como 0; la respuesta
   declara el efecto del filtro (incluida o excluida, pero no silenciosa).
7. El campo legado `current_occupation` sigue serializándose como entero en la fase de
   transición; un cliente antiguo no recibe un `NULL` inesperado.
8. Prueba de contrato sobre `/beaches`, `/donde-ir`, `/search` y `/external` para verificar que
   el estado nuevo es aditivo y que ningún texto afirma ocupación desconocida como 0 %.

---

## 3. Q34 — Valores heredados y datos desconocidos

### 3.1 Defaults actuales

| Campo | Default del modelo | Esquema Pydantic | Nulabilidad en BD | Seed | Efecto actual |
|---|---|---|---|---|---|
| `current_occupation` | `0` (`models.py:71`) | `int`, `0..100` (`schemas.py:15`) | `NULL` permitido (`0001:41`) | 20–92 | Un `0` se lee como “vacía”; `relative_pressure` da `0.0` |
| `jellyfish_present` | `False` (`models.py:82`) | `bool = False` (`schemas.py:26`) | `NULL` permitido (`0001:49`) | `False` | “✓ Sin medusas” sin observación |
| `sargasso_level` | `0` (`models.py:85`) | `int`, `0..3` (`schemas.py:28`) | `NULL` permitido (`0001:51`) | `0` | `0` se lee como “sin sargazo” |
| `posidonia_present` | `False` (`models.py:86`) | `bool = False` (`schemas.py:29`) | `NULL` permitido (`0001:52`) | `False` | `False` se lee como “sin posidonia” |
| `has_kiosk` … `has_lifeguard` | `False` (`models.py:92-97`) | `bool = False` (`schemas.py:35-40`) | `NULL` permitido (`0001:56-61`) | mezcla `True`/`False` | “Sin socorrista”, “sin parking”, etc. sin dato |
| `data_status` | `unavailable` (`models.py:111`) | `BeachCreate` usa `live` (`schemas.py:44`) | `NULL` permitido (`0001:62`) | el seed fuerza `live` (`seed_data.py:536`) | El seed y las altas se presentan como datos vivos |
| `flag_color` | `unknown` (`models.py:80`) | `unknown` (`schemas.py:24`) | `NULL` permitido | valores concretos | Correcto: `unknown` es explícito |
| `water_quality` | `unknown` (`models.py:88`) | `unknown` (`schemas.py:31`) | `NULL` permitido | valores concretos | El valor `unknown` existe, pero `data_quality` lo etiqueta como `observation` porque no es `None` |

**Hecho clave**: los defaults son de Python, no del servidor. La base admite `NULL` en todas
estas columnas, pero la aplicación nunca lo produce por defecto. Un `NULL` escrito por SQL
crudo o por una migración futura puede romper la serialización, porque `BeachResponse` hereda
`current_occupation: int` y los booleanos no opcionales de `BeachBase`.

### 3.2 Qué procedencia se puede demostrar

| Tipo de registro | ¿Se puede demostrar su origen? | Clasificación propuesta |
|---|---|---|
| Filas creadas por `seed_data.py` en una base vacía | **Sí, por el código del seed**, no por el valor de la fila | `synthetic` / `seed` |
| Filas existentes que “parecen” del seed | **No automáticamente**: pudieron editarse | Requieren auditoría; no se les inventa `seed` |
| Filas creadas por `POST /beaches` | **No**: `BeachCreate` no captura fuente ni método | `unknown` / `manual` |
| Filas actualizadas por `PUT /beaches` | **No** | `unknown` / `manual` |
| Filas creadas por scrapers/importadores | **No hay ninguna ruta versionada que las escriba**; si existe un proceso externo, no es verificable desde el repositorio | `unknown` o `imported`, solo con evidencia |
| Observaciones reales | **No existe tabla de observaciones** | No hay ninguna demostrable hoy |

**Conclusión**: en el código versionado **no hay ningún registro que pueda clasificarse como
observación real con procedencia demostrable**. El seed es el único conjunto identificable, y
es sintético. Todo lo demás es, como máximo, `unknown`/`manual` hasta que exista una fuente
registrada.

No se deben inventar `observed_at`, `source_id`, `method_id` ni `fetched_at` retrospectivos.

### 3.3 Alternativas de migración

| Alternativa | Ventaja | Inconveniente | Veredicto |
|---|---|---|---|
| **A. Conservar valores + añadir estado explícito** | No rompe clientes; no borra datos; permite distinguir | Exige que **todos** los consumidores lean el estado, no el valor bruto | **Recomendada para la transición** |
| **B. Poner `NULL` en los campos legados** | Semánticamente limpio | Rompe `int`/`bool` de Pydantic y clientes; no distingue un `0` real de un default; puede borrar información | **No aplicar en bloque** |
| **C. Estrategia por variable** | Respeta semánticas distintas | Más trabajo y más campos | **Recomendada como combinación con A** |

La alternativa B solo es viable después de:

- cambiar los esquemas de respuesta a opcionales;
- inventariar clientes;
- decidir una ventana de transición;
- tener una forma de no perder un `0` que fuera real.

### 3.4 Recomendación por variable

| Variable | Recomendación | Regla de lectura |
|---|---|---|
| `current_occupation` | Conservar el entero legado; añadir `occupancy_status`; **no escribir nuevas observaciones en el campo legado** mientras Q29 esté abierta | `0` solo es “vacía” si `occupancy_status = observed/estimated` y hay fuente; si no, es `unknown` |
| `jellyfish_present` | Conservar el booleano; añadir `jellyfish_status` (`present/absent/unknown`) | `False` solo es “ausencia” si `jellyfish_status = absent` con fuente; si no, `unknown` |
| `sargasso_level` | Conservar el entero; añadir `sargasso_status` (`none/present/unknown`) | `0` solo es “sin sargazo” si el estado lo confirma |
| `posidonia_present` | Conservar el booleano; añadir `posidonia_status` | `False` solo es “sin posidonia” si el estado lo confirma |
| `has_*` | Conservar los booleanos; **no** convertirlos en seis estados nuevos sin necesidad. Si se necesita procedencia por servicio, usar una tabla `beach_service_status` en una fase posterior | En Fase 1, los servicios sin procedencia se exponen `unknown`; no se afirma `false` |
| `data_status` | No usar `live` por defecto. `BeachCreate` debe nacer en `unavailable`; el seed debe ser `synthetic` o `unavailable` + `data_origin = seed` | `live` solo con observación válida y vigente |
| `data_origin` (nuevo) | `seed`, `manual`, `imported`, `observed`, `unknown` | Es la forma más compatible de distinguir el seed sin añadir un valor nuevo a `DataStatus` |
| `max_capacity` | No usarlo como capacidad oficial; no derivar presión sin referencia validada | `NULL`/no validado |
| `flag_color`, `water_quality` | Mantener `unknown`; corregir `data_quality` para que `unknown` no sea `observation` | Ya expresan desconocido, pero sus consumidores no lo respetan |

**Sobre `DataStatus`**: hoy solo tiene `live`, `estimated` y `unavailable`
(`src/models.py:47-50`). La columna es `String(20)`, así que añadir `synthetic` no requiere un
`ALTER TYPE` nativo. Sin embargo, **añadir un valor nuevo al enum de respuesta puede romper
clientes** que validen el enum. Recomendación de transición:

- exponer `synthetic` en `data_origin` y en `data_quality.nature`;
- mantener `data_status` en `unavailable` para el seed durante la fase de compatibilidad;
- decidir más adelante, con inventario de clientes, si se añade `synthetic` a `DataStatus`.

Si el propietario prefiere la opción más explícita, añadir `synthetic` a `DataStatus` es
posible, pero debe documentarse como cambio aditivo de enum y probarse con clientes.

### 3.5 Estrategia de migración recomendada

1. **No mezclar DDL y backfill en la misma migración.**
   - `0003`: solo tablas y columnas nuevas, todas anulables, sin defaults de servidor y sin
     tocar filas existentes.
   - `0004` o script de datos: auditoría y clasificación, con registro de lo cambiado.
2. **No poner `NULL` en las columnas legadas en Fase 1.** Se conservan `0`/`False` y se añade
   el estado. El `NULL` se decide en Fase 6, tras pruebas de contrato.
3. **No inventar procedencia.** Una fila sin evidencia queda `unknown`/`manual`; el seed
   nuevo se marca `seed` en el momento de inserción, no por comparación de valores.
4. **No crear observaciones a partir de defaults.** Una observación requiere fuente, método,
   `observed_at` y unidad; no se rellena con `0`/`False`.
5. **Auditoría previa**: contar filas por `data_status`, valores `0`/`False`, `NULL`,
   `max_capacity` presente y playas sin observación. La consulta es de solo lectura.
6. **Reversibilidad**: el `downgrade` de `0003` elimina solo lo nuevo; el backfill de `0004`
   guarda el valor anterior o se ejecuta con un informe que permita reconstruirlo.

### 3.6 Pruebas de contrato propuestas

1. `BeachResponse` con `current_occupation=0` y `occupancy_status="unknown"` no afirma
   “0 %”, “playa tranquila” ni `pressure_relative=0`.
2. `jellyfish_present=False` + `jellyfish_status="unknown"` no produce “sin medusas”.
3. `sargasso_level=0` + `sargasso_status="unknown"` no produce “sin sargazo”.
4. `has_lifeguard=False` + `service_status["lifeguard"]="unknown"` no produce “sin
   socorrista”.
5. `DataStatus` legado sigue aceptando `live/estimated/unavailable`; si se añade `synthetic`,
   la prueba de compatibilidad documenta el nuevo valor.
6. El seed nuevo no produce `data_status="live"`.
7. Una fila creada por la API sin fuente no se clasifica como `observed`.
8. La migración conserva el número de filas y no modifica los valores legados.
9. `NULL` en una columna legada, si se introduce en una fase posterior, se serializa como
   `null` y no como `0`/`False`.

---

## 4. Q31 — Vigencia de las observaciones

### 4.1 Definiciones

| Campo | Significado | Regla |
|---|---|---|
| `observed_at` | Instante en que la fuente observó/estimó el fenómeno | Obligatorio para una observación utilizable; no se inventa |
| `fetched_at` | Instante en que SANDAM obtuvo el dato | Obligatorio; no sustituye a `observed_at` |
| `valid_from` | Inicio de validez | Por defecto, `observed_at`, si la fuente lo permite |
| `valid_until` | Fin de validez | Explícito o derivado de una regla documentada; `NULL` = **desconocido**, no infinito |
| `validity_basis` | Por qué se eligió esa validez | `source_declared`, `source_cadence`, `product_horizon`, `none` |
| `status` | Vigencia | `current`, `stale`, `superseded`, `invalid`, `unknown` |

`last_updated` del registro **no** es la hora de la observación. Un `fetched_at` reciente no
hace joven un dato viejo.

### 4.2 Evidencia y política provisional por variable

| Variable | Evidencia disponible | Política provisional | ¿Puede ser `current`? |
|---|---|---|---|
| **Aforo/ocupación — Calvià** | Panel oficial de 4 zonas; la página indica actualización cada 15 min; una noticia local dice 10 min (discrepancia anotada) | Solo con convenio: `valid_until = observed_at + 15 min` si se confirma que el panel publica un snapshot con esa cadencia. No activar antes | Solo tras permiso y confirmación de la cadencia |
| **Aforo/ocupación — Consell** | App “Platges de Mallorca”; frecuencia no publicada | Sin regla documentada: `valid_until = NULL`, estado `unknown` para decisiones; mostrar “última observación disponible” | **No** |
| **Aforo/ocupación — Gemelo Digital** | Web con login; actualizaciones de socorristas “varias veces al día”; previsión diaria/7 días | Sin exportación ni API verificada; no se usa como observación actual | **No** |
| **Aforo/ocupación — UIB** | No verificado; el código apunta a `uib.cat`, el blueprint a `uib.es` | No usar; no hay regla de vigencia | **No** |
| **Meteorología (AEMET)** | API documentada; productos de observación y predicción con cadencias distintas | Registrar la cadencia del producto concreto. El caché de 30 min de `weather.py` **no** es una regla de validez | Solo si el producto y su cadencia están registrados |
| **Oleaje/estado del mar (SOCIB/Copernicus)** | Productos con resolución y cadencia variable; algunos son predicción, no observación | `valid_until` según producto/horizonte; declarar `nature` y resolución espacial. No presentar un modelo regional como medición puntual | Solo con la regla del producto |
| **Calidad del agua oficial** | Muestreo estacional; frecuencia exacta por verificar; PDF, no API verificada | Usar la fecha de muestreo y el periodo de clasificación oficial; si no se conoce, `valid_until = NULL` y no llamarlo actual | **No** como “tiempo real”; solo como observación periódica |
| **Medusas** | MedusApp: reporte ciudadano, sin API verificada; Consell/Gemelo: datos de socorrismo no verificados | Sin fuente sistemática: `valid_until = NULL`, `unknown`/`user_report`; no usar como factor | **No** |
| **Servicios e infraestructura** | Documentales; sin fecha de verificación en el modelo | `valid_until` explícito si la fuente lo da; si no, `NULL` y “documentado, no verificado hoy” | **No** como estado actual |
| **Restricciones y avisos oficiales** | Sin integración verificada; el código de alertas es fabricado (ver §5.5) | Solo una fuente oficial con hora y fin explícito. Si no hay fin, no se inventa; no se afirma que la playa es segura | Solo con fuente oficial |

### 4.3 Comportamiento ante datos antiguos, ausentes o contradictorios

- **Antiguo**: si `valid_until < now`, `status = stale`; se puede mostrar con su hora, pero no
  cuenta para `coverage` ni para una decisión como dato actual.
- **Ausente**: `status = unknown`; no se rellena con `0`, `False` ni “sin riesgo”. `coverage`
  no lo cuenta.
- **Contradictorio**: se conservan ambas observaciones, se aplica la prioridad documentada y,
  si no se resuelve, se marca conflicto/`unknown`; **no se promedia en silencio**.
- **Fuente caída**: se conserva el último dato válido solo como `stale`; no se renueva
  `fetched_at` para aparentar actualidad.
- **Reloj inconsistente**: `observed_at` futuro o una diferencia inexplicable se rechaza o se
  marca `invalid` con motivo; no se corrige inventando una hora.
- **Resolución espacial**: una observación regional no se presenta como puntual; se declara
  `spatial_resolution_m`.

### 4.4 Recomendación

1. **No hay un plazo universal.** Ni 15 minutos ni 30 minutos ni 24 horas se aplican a todas
   las variables.
2. `valid_until = NULL` significa **validez desconocida**, no validez infinita. Sin una regla
   documentada, la observación no puede ser `current` para una decisión.
3. `fetched_at` no prolonga la validez.
4. El caché de una API (por ejemplo, 30 minutos en `weather.py`) es una decisión de
   rendimiento, no una regla de vigencia.
5. La regla debe ser **por variable y por fuente**, no solo por variable. `variables.
   default_validity_minutes` de `data-model.md` es insuficiente si se usa como plazo universal;
   debe ser nullable y acompañarse de `validity_basis`, o sustituirse por reglas por
   `(variable, source)` cuando existan fuentes reales.
6. Prohibido usar “tiempo real” sin un umbral declarado y verificado (FR-020). Mientras
   tanto: “última observación disponible”, con hora y estado.
7. En seguridad, lo desconocido **no** es favorable: no se afirma que una playa es segura por
   no tener un aviso.

### 4.5 Pruebas necesarias

1. Reloj inyectable: `valid_until` futuro → `current`; pasado → `stale`; `NULL` → `unknown`
   (no `current`).
2. Observación sin `observed_at` no puede ser `current`.
3. Observación con `fetched_at` reciente y `observed_at` viejo sigue `stale`.
4. Dos fuentes contradictorias: se conservan ambas; no se promedia; se aplica prioridad.
5. Fuente caída: el último dato se degrada a `stale`, no se renueva.
6. `coverage` no cuenta defaults, `unknown` ni `synthetic` en producción.
7. `pressure_relative` es `null` si la observación es `stale` o `unknown`.
8. La API no usa la frase “tiempo real” si no hay regla verificada.

---

## 5. Q30 y Q33 — Acceso, permisos y licencias

### 5.1 Matriz de fuentes

La columna “acceso probado” distingue entre **haber localizado la página/documentación** y
**haber probado una API o extracción automatizada**. En esta fase no se ejecutaron scrapers ni
se usaron credenciales.

| Fuente | Encontrada | Acceso probado | API / interfaz | Licencia / condiciones | Histórico | Convenio | Estado para producción |
|---|---|---|---|---|---|---|---|
| **Consell de Mallorca — app Platges de Mallorca** | Sí, nota oficial | No automatizado; app móvil | App; sin API pública documentada | No verificada | No documentado | Sí | **Bloqueada** |
| **Govern — Gemelo Digital** | Sí, nota y login | No automatizado | Web con login; sin API pública documentada | No verificada | Uso interno; sin exportación pública | Sí | **Bloqueada** |
| **Calvià — panel de aforo** | Sí, panel oficial | No automatizado | Web; sin API pública documentada | No verificada | No documentado | Sí | **Bloqueada**; candidata a referencia con permiso |
| **UIB — ocupación por cámaras** | Código apunta a `ocupacioplatges.uib.cat`; blueprint a `uib.es` | No | Sin API pública verificada | No verificada | No verificado | Sí | **Bloqueada**; no usar bypass |
| **SOCIB** | Sí, API documentada | No se probó con credencial | API REST/Swagger; token | Términos no verificados en esta sesión | Repositorio | No para API, pero Q5 bloquea | **Bloqueada** por Q5 y revisión legal; no es ocupación |
| **AEMET OpenData** | Sí, API documentada | Cliente existente; no prueba live en esta fase | API REST; API key | Atribución AEMET; nota legal a revisar | Sí | No | **Viable técnicamente**, no integrada en esta fase |
| **Copernicus Marine** | Sí, catálogo/API | No | API/Toolbox; registro | Licencia CMEMS verificada (atribución/DOI) | Sí | No | **Viable** para contexto regional, no para ocupación |
| **Calidad oficial del agua** | Sí, informe PDF | No | PDF; API no verificada | No verificada | Informes anuales | Posible | **Bloqueada** para producción |
| **CAIB — `clima_maritim_platges`** | Sí, CKAN | Sí, API CKAN consultada | CKAN + GeoJSON/CSV | CC-BY verificada | Mensual | No | **Viable como contexto**, no observación instantánea |
| **CAIB — `carac_platges`** | Sí, CKAN | Consulta de metadatos | Descarga pública | `isopen: false`, licencia vacía | Mensual | No | **Bloqueada** |
| **CAIB — `platges-adherides-programa-antitabaquisme`** | Sí, CKAN | Consulta de metadatos | Descarga pública | Sin licencia declarada | No verificado | No | **Bloqueada** |
| **MedusApp** | Sí, app/web | No | Sin API pública verificada | No verificada | No verificado | Posible | **Bloqueada** |
| **112 Baleares** | No se encontró una fuente real; el código fabrica avisos | No | No | No | No | No | **No es una fuente**; retirar el código fabricado |
| **Google/TomTom/ORS** | Sí, comerciales | No | API comercial | Contractual, por verificar | — | Posible | **Fuera de alcance** |

### 5.2 Qué falta para cerrar Q30/Q33

Para cada fuente bloqueada, la evidencia que la resolvería es:

1. **Documento escrito** del organismo/proveedor con:
   - licencia o condiciones de reutilización;
   - si existe API, endpoint, autenticación, cuotas y límites;
   - frecuencia y latencia;
   - cobertura y resolución espacial;
   - histórico disponible y formato;
   - contacto responsable y fecha de revisión.
2. **Muestra de datos con marca temporal** y, si se va a validar, exportación histórica.
3. **Confirmación de que la web pública no es una autorización** para extracción masiva.
4. Para Calvià: confirmar la cadencia real (15 min oficial frente a 10 min en prensa), el
   carácter “solo arena” y la disponibilidad de histórico.
5. Para UIB: aclarar el dominio vigente (`.cat`/`.es`), si hay API y cuáles son las
   condiciones; el blueprint lo describe como página pública no inspeccionada.
6. Para SOCIB: rotar/revocar la credencial (Q5) y revisar términos; sin eso, no se usa.
7. Para calidad del agua: licencia, frecuencia exacta y posibilidad de consulta estructurada.
8. Para CAIB: corregir la licencia de `carac_platges` y de las playas sin humo, o autorización
   escrita.

### 5.3 Qué puede implementarse sin convenios

**Sí puede avanzar**:

- el contrato conceptual de observación;
- las tablas y columnas aditivas;
- la separación naturaleza/validación/vigencia;
- la clasificación del seed como `synthetic`;
- los estados `unknown` y la corrección de consumidores para no premiar defaults;
- el catálogo de fuentes con estados `blocked`/`research`;
- pruebas de contrato y migración;
- una demostración con datos sintéticos etiquetados.

**No puede avanzar sin permiso o licencia**:

- adaptadores de Calvià, Consell, Gemelo Digital, UIB, MedusApp y calidad del agua;
- uso de `carac_platges` o playas sin humo;
- validación de ocupación contra datos reales;
- afirmaciones de “tiempo real”, cobertura o histórico;
- cálculo de presión con datos reales.

**SOCIB**: aunque la API esté documentada, Q5 y la revisión de términos la mantienen
bloqueada. No se debe usar la credencial comprometida.

### 5.4 Riesgo específico: `/scraper/*` y los bypass

El código versionado contiene scrapers que:

- usan Selenium/Playwright y `scrapling` con `bypass=True`
  (`src/integrations/scrapling_v2.py:27-29`);
- intentan extraer ocupación de `ocupacioplatges.uib.cat` y de
  `platgesdebalears.com` sin API ni permiso verificado;
- se exponen en `/api/v1/scraper/actualizar`, `/ocupacion`, `/medusas` y `/banderas`
  (`src/api/scraper_endpoints.py`);
- usan `0` o `50` como fallback cuando no encuentran el dato
  (`scraper.py:436`; `scraper_scrapling.py:67`).

**No se han ejecutado en esta fase.** No son una fuente autorizada ni una base legal para
producción. Antes de un piloto deben desactivarse o retirarse; un `robots.txt` respetado no
concede licencia. Esta es una acción de código posterior, no de esta revisión.

### 5.5 Riesgo específico: alertas fabricadas

`src/integrations/alerts_system.py` devuelve avisos inventados: “todas las playas operan” con
fuente `112 Catalunya`, medusas “confirmadas” sin observación y una calidad del agua con fecha.
**No está importado desde `src/`**, pero no debe usarse ni conectarse. No es una fuente.

---

## 6. Q32 — Validación de métodos heurísticos

### 6.1 Métodos actuales

| Método | Implementación | Entradas | Salida | Problema |
|---|---|---|---|---|
| Ocupación `heuristic_hour_day_weather_v1` | `src/utils/predictions.py:73-139` | `current_occupation` actual, hora, día, meteo | Predicción 0–100, `validated=false`, `confidence=null` | La base puede ser un default `0`; los factores no tienen fuente empírica; `datetime.now()` no es inyectable |
| Medusas `heuristic_wind_tide_temperature_v1` | `src/utils/predictions.py:142-210` | `jellyfish_present` actual, viento, marea, temperatura | Riesgo 0–1, `validated=false`, `confidence=null` | La base puede ser `False` por defecto; el 0,1/0,7 y los umbrales no tienen fuente empírica |

Una suite de tests verde solo demuestra que el contrato se cumple; **no** demuestra exactitud.

### 6.2 Protocolo propuesto

#### Datos de referencia

- **Ocupación**: panel de Calvià (4 zonas, actualización oficial cada 15 min) y/o Consell/
  Gemelo Digital, **con convenio**. Se necesita exportación histórica con playa, hora y
  metodología, no una captura manual aislada.
- **Medusas**: registros de socorrismo o MedusApp moderados; si no hay una fuente sistemática,
  no se valida.
- **Meteo de entrada**: AEMET/SOCIB para las mismas horas, con estación y hora.

#### Obtención legítima

- solicitud escrita y permiso de uso;
- sin scraping, sin bypass, sin credenciales comprometidas;
- datos agregados, sin información personal;
- acuerdo de conservación y atribución.

#### Ventana y cobertura

- unidad de análisis: playa-día-hora;
- al menos una temporada completa (junio–septiembre); ideal dos;
- 4 playas de Calvià con perfiles distintos; si se amplía, declarar selección y sesgo;
- reportar cobertura y missing; no imputar sin declararlo.

#### Separación

- partición **temporal**, no aleatoria: entrenamiento/calibración en un periodo y evaluación en
  otro posterior;
- si solo hay una temporada, usar validación temporal por bloques o *rolling origin*;
- no elegir el umbral después de ver resultados.

#### Métricas

- **Ocupación**: MAE, RMSE, sesgo, correlación; error por franja y por playa; cobertura.
- **Medusas**: precisión, recall, F1, PR-AUC, matriz de confusión y prevalencia.
- Reportar intervalo/incertidumbre si el método lo permite.

#### Línea base

- **Ocupación**: persistencia (valor de la hora anterior) y, como contraste, media histórica
  por playa/franja.
- **Medusas**: tasa base/prevalencia histórica.

#### Criterios de aceptación

No se fijan números en esta revisión. El propietario debe aprobar **antes** de evaluar:

- cobertura mínima;
- mejora mínima frente a la línea base;
- sesgo máximo admitido;
- comportamiento por subgrupo (playa/franja);
- calibración exigida;
- qué se considera “inconcluso”.

Sin esos valores, el método queda `validated=false` y `confidence=null`.

### 6.3 Cuándo el método queda solo informativo

- no hay datos de referencia o el permiso no llega;
- la cobertura es insuficiente;
- no supera la línea base;
- empeora en un subgrupo relevante;
- la base de entrada es desconocida (ocupación/medusas sin observación);
- el método se usa fuera del rango temporal/espacial validado.

En todos esos casos: se muestra como **estimación no validada** o se retira; nunca como factor
de recomendación ni como exclusión de seguridad.

### 6.4 Lo que no vale como evidencia

- fixtures sintéticos;
- tests unitarios del contrato;
- una demo con seed;
- una captura manual sin hora;
- una comparación contra otra predicción.

Todo eso puede probar que el sistema funciona, pero **no** que el heurístico sea exacto.

---

## 7. Dependencias entre las preguntas

Leyenda: **Sí** = bloquea; **Parcial** = condiciona el diseño; **No** = no bloquea.

| Pregunta | Contrato conceptual | Estructura de BD | Migración `0003` | Ingestión de fuentes | Calidad/vigencia | Ocupación en recomendaciones | Validación de predicciones |
|---|---|---|---|---|---|---|---|
| **Q29** unidad/base | Parcial: unit/reference | Parcial: columnas de referencia | Parcial: se pueden añadir campos genéricos | Sí para ocupación real | Sí para presión | **Sí** | Parcial: base de entrada |
| **Q30** acceso/histórico | No | Parcial: catálogo de fuentes | No: se pueden crear fuentes `blocked` | **Sí** | No | Sí para datos reales | **Sí** |
| **Q31** vigencia | **Sí** | Parcial: `valid_until`/`validity_basis` | No: columnas anulables | Sí por fuente | **Sí** | Sí | Parcial: horizonte |
| **Q32** validación | No | No | No | No | No | No si es informativo | **Sí** |
| **Q33** licencias CAIB | No | Parcial: licencia en catálogo | No: fuentes `blocked` | **Sí** | No | No si no se usa | Parcial si se usa como referencia |
| **Q34** legados | **Sí** | **Sí**: estados/nullabilidad | **Sí**: columnas de estado, sin backfill automático | No | **Sí** | **Sí** | **Sí**: base de entrada |

### 7.1 Decisiones que deben resolverse antes de migrar

1. **Q34**: qué columnas de estado se añaden y si se mantiene `0`/`False` o se relaja a
   `NULL`. La recomendación es añadir estado y no tocar los valores legados en `0003`.
2. **Q29**: qué campos genéricos de unidad/referencia entran en `observations`; no hace falta
   elegir la unidad canónica, pero sí decidir que el contrato la admite.
3. **Q31**: que `valid_until = NULL` signifique desconocido y que no haya una regla universal.
4. **Vocabulario**: `unknown`, `stale`, `synthetic` y `data_origin`; decidir si `synthetic`
   entra en `DataStatus` o solo en `data_origin`/`data_quality`.

### 7.2 Decisiones que pueden permanecer abiertas

- **Q30/Q33**: acceso, API y licencia de Calvià, Consell, Gemelo Digital, UIB, MedusApp,
  calidad del agua y CAIB. No bloquean el modelo genérico ni la migración DDL.
- **Q32**: umbrales de aceptación y datos de referencia. No bloquean el modelo; solo el uso
  de los heurísticos como factor.
- **Q29**: unidad canónica y superficie de referencia. Pueden quedar abiertas si no se emite
  presión numérica y el contrato soporta ambas.
- **Q31**: reglas concretas de cada fuente. Pueden quedar abiertas si no se declara `current`
  sin regla documentada.
- **Q34**: ventana de transición y momento de pasar a `NULL`. Puede quedar abierta si se
  mantienen los campos legados con estado.

---

## 8. Impacto sobre la compatibilidad

| Elemento | Impacto | Mitigación |
|---|---|---|
| Tablas y columnas nuevas | Aditivo; no cambia columnas existentes | DDL en `0003`, sin backfill |
| `current_occupation: int` | No admite `NULL`; cambiarlo a opcional rompe clientes | Mantener entero + `occupancy_status` en la transición |
| `jellyfish_present`/`has_*`: `bool` | No admiten `NULL`; `False` sigue siendo ambiguo | Mantener booleano + estado; no afirmar ausencia sin fuente |
| `DataStatus` | Añadir `synthetic` puede romper clientes que validen el enum | Exponer `data_origin`/`data_quality`; decidir `DataStatus` con inventario |
| `BeachCreate.data_status` | Hoy nace `live`; cambiarlo a `unavailable` es un cambio de comportamiento | Documentar y probar; es una corrección de veracidad |
| `DashboardSummary.avg_occupation: float` | Si no hay observaciones válidas, el valor honesto es `null`, no `0` | Añadir `occupancy_coverage` y decidir `Optional[float]`; puede ser cambio incompatible |
| Filtros `occupation_min/max` | El desconocido no puede compararse como 0; excluirlo silenciosamente también es engañoso | Añadir metadato de filtro (`unknown_excluded`/`filter_status`) y probar contrato |
| `/donde-ir` `pressure_relative` | Pasa de `0.0` a `null` en casos desconocidos | Es intencionado; actualizar clientes y documentación |
| `/external` `occupation` | Sigue siendo un número sin unidad | Añadir `occupation_status`/`occupancy_unit`; no romper el campo |
| `/scraper/*` | No tiene base legal verificada y usa bypass | Desactivar antes de producción; no es compatible con FR-015 |
| Tests actuales | Asumen `data_status="live"`, `current_occupation` 0–100 y defaults | Actualizar con pruebas de compatibilidad, no solo cambiar asserts |

**Cambios potencialmente incompatibles** que requieren ADR/decisión:

- `avg_occupation` nullable;
- `current_occupation` nullable;
- `has_*` nullable;
- añadir `synthetic` a `DataStatus`;
- filtros de ocupación con semántica de “no evaluable”.

---

## 9. Riesgos de migración

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Mezclar DDL y backfill en `0003` | Rollback difícil; datos modificados sin traza | Separar `0003` (esquema) y `0004`/script (datos) |
| `NULL` inmediato en columnas legadas | Rompe Pydantic y clientes; puede borrar un `0` real | No aplicar en Fase 1; inventario y pruebas primero |
| `DataStatus.synthetic` en el enum | Clientes estrictos rechazan un valor nuevo | Usar `data_origin` en transición; decidir después |
| Filas existentes con defaults | Se confunden con observaciones | Auditoría de solo lectura; clasificar `unknown`, no inventar fuente |
| Seed reejecutado | Duplicados o `live` de nuevo | `data_origin=seed` en inserción; no tocar existentes sin auditoría |
| SQLite vs PostgreSQL | Diferencias de `ALTER TABLE`, FK, tipos | Probar la cadena completa en ambos; CI con PostgreSQL 16 |
| `DateTime` sin zona | Ambigüedad de vigencia | UTC explícito; `observed_at`/`fetched_at`/`valid_until`; tests con reloj |
| `capacity_reference` sin `capacity_method` | Capacidad aparente sin método | Mantener invariante ORM; auditar filas crudas |
| `max_capacity` del seed | Se usa como capacidad oficial | No derivar presión; etiquetar como no validada |
| Fuente sin licencia | Uso ilegal o no autorizado | Catálogo `blocked`; no adaptadores |
| Ingesta duplicada | Observaciones repetidas o contradictorias | `ingestion_runs` e idempotencia; no implementar aún |
| Caché confundido con vigencia | Dato viejo presentado como actual | `fetched_at` ≠ `valid_until`; regla explícita |
| Migración no probada en datos reales | Fallo en producción | Ensayo en copia/staging; no ejecutar en producción sin aprobación |

---

## 10. Pruebas necesarias antes de cerrar la Fase 1

### 10.1 Contrato y dominio

- unidad/referencia obligatorias para ocupación numérica;
- `pressure_relative` nulo si desconocido, sin unidad o sin referencia;
- `current_occupation=0` + estado `unknown` no es “0 %”;
- `jellyfish_present=False` + estado `unknown` no es “sin medusas”;
- `has_lifeguard=False` + estado `unknown` no es “sin socorrista”;
- seed nuevo no es `live`;
- `data_quality` no etiqueta `unknown` como `observation`;
- `coverage` no cuenta defaults;
- `valid_until=NULL` no es `current`;
- reloj inyectable: `current`/`stale`/`invalid`;
- contradicción: se conservan ambas fuentes, sin promedio;
- fuente caída: `stale`, no renovación.

### 10.2 Migración

- `0003` upgrade/downgrade en SQLite y PostgreSQL 16;
- columnas e índices esperados;
- filas existentes preservadas;
- valores legados sin cambios;
- columnas nuevas anulables y sin defaults de servidor;
- `data_status` `String(20)` acepta `synthetic` sin `ALTER TYPE`;
- orden de creación de tablas/FK;
- `downgrade` no toca datos preexistentes;
- prueba de que el backfill (si se ejecuta) es auditable y reversible.

### 10.3 Contrato de API

- snapshots de `/beaches`, `/donde-ir`, `/recommendations`, `/search`, `/external` y
  `/dashboard`;
- campos existentes preservados;
- campos nuevos aditivos;
- `null` vs `0`/`false` documentado;
- filtros de ocupación con desconocido: sin comparación silenciosa;
- `avg_occupation` y cobertura: decisión explícita.

### 10.4 Auditoría de datos

- filas por `data_status`;
- filas con `current_occupation=0`;
- filas con `jellyfish_present=False`, `sargasso_level=0`, `posidonia_present=False`;
- filas con `has_*=False`;
- filas con `max_capacity` y `capacity_reference`;
- playas sin observación;
- **sin modificar datos**.

### 10.5 Lo que no es una prueba de exactitud

- fixtures sintéticos;
- seed;
- tests de contrato;
- una demo.

La exactitud solo se prueba con el protocolo de Q32 y datos de referencia autorizados.

---

## 11. Decisiones que necesitan aprobación expresa del propietario

1. **Q29**: aceptar que no se adopta una unidad canónica todavía y que `pressure_relative`
   queda `null` hasta que haya unidad y referencia defendibles.
2. **Q29**: decidir si el contrato soporta `%` y `count` simultáneamente o si se elige una
   sola unidad para el piloto.
3. **Q34**: aprobar la transición “valor legado + estado explícito” y rechazar el `NULL`
   masivo en Fase 1.
4. **Q34**: decidir si `synthetic` se añade a `DataStatus` o se expresa solo en
   `data_origin`/`data_quality`.
5. **Q31**: aprobar que `valid_until = NULL` significa desconocido y que no se usará “tiempo
   real” sin umbral verificado.
6. **Q31**: aprobar la política provisional por variable, especialmente la de Calvià (15 min)
   y la de calidad del agua (estacional).
7. **Q30/Q33**: decidir si se inicia contacto formal con Calvià, Consell, Gemelo Digital, UIB
   y el responsable de calidad del agua; sin acuerdo, no hay adaptadores.
8. **Q32**: aprobar el protocolo y los umbrales de aceptación **antes** de ver resultados.
9. **Compatibilidad**: aprobar o rechazar los cambios potencialmente incompatibles
   (`avg_occupation` nullable, filtros con estado, `current_occupation` nullable).
10. **Seguridad**: ordenar la desactivación de `/scraper/*` y la retirada del código de bypass
    antes de cualquier despliegue; la rotación de SOCIB sigue siendo del propietario.

---

## 12. Preguntas que pueden permanecer abiertas

- **Q29**: unidad canónica y superficie de referencia, siempre que no se emita presión
  numérica y el contrato admita unidad/referencia.
- **Q30/Q33**: API, histórico, licencia y convenio de las fuentes; no bloquean el modelo
  genérico.
- **Q31**: reglas concretas de cada fuente; no bloquean el DDL si `valid_until` es anulable y
  `NULL` significa desconocido.
- **Q32**: umbrales de aceptación y datos de referencia; no bloquean el modelo, solo el uso
  de heurísticos como factor.
- **Q34**: ventana de transición y paso final a `NULL`; no bloquea la Fase 1 si se conservan
  los valores legados con estado.
- **Q1/Q11/Q14**: capacidad oficial, catálogo de vulnerabilidad y reglas anti-traslado; siguen
  fuera de esta fase.

---

## 13. Plan acotado para Fase 0/1 (no ejecutado)

### Fase 0A — Decisiones y contrato (sin código)

**Objetivo**: congelar el contrato antes de tocar la base.

- Aprobar las decisiones de §11.
- Añadir al contrato de observación: `unit`, `reference_type`, `reference_value`,
  `reference_unit`, `reference_source_id`, `reference_is_validated`, `validity_basis`.
- Definir `unknown` vs `null` y `synthetic`.
- Revisar `data-model.md`:
  - `variables.default_validity_minutes` no puede ser un plazo universal;
  - `services_status` no se implementa como mapa JSON; se difiere o se normaliza;
  - `observations` necesita los campos de referencia de Q29.
- **Salida**: contrato y decisiones aprobadas; ninguna migración.

### Fase 0B — Auditoría de solo lectura

- Script `scripts/audit_legacy_defaults.py` o consulta SQL equivalente, sin escrituras.
- Métricas: filas por `data_status`, `0`/`False`, `NULL`, `max_capacity`, playas sin
  observación.
- Si la base no está disponible, el informe declara “no verificable” y no inventa cifras.
- **Salida**: `docs/DATA_AUDIT_OCCUPANCY.md` con evidencia y limitaciones.

### Fase 0C — Catálogo de fuentes

- Cargar `data_sources` con estados `research`/`blocked`; ninguna fuente sin licencia queda
  `active`.
- No crear adaptadores.
- **Salida**: catálogo inicial y lista de bloqueos.

### Fase 1A — Migración `0003` solo DDL

- Tablas: `data_sources`, `variables`, `methods`, `transformations`, `validation_records`,
  `ingestion_runs`, `observations`.
- Columnas en `beaches`: `occupancy_status`, `jellyfish_status`, `sargasso_status`,
  `posidonia_status`, `data_origin`, todas anulables y sin defaults de servidor.
- `observations`: unidad, referencia, tiempos, naturaleza, validación, estado.
- Índices: `(beach_id, variable_code, observed_at)`, `(status, valid_until)`,
  `(source_id, fetched_at)`.
- Sin backfill, sin cambios de valores, sin tocar `current_occupation`.
- **Salida**: esquema nuevo; API sin cambios.

### Fase 1B — Clasificación de legados (separada)

- `0004` o script de datos, solo después de la auditoría y con aprobación.
- Seed nuevo: `data_origin=seed`, `data_status=unavailable` (o `synthetic` si se aprueba),
  estados `unknown`.
- Filas sin origen: `data_origin=unknown`, estados `unknown`; no se crean observaciones.
- Guardar traza de lo cambiado.
- **Salida**: datos clasificados sin inventar fuente.

### Fase 1C — Pruebas y documentación

- Migración SQLite/PostgreSQL, `downgrade`, compatibilidad de respuestas.
- Documentar `unknown`, `stale`, `synthetic`, unidad/referencia y límites.
- **Salida**: Fase 1 verificable; sin consumidores nuevos y sin fuentes.

### Exclusión expresa

No forman parte de esta Fase 0/1:

- adaptadores AEMET, SOCIB, Copernicus, Calvià, Consell, Gemelo Digital, UIB, MedusApp,
  calidad del agua o CAIB;
- uso de `carac_platges` o playas sin humo;
- cálculo de presión con datos reales;
- cambio de pesos o inclusión de ocupación en el score;
- activación de `/scraper/*`;
- cualquier dato sintético presentado como real.

---

## 14. Recomendación única para el siguiente paso

**No empezar por la migración.** El siguiente paso debe ser aprobar Q29/Q31/Q34 con la
dirección propuesta —campo legado + estado explícito, unidad/referencia en la observación,
`valid_until=NULL` como desconocido y ninguna presión numérica sin base— y ejecutar después
solo la Fase 0/1: auditoría de solo lectura, contrato y migración `0003` DDL, sin backfill
automático y sin adaptadores. Q30/Q33 y Q32 pueden seguir abiertas y no deben bloquear ese
trabajo.

---

## Anexo — Archivos y referencias revisados

- `AGENTS.md`; `.specify/memory/constitution.md`.
- `specs/002-trusted-observations-and-occupancy/spec.md`, `research.md`, `data-model.md`,
  `plan.md`, `tasks.md`, `contracts/`.
- `src/models.py`, `src/schemas.py`, `src/crud.py`, `src/api/beaches.py`,
  `src/api/dashboard.py`, `src/api/donde_ir.py`, `src/api/external_data.py`,
  `src/api/scraper_endpoints.py`, `src/utils/scoring.py`, `src/utils/recommendations.py`,
  `src/utils/recommendation_engine.py`, `src/utils/predictions.py`, `src/utils/fallback.py`.
- `src/integrations/scraper.py`, `scraper_scrapling.py`, `scrapling_v2.py`,
  `real_data_client.py`, `alerts_system.py`.
- `alembic/versions/0001_initial.py`, `0002_metadata_fields.py`; `seed_data.py`;
  `tests/conftest.py`, `tests/test_beaches.py`, `tests/test_migrations.py`.
- `docs/OPEN_QUESTIONS.md`, `docs/API_GUIDE.md`, `docs/PROJECT_CONTEXT.md`,
  `docs/CONTEXTO_MAESTRO.md`, `docs/PRODUCT_BLUEPRINT.md`.
