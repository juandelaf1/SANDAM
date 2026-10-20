# Phase 0 — Research: observaciones fiables, procedencia y presión

**Feature**: 002-trusted-observations-and-occupancy
**Fecha**: 2026-10-20
**Estado**: investigación y diseño; **nada de esto está implementado**.

Este documento registra (a) el estado real del dato en SANDAM, (b) las rutas que
convierten lo desconocido en una señal favorable, (c) las fuentes investigadas con su
acceso y licencia, (d) el contrato conceptual de observación y (e) el protocolo de
validación. No sustituye a la implementación ni a una revisión legal de licencias.

## 1. Método y límites

- Se leyó el código de `src/` y se contrastó con `specs/001-.../spec.md`,
  `data-model.md` y `convergence-audit.md`.
- Se consultaron páginas y API públicas **sin** eludir autenticación, sin rastrear masivamente
  y sin usar credenciales.
- Cuando una fuente no se pudo verificar (contenido dinámico, PDF, login), se marca
  **no verificada** en lugar de suponer su contenido.
- Las licencias se registran como **verificadas** solo si la página consultada las enuncia.
  Una descarga pública no equivale a licencia de reutilización.

## 2. Baseline: qué representa hoy cada variable

Matriz variable × origen actual × semántica × procedencia × vigencia × usos × riesgo ×
corrección. `models.py` se cita por línea.

| Variable | Origen actual | Semántica real | Procedencia | Vigencia | Usos | Riesgo | Corrección propuesta |
|---|---|---|---|---|---|---|---|
| `current_occupation` | Seed + `default=0` (`models.py:71`); esquema Pydantic `default=0` | Entero 0–100 sin unidad ni método; 0 puede significar “vacía” o “sin dato” | Ninguna | `last_updated` del registro, no de la observación | Score (no), explicación (sí), `/recommendations` (sí), `/search` (sí), `/external` (sí), dashboard (media) | Alto: presenta desconocido como 0 % y como mérito | `occupancy_status` + observación con fuente/hora/validez; no usarla como mérito |
| `flag_color` | Seed + `default=unknown` | Estado de bandera; `unknown` es correcto | Ninguna | No | Elegibilidad (amarilla/roja), explicación | Medio: `unknown` limita, no excluye; no hay hora | Observación con `observed_at` y `valid_until` corto |
| `water_quality` | Seed + `default=unknown` | Categoría oficial o desconocida | Ninguna | No | Score/explicación; `data_quality` la llama “observation” aunque sea `unknown` | Alto: etiqueta errónea | Observación periódica (temporada) con fuente oficial y validez |
| `water_temp` | Seed; nullable | Temperatura puntual o regional | Ninguna | No | Explicación, predicción de medusas | Medio | Observación/estimación con resolución espacial |
| `air_temp` | Seed; nullable | Temperatura | Ninguna | No | Explicación | Bajo | Observación AEMET con estación y hora |
| `uv_index` | Seed; nullable | Índice UV | Ninguna | No | Score | Medio | Observación/previsión AEMET con horizonte |
| `wind_speed` | Seed; nullable | Viento | Ninguna | No | Explicación, medusas | Medio | Observación AEMET/SOCIB con hora |
| `wave_height` | Seed; nullable | Oleaje | Ninguna | No | Score | Medio | Observación/estimación SOCIB/Copernicus con hora y resolución |
| `tide` | Seed; nullable | Marea | Ninguna | No | Solo informativo | Bajo | Observación/estimación con hora |
| `jellyfish_present` | Seed + `default=False` (`models.py:82`) | Booleano; `False` mezcla “no hay” y “no se sabe” | Ninguna | No | Elegibilidad/explicación/alertas | **Alto**: “✓ Sin medusas” sin dato | `jellyfish_status` (`present/absent/unknown`) + observación |
| `jellyfish_species` | Seed; nullable | Especie | Ninguna | No | Informativo | Bajo | Observación con método |
| `sargasso_level` | Seed + `default=0` (`models.py:85`) | Nivel 0–3; 0 mezcla “sin sargazo” y “sin dato” | Ninguna | No | Explicación | Alto | `sargasso_status` + observación |
| `posidonia_present` | Seed + `default=False` (`models.py:86`) | Booleano; `False` mezcla ausencia y desconocido | Ninguna | No | Informativo | Medio | Estado explícito + fuente |
| `has_kiosk/shade/showers/parking/accessibility/lifeguard` | Seed + `default=False` (`models.py:92-97`) | Servicio disponible; `False` mezcla “no existe” y “no documentado” | Ninguna | No | Elegibilidad (socorrista), explicación, `/search` | **Alto**: “Sin socorrista” sin dato | `service_status` (`present/absent/unknown`) + fuente documental |
| `max_capacity` | Seed; nullable | Cifra sin metodología | Ninguna | No | `relative_pressure` (indirecto) | Alto (Q1) | No usar como capacidad oficial; si se usa, etiquetar como referencia no validada |
| `protection_status`, `access_restrictions`, `capacity_reference`, `capacity_method`, `vulnerability_level` | Migración 0002; nullable | NULL = desconocido (correcto) | Parcial (texto libre) | No | Elegibilidad/informativo | Bajo | Mantener; validar catálogo (Q11/Q14) |
| `data_status` | `default=unavailable`; seed lo fuerza a `live` (`seed_data.py:536`); `BeachCreate` usa `live` por defecto (`schemas.py:44`) | Estado global del registro | Ninguna | No | `/recommendations` lo devuelve | **Alto**: seed y altas “live” sin observación | `synthetic` para seed; `live` solo con observación válida |
| `last_updated` | Automático del registro | Última escritura del registro, no de la observación | — | — | Informativo | Medio: se confunde con hora del dato | Mantener como metadato del registro; añadir `observed_at` |

### 2.1 Defaults que afirman un hecho

`current_occupation=0`, `jellyfish_present=False`, `sargasso_level=0`, `posidonia_present=False`
y los seis `has_*` son **defaults de Python** (no de servidor). En la práctica, cualquier fila
creada por el ORM sin esos campos afirma un hecho que no se ha observado. El seed los rellena
con valores concretos y además marca el registro como `live`.

### 2.2 `data_quality` actual

`recommendation_engine.py:255-260`:

```python
"water_quality": {"nature": "observation" if playa.get("water_quality") is not None else "unknown", "source": None},
"occupation":    {"nature": "observation" if playa.get("current_occupation") is not None else "unknown", "source": None},
```

- `water_quality` siempre es una cadena (`"unknown"` por defecto) → nunca es `None` → siempre
  “observation”.
- `current_occupation` siempre es un entero (0 por defecto) → siempre “observation”.
- `source` es `None` en todas.
- No cubre `flag_color`, medusas, sargazo, servicios.

## 3. Rutas que convierten lo desconocido en favorable

| Archivo:línea | Comportamiento | Efecto |
|---|---|---|
| `src/utils/recommendations.py:47-51` | `occupation = beach.get("current_occupation", 0)`; si ≥ 90 avisa, si ≥ 70 avisa | Un default 0 no genera aviso; un 0 real tampoco. No distingue. |
| `src/utils/recommendations.py:73-74` | `if occupation < 50: details.append("✓ Playa tranquila")` | **Premia el desconocido** (0) como playa tranquila. |
| `src/utils/recommendations.py:67-68` | `if not beach.get("jellyfish_present"): details.append("✓ Sin medusas")` | **Afirma ausencia** de medusas cuando el valor es `False` por defecto. |
| `src/utils/recommendations.py:76` | Si no hay mensajes: “Condiciones óptimas para el baño” | **Afirma condiciones óptimas** sin datos. |
| `src/utils/recommendations.py:55-58` | `if not beach.get("has_lifeguard"): "Sin socorrista"` | **Afirma ausencia** de socorrista cuando es `False` por defecto. |
| `src/crud.py:220` | `if beach.current_occupation and max_occupation ...` | Un 0 desactiva el filtro de ocupación. |
| `src/crud.py:240-241` | `if alt["current_occupation"] < beach.current_occupation: "Ocupación menor"` | **Premia** la ocupación baja, incluso si es default. |
| `src/crud.py:246-247` | `if not alt["jellyfish_present"] and beach.jellyfish_present: "Sin medusas"` | Compara booleanos con defaults; puede afirmar ausencia. |
| `src/api/external_data.py:103,113` | Devuelve `occupation` sin estado | Cliente no puede saber si es 0 real o desconocido. |
| `src/api/dashboard.py:19,104` | `avg(current_occupation)` | La media incluye defaults 0 y sesga a la baja. |
| `src/utils/fallback.py:19-21` | `jellyfish_present=None → False` + disclaimer | Convierte desconocido en “sin medusas” (el disclaimer no cambia el valor). |
| `src/utils/recommendations.py:111-116` | `if occupation >= 90: alerta “máxima capacidad”` | Un default 0 no genera alerta; el desconocido se presenta como “no lleno”. |
| `src/utils/recommendation_engine.py:312` | `"{}%".format(playa.get("current_occupation", 0))` | `/evaluar-playa/{nombre}` muestra `0%` cuando no hay dato. |
| `src/utils/scoring.py:253` | `relative_pressure(beach.get("current_occupation"))` | La función maneja bien `None`, pero el default `0` produce `0.0` (presión nula aparente). |
| `src/api/donde_ir.py:27` + `recommendation_engine.py:235` | `flags.ocupacion` y `flags.medusas` sin estado | La UI puede interpretar 0/False como hechos. |

**Conclusión**: el problema no es solo un campo; es una cadena de decisiones que interpreta
“valor por defecto” como “hecho observado”. La spec 002 debe romper esa cadena en el origen
(estado explícito) y en cada consumidor.

## 4. Fuentes investigadas

Clasificación de acceso:

- **API documentada**: existe documentación pública de API.
- **Descarga pública**: ficheros descargables, sin API de consulta.
- **Interfaz web**: solo panel/página; sin contrato de datos.
- **Requiere convenio/permiso**: no hay acceso público documentado; hace falta acuerdo.
- **No verificada**: no se pudo confirmar en esta sesión.

### 4.1 Cuadro resumen

| Fuente | Variables | Cobertura | Resolución / frecuencia | Histórico | Método | Acceso | Licencia / condiciones | Coste | Validación | Decisión |
|---|---|---|---|---|---|---|---|---|---|---|
| **Consell de Mallorca — app “Platges de Mallorca”** | Ocupación, condiciones de baño, pasarelas accesibles | Playas de Mallorca con servicio de socorrismo | “Tiempo real”; frecuencia no publicada | No documentado | Datos de la Direcció General d'Emergències i Interior | App móvil; **sin API pública documentada** | **No verificada**; requiere permiso | Desconocido | Comparar con aforo municipal | **Requiere convenio**; no raspar |
| **Govern — Gemelo Digital de Turismo** (`platges.illesbalears.travel`) | Ocupación actual, previsión 7 días, alternativas | Baleares; en pruebas | Varias veces/día (socorristas); previsión diaria | Datos históricos usados por el modelo; no se ofrece exportación pública | Modelos analíticos + IA; actualizaciones de socorristas | **Interfaz web con login**; sin API pública documentada | **No verificada**; requiere acuerdo | Desconocido | Comparar con observación directa | **Requiere convenio** |
| **Ajuntament de Calvià — panel de aforo** | Ocupación total (solo arena), personas presentes, espacio por persona | Peguera, Palmanova, Magaluf, Santa Ponça (4 zonas) | **Cada 15 min** según la página oficial | No documentado | Cámaras/sensores; estimación | **Interfaz web**; sin API pública documentada | **No verificada**; requiere permiso | Desconocido | Fuente de referencia prioritaria para validar heurísticos | **Requiere convenio**; candidato a piloto |
| **UIB (estimaciones/cámaras)** | Ocupación | No verificada | No verificada | No verificado | No verificado | **No verificada**: no se encontró API pública | **No verificada** | Desconocido | — | **No usar** hasta verificar |
| **SOCIB** | Oleaje, temperatura, corrientes, viento, nivel del mar | Plataformas fijas y modelos del Mediterráneo occidental | Depende del producto; tiempo real y diferido | Sí (repositorio) | Medición in situ + modelos | **API documentada** (`api.socib.es`, Swagger, notebooks); credencial para acceso máquina-máquina | Términos de uso públicos; **revisión legal pendiente** | Gratuito | Comparar con estación/playa | **Viable para meteoceánica**, no para ocupación |
| **AEMET OpenData** | Temperatura, viento, UV, precipitación, avisos | Estaciones de Baleares; terrestre | Según producto (observación y predicción) | Sí | Medición + modelos | **API REST documentada**; API key gratuita | Reutilización con atribución (“citando a AEMET”); **revisar nota legal** | Gratuito | Comparar estación vs playa | **Viable**; ya hay cliente |
| **Copernicus Marine** | SST, oleaje, corrientes, salinidad, turbidez | Mediterráneo / global | Resolución variable según producto (consultar ficha); horario/diario | Sí | Modelos + observaciones asimiladas | **API/Toolbox documentada**; registro gratuito | Licencia CMEMS: uso libre, modificación y redistribución con atribución y DOI | Gratuito | Comparar con SOCIB | **Viable** para contexto regional |
| **Calidad oficial de aguas de baño (Govern)** | Calidad microbiológica, clasificación | 160 zonas de baño; 191 puntos (Mallorca 113, Eivissa 41, Menorca 30, Formentera 7) | Muestreo estacional (frecuencia exacta **por verificar**) | Informes anuales | Analítica oficial | **Descarga pública (PDF)**; no se verificó API | **No verificada**; datos públicos con condiciones por confirmar | Gratuito | Fuente oficial | **Viable como observación periódica**; no “tiempo real” |
| **CAIB Open Data — `clima_maritim_platges`** | Hs, Tp, dirección, extremos | Playas de Baleares | **Mensual**; derivado | Sí | Propagación de oleaje/mareas/surges desde aguas externas a 10 m | **API CKAN + GeoJSON/CSV** | **CC-BY** (verificada) | Gratuito | No es observación actual; es clima marítimo | **Viable como contexto**, no como observación instantánea |
| **CAIB Open Data — `carac_platges`** | Longitud, altura de berma, pendiente sumergida, calibre de sedimento | Playas de Baleares | Mensual | Sí | Caracterización física | **Descarga pública** GeoJSON/CSV | **Licencia no declarada** (`isopen: false`) | Gratuito | Útil para capacidad física, pero **no usar** hasta aclarar licencia | **Bloqueada por licencia** |
| **MedusApp** | Avistamientos y picaduras reportadas por usuarios | Cobertura variable (**no verificada**) | Tiempo real ciudadano | No verificado | Reporte voluntario | **App/web**; sin API pública documentada | **No verificada** | Gratuito | Requiere moderación y contraste | **No usar** sin acuerdo/licencia |
| **Google Routes / TomTom / ORS** | Tiempo de viaje por carretera | Mallorca | Tiempo real/estático según proveedor | — | Tráfico + red viaria | **API comercial** | Contractual (**por verificar**) | De pago o cuota (**por verificar**) | Comparar con rutas conocidas | **Fuera de alcance** de esta spec |
| **RASPAL_SCRAPER** | — | — | — | — | Scraping con robots.txt, throttle, caché | Herramienta local | MIT (según su README) | Gratuito | — | **Herramienta de ingesta**, no fuente; no autoriza a raspar |
| **ClimApp** | Meteorología AEMET por coordenadas | España | Según AEMET | Sí (SQLite/JSON) | Ingesta + normalización + reintentos + validación | Flask local | — | Gratuito | — | **Reutilizar patrones**, no datos |
| **GeoRisk_Finder** | Riesgos sísmicos/ciclónicos/volcánicos | Global; H3 resolución 3 | Agregado | — | Clustering | FastAPI local | — | Gratuito | No es escala playa | **No aplicable** a ocupación |

### 4.2 Fichas de las fuentes prioritarias

#### Consell de Mallorca — “Platges de Mallorca”

- **Qué es**: app móvil del Consell de Mallorca con información de ocupación y condiciones de
  baño de las playas de Mallorca con servicio de socorrismo; operativa desde junio de 2021.
- **Origen del dato**: Direcció General d'Emergències i Interior.
- **Evidencia**: nota oficial del Consell (URL en §8).
- **Acceso**: app móvil; **no se encontró API pública documentada**. La web institucional no
  publica un contrato de datos.
- **Licencia**: no verificada. No se debe asumir reutilización por ser una app pública.
- **Limitaciones**: no cubre playas sin socorrista; frecuencia no publicada; no hay histórico
  descargable.
- **Uso propuesto**: fuente de referencia para validar ocupación, previo convenio.

#### Govern — Gemelo Digital de Turismo

- **Qué es**: plataforma web (`platges.illesbalears.travel/login`) con ocupación actual,
  previsión a 7 días y recomendaciones de alternativas; en fase de pruebas.
- **Origen del dato**: equipos de socorrismo que actualizan varias veces al día; el modelo
  combina histórico, tiempo real, día de la semana, condiciones ambientales y meteoceánicas.
- **Acceso**: requiere login; **no se encontró API pública documentada**.
- **Licencia**: no verificada; requiere acuerdo.
- **Limitaciones**: en pruebas y ampliación progresiva; cobertura/frecuencia no garantizadas;
  las previsiones son predicción, no observación.
- **Uso propuesto**: referencia de ocupación y benchmark de predicción, previo convenio.

#### Ajuntament de Calvià — panel de aforo

- **Qué es**: panel público de aforo de Peguera, Palmanova, Magaluf y Santa Ponça.
- **Datos**: aforo total (solo zona de arena), distribución de espacio disponible por persona y
  número de personas presentes.
- **Frecuencia**: **cada 15 minutos** según la página oficial (una noticia local dice 10 minutos;
  prevalece la fuente oficial y se anota la discrepancia).
- **Método**: sistema de cámaras/sensores; la noticia local menciona sensores inteligentes y, en
  una segunda fase, boyas para temperatura, pH y turbidez. **Las boyas son futuras, no actuales.**
- **Acceso**: interfaz web; **sin API pública documentada**.
- **Licencia**: no verificada; requiere permiso municipal.
- **Limitaciones**: solo 4 zonas; no cubre toda la isla; la cifra es una estimación del sistema,
  no un conteo manual certificado.
- **Uso propuesto**: **referencia prioritaria** para el protocolo de validación de ocupación
  (permite comparar a la misma hora y en la misma playa).

#### SOCIB

- **Qué es**: ICTS de observación costera de Baleares.
- **Acceso**: API documentada en `https://api.socib.es` con Swagger
  (`https://api.socib.es/swagger/`), ejemplos en Python
  (`https://github.com/socib/API_examples`); permite JSON y netCDF; requiere credencial
  (API key/token) para acceso máquina-máquina.
- **Datos**: entradas del repositorio (tiempo real, diferido, L0/L1/L2), con filtros por
  instrumento, plataforma, variable, fecha, etc.
- **Licencia**: la página de términos de uso existe, pero su contenido no se pudo verificar en
  esta sesión (render dinámico). **Revisión legal pendiente.**
- **Limitaciones**: no mide ocupación; la resolución espacial es de plataforma/modelo, no de
  playa; no todas las playas tienen estación.
- **Uso propuesto**: observación/estimación de oleaje, temperatura y corrientes; etiquetar
  resolución y método.

#### AEMET OpenData

- **Acceso**: API REST; requiere API key gratuita; permite interacción periódica/programada.
- **Licencia**: reutilización con atribución (“citando a AEMET como autora”); consultar la nota
  legal para condiciones completas.
- **Datos**: observación y predicción; estaciones; avisos.
- **Limitaciones**: la estación no está en la playa; hay que interpolar o declarar la distancia.
- **Uso propuesto**: observación meteorológica con `station_id`, `observed_at` y distancia a la
  playa.

#### Copernicus Marine

- **Acceso**: catálogo y Toolbox/API; registro gratuito.
- **Licencia**: gratuita, mundial, no exclusiva, perpetua; permite copia, modificación,
  productos derivados y redistribución; exige atribución y citar DOIs.
- **Datos**: temperatura, salinidad, corrientes, oleaje, viento, turbidez, etc.; productos de
  forecast, near-real-time y multi-year.
- **Limitaciones**: resolución de modelo (no observación puntual); posibles sesgos cerca de
  costa (verificar por producto).
- **Uso propuesto**: contexto regional y contraste; nunca presentarlo como medición de la playa.

#### Calidad oficial de aguas de baño

- **Qué es**: control oficial de zonas de baño de las Illes Balears.
- **Datos**: 160 zonas de muestreo; 191 puntos (Mallorca 113, Eivissa 41, Menorca 30,
  Formentera 7) (informe 2026 de Informe Mar Balear, a partir de datos del Govern).
- **Acceso**: informe PDF público; no se verificó una API de consulta.
- **Licencia**: no verificada.
- **Limitaciones**: muestreo estacional, no continuo; la clasificación puede referirse a la
  temporada, no al día; no confundir con “tiempo real”.
- **Uso propuesto**: observación periódica con `valid_until` de días/semanas según la regla
  oficial que se acuerde.

#### CAIB Open Data

- **API**: CKAN (`/api/3/action/package_search`, `package_show`), verificada.
- **`clima_maritim_platges`**: mensual, CC-BY, GeoJSON/CSV; **derivado** de propagación de
  oleaje/mareas/surges, no observación instantánea.
- **`carac_platges`**: características físicas (longitud, berma, pendiente, sedimento), mensual;
  `isopen: false` y licencia vacía → **no usar en producción** hasta aclarar.
- **`platges-adherides-programa-antitabaquisme`**: GeoJSON; sin licencia declarada.

#### MedusApp

- **Qué es**: app/web de reporte ciudadano de avistamientos y picaduras.
- **Acceso**: no se encontró API pública documentada.
- **Licencia**: no verificada.
- **Limitaciones**: reporte voluntario, sesgo de participación, posible duplicación, requiere
  moderación; no es una observación científica sistemática.
- **Uso propuesto**: no integrar; si se usa, `nature=user_report`, `validated=false` y con
  contraste.

### 4.3 Fuentes descartadas o no verificadas

- **UIB**: no se encontró una API pública de ocupación. No se afirma que exista ni que no; se
  marca **no verificada**. Cualquier colaboración requiere confirmación de la UIB.
- **Webcams**: no se usan para estimar ocupación sin permiso y sin resolver privacidad.
- **Scraping de apps/web municipales**: descartado. RASPAL puede respetar `robots.txt`, pero eso
  no concede licencia ni permiso de reutilización.

## 5. Contrato conceptual de observación

Detalle completo en [`data-model.md`](./data-model.md) y
[`contracts/observation.schema.json`](./contracts/observation.schema.json).

Resumen de la entidad:

```text
Observation
  observation_id, beach_id, variable_code
  value (num | bool | text | null), unit
  nature: observation | user_report | estimate | prediction | historical | synthetic | unknown
  source_id, method_id
  observed_at, fetched_at, valid_from, valid_until
  spatial_resolution_m, uncertainty, uncertainty_unit
  validation_status: unvalidated | validated | rejected
  transformation_id
  privacy: aggregation_level, contains_personal_data
  status: current | stale | superseded | invalid
```

Reglas clave:

1. `nature` describe **cómo se obtuvo**; `validation_status` describe **si se contrastó**;
   `status` describe **si sigue vigente**. No son lo mismo.
2. Sin `source_id`, `method_id` y `observed_at`, una observación no puede ser `current`.
3. `unknown` no es un valor: es la ausencia de observación utilizable. No se serializa como 0.
4. `synthetic` nunca se usa en producción.
5. `valid_until` se define por variable y fuente; no hay una validez universal.
6. La unidad es obligatoria para valores numéricos; la resolución espacial es obligatoria para
   cualquier valor que no sea puntual.

### 5.1 Alternativas evaluadas

| Alternativa | Ventaja | Inconveniente | Decisión |
|---|---|---|---|
| A. Añadir columnas de procedencia a `beaches` | Migración mínima | No hay histórico; una fila por playa no puede guardar varias fuentes/instantes; sigue mezclando naturaleza | Descartada |
| B. Tabla `observations` con columnas tipadas + payload JSON | Flexible, portable, histórico | Requiere disciplina de validación; JSON puede ocultar errores | **Elegida** para el MVP |
| C. Tablas por variable | Tipado fuerte | Rígido; muchas tablas; migraciones por variable | Descartada para MVP |
| D. Solo envoltura en la respuesta | Sin migración | No auditable, no persistente | Descartada |

**Diseño elegido (conceptual)**: `observations` como tabla central con `variable_code`,
`value_num`, `value_bool`, `value_text`, `unit`, más `data_sources` y `variables` como
catálogos. No se usan ENUM nativos ni JSONB (portabilidad PostgreSQL/SQLite, coherencia con
ADR 0005). La validación de tipos se hace en la capa de dominio y en tests.

## 6. Estrategia para defaults heredados

No se propone un “big bang”. Fases:

1. **Medir** (sin cambiar esquema): inventariar cuántas filas tienen valores que solo pueden
   venir del default y cuántas tienen un valor con posible observación. Esto se hace con una
   consulta de auditoría y un informe, no con una migración.
2. **Añadir estado** (migración aditiva): `occupancy_status`, `jellyfish_status`,
   `sargasso_status`, `services_status` (o tabla de estados), `data_origin`
   (`seed/imported/observed/api`). Sin borrar columnas.
3. **Rellenar** con `unknown`/`synthetic` según la evidencia; nunca inventar fuente.
4. **Cambiar consumidores** para que lean el estado, no el valor bruto.
5. **Relajar defaults** (migración posterior): permitir `NULL` en las columnas heredadas y
   retirar los defaults de Python; la API mantiene compatibilidad con campos adicionales.
6. **Retirar** la columna antigua solo si se demuestra que no hay clientes que la usen; antes,
   mantenerla como “legacy”.

Compatibilidad: los clientes actuales siguen recibiendo `current_occupation` (entero), pero
también `occupancy_status` y `occupancy_observed_at`. Si el valor es desconocido, se propone
`current_occupation = null` en la nueva versión; para no romper, la fase 2 puede mantener `0`
con `occupancy_status = "unknown"` y documentar que el 0 no debe interpretarse. La decisión
final se tomará en el plan de implementación con pruebas de contrato.

## 7. Protocolo de validación de heurísticos

Objetivo: decidir si los heurísticos de ocupación y medusas se mantienen, se ajustan o se
retiran. Sin datos de referencia, no se declara exactitud.

### 7.1 Datos de referencia

- **Ocupación**: panel de Calvià (4 zonas, cada 15 min) y/o app del Consell / Gemelo Digital,
  previo convenio. Se necesita exportación histórica con hora y playa.
- **Medusas**: datos de socorrismo/MedusApp moderados, o registro oficial si existe. Sin esto,
  no se valida.
- **Meteo**: AEMET/SOCIB para las mismas horas (variables de entrada).

### 7.2 Diseño

- **Unidad**: playa-día-hora.
- **Ventana**: al menos una temporada completa (junio–septiembre); ideal dos.
- **Cobertura mínima**: 4 playas de Calvià con perfiles distintos; si se amplía, declarar
  selección y sesgo.
- **Partición**: entrenamiento/validación temporal (no aleatoria) para evitar fuga de futuro.
- **Línea base**: persistencia (la ocupación de la hora anterior) para ocupación; tasa base para
  medusas.
- **Métricas ocupación**: MAE, RMSE, sesgo, correlación; error por franja horaria y por playa.
- **Métricas medusas**: precisión, recall, F1, matriz de confusión; reportar prevalencia.
- **Missing**: excluir del cálculo y reportar cobertura; no imputar sin declararlo.
- **Umbral de aceptación**: se acuerda **antes** de ver resultados. Como mínimo, el heurístico
  debe superar la línea base; el margen concreto es una decisión de producto (Q-proto).
- **Reproducibilidad**: semilla fija si hay algún componente aleatorio (no debería), versión del
  método, hash del conjunto y script.

### 7.3 Salida

- Informe con métricas, cobertura, sesgo, limitaciones y decisión (mantener/ajustar/retirar).
- Si no se supera el umbral: el heurístico queda `validated=false`, no se usa como factor de
  recomendación y se muestra solo como informativo o se retira.
- Si se supera: se registra `ValidationRecord` y se puede usar con `confidence` solo si el
  método produce una medida calibrada.

## 8. Fuentes consultadas (URLs)

- Consell de Mallorca, app “Platges de Mallorca”:
  `https://www.conselldemallorca.es/totes-les-noticies/-/asset_publisher/bqOupoVYvgPA/content/platges-de-mallorca-una-aplicacio-per-obtenir-informacio-en-temps-real-de-l-ocupacio-i-les-condicions-de-banyplatges-de-mallorca-una-aplicacio-per-obtenir-informacio-en-temps-real-de-l-ocupacio-i-les-condicions-de-bany/695139`
- Govern, Gemelo Digital (nota oficial):
  `https://www.caib.es/pidip2front/jsp/es/ficha-convocatoria/el-govern-activa-el-gemelo-digital-de-turismo-para-mejorar-la-gestion-de-la-afluencia-en-las-playas-de-las-illes-balears`
- Govern, plataforma: `https://platges.illesbalears.travel/login?lang=es`
- Calvià, panel oficial:
  `https://www.calvia.com/ca/arees-municipals/playas-y-litoral/aforament-de-les-platges-en-temps-real`
- Calvià, noticia local (10 min; boyas futuras):
  `https://www.mallorcaaldia.com/ca/part-forana/calvia-monitoritza-platges-minut-a-minut-sensors-intel%C2%B7ligents/20260511143856004277.html`
- SOCIB API: `https://api.socib.es` · Swagger: `https://api.socib.es/swagger/` ·
  ejemplos: `https://github.com/socib/API_examples`
- SOCIB, términos: `https://www.socib.es/en/what-we-do/metocean-data/data-terms-of-use`
- AEMET OpenData: `https://opendata.aemet.es/centrodedescargas/info`
- Copernicus Marine, licencia:
  `https://marine.copernicus.eu/user-corner/service-commitments-and-licence`
- CAIB Open Data (CKAN): `https://intranet.caib.es/opendatacataleg/api/3/action/package_search?q=platges`
- Calidad de aguas de baño (Informe Mar Balear 2026):
  `https://www.informemarbalear.org/ca/platges/imb-qualitat-aigues-bany-cat_2026.pdf`
- MedusApp: `https://www.medusapp.net`

## 9. Integración con herramientas del entorno autorizado

| Herramienta | Capacidad real | Uso en SANDAM | Requisitos / límites |
|---|---|---|---|
| **RASPAL_SCRAPER** | Scraper configurable; comprueba `robots.txt`, `crawl-delay`, dominios sensibles; caché, throttle, extracción; dashboard web | Herramienta de ingesta para fuentes **con permiso**; no es una fuente | No concede licencia; hay que revisar ToS; no usarlo para eludir límites; no ejecutar en producción sin revisión |
| **ClimApp** | Ingesta AEMET por coordenadas; normalización; reintentos; validación; API Flask; almacenamiento SQLite/JSON | Reutilizar patrones de normalización/reintentos/validación para el adaptador AEMET | No es una fuente de ocupación; su modelo de datos es otro; no copiar datos sin trazabilidad |
| **GeoRisk_Finder** | Rejilla H3 resolución 3 (celdas muy grandes); clustering de riesgos sísmicos/ciclónicos/volcánicos; FastAPI | **No aplicable** a ocupación de playas | La resolución H3 no es de playa; no mezclar riesgos globales con seguridad de baño |
| **GeoRisk_Finder (variante)** | Preprocesado/visualización | Referencia metodológica, no datos | Sin relevancia directa |

## 10. Decisiones de investigación

- **D1**: La ocupación es un indicador de presión **relativa** y **no** un mérito. No entra en
  el scoring ni en el desempate.
- **D2**: `unknown` es un estado de primera clase; no se representa con 0/False.
- **D3**: Seed = `synthetic`; nunca `live`.
- **D4**: El contrato de observación separa naturaleza, validación y vigencia.
- **D5**: Migración aditiva y por fases; sin reconstruir tablas; sin borrar datos.
- **D6**: Solo fuentes con acceso y licencia verificados; el resto queda como investigación.
- **D7**: Los heurísticos no se presentan como exactos; `validated=false` y `confidence=null`
  hasta el protocolo.
- **D8**: Calvià es la referencia prioritaria para validar ocupación por su panel público cada
  15 minutos; el acceso a datos históricos requiere permiso.

## 11. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Confundir una web pública con una API autorizada | Alto (legal y de datos) | Registrar licencia y permiso; no raspar |
| El seed se usa en producción | Alto (veracidad) | `synthetic` + bloqueo en producción |
| La migración de defaults rompe clientes | Medio | Campos aditivos, fase de compatibilidad, tests de contrato |
| Datos de ocupación sesgados (solo playas turísticas) | Medio | Declarar cobertura y sesgo; no generalizar |
| Predicciones con apariencia de certeza | Alto | `validated=false`, `confidence=null`, sin uso como factor |
| Cambios de licencia | Medio | Registro de fuente y fecha de revisión; poder purgar |
| Duración/validez mal definidas | Medio | Regla por variable y fuente; tests con reloj inyectable |
