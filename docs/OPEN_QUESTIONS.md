# Decisiones pendientes (Open Questions)

Preguntas que **no** pueden resolverse de forma responsable con la información disponible hoy.
Cada una indica por qué bloquea algo, quién debe resolverla y qué evidencia se necesita.
Cuando se resuelva, se traslada a un ADR o a una especificación.

**Última revisión**: 2026-10-19

---

## Q1 — Metodología y fuentes de capacidad de acogida

- **Relacionada con**: FR-014, Restricciones de Producto, `TODO(CAPACITY_METHODOLOGY)`.
- **Bloquea**: usar cualquier umbral de capacidad en recomendaciones. Hoy `max_capacity` del seed
  es una cifra orientativa sin metodología.
- **Necesita**: identificar planes de gestión, estudios o normativa que definan capacidad ecológica
  / física / de acceso / de servicios por playa, o decidir explícitamente usar solo indicadores de
  presión **relativa** etiquetados.
- **Responsable**: producto (con apoyo de fuentes oficiales).

## Q2 — Fuente de aforo/ocupación en tiempo real

- **Relacionada con**: US1, presión turística.
- **Bloquea**: pasar de ocupación "del seed" a observación real. No hay fuente pública fiable
  confirmada para todas las playas de Mallorca.
- **Necesita**: investigación de fuentes legítimas (oficiales, contadores agregados, ocupación de
  aparcamientos) **y** revisión de condiciones de uso y privacidad antes de integrar cualquier
  fuente.
- **Prohibido**: incorporar cámaras o seguimiento individual como solución por defecto.

## Q3 — Cálculo real del tiempo de viaje

- **Relacionada con**: FR-013.
- **Bloquea**: presentar un tiempo de viaje como dato (hoy es Haversine × factor).
- **Necesita**: decidir si se integra un proveedor de rutas (con condiciones de uso y coste) o si se
  mantiene como **estimación etiquetada** de forma indefinida.

## Q4 — Condiciones de uso y licencias de las fuentes externas

- **Relacionada con**: Principio VIII, `TODO(DATA_SOURCES)`.
- **Bloquea**: integrar SOCIB, CAIB, Govern, platgesdebalears, MedusApp, UIB BeachCam en la app.
- **Necesita**: revisar términos, licencias, límites de uso y privacidad de cada fuente antes de
  usarla en producción. Hoy existen clientes en `src/integrations/` **no usados** por la app.

## Q5 — Rotación de la credencial SOCIB (SEGURIDAD)

- **Relacionada con**: Principio VIII, incidente de seguridad.
- **Estado**: la credencial aparece en el **historial de git** (no en el árbol actual ni en `.env`).
  Debe tratarse como comprometida.
- **Bloquea**: no bloquea el desarrollo, pero es prioritario.
- **Necesita**: **rotar/revocar la clave** en el proveedor (acción del propietario; el agente no
  puede hacerlo) y, opcionalmente, purgar el historial (`git filter-repo`/BFG) — reescritura
  destructiva que requiere decisión explícita. No copiar el valor a ningún archivo.
- **Responsable**: propietario del repositorio.

## Q6 — Gestión de los prototipos del repositorio

- **Relacionada con**: limpieza.
- **Bloquea**: no bloquea; se decidió **no** limpiar en la fase SDD actual.
- **Necesita**: decidir el destino de 12 dashboards (`notebooks/`), 25+ scripts de test y 13+
  scripts `debug_*` de la raíz (todos sin versionar). Opciones: archivar, borrar o convertir en
  tests reales. Fuera del alcance de la spec 001.

## Q7 — Plataforma de despliegue

- **Relacionada con**: ADR 0004 (Propuesta).
- **Bloquea**: un MVP desplegado y verificable.
- **Necesita**: comparar contenedor + PostgreSQL gestionado (recomendado) frente a Cloudflare
  Workers, con una **prueba técnica** de compatibilidad de dependencias si se considera Workers.

## Q8 — Política de reconciliación de fuentes contradictorias

- **Relacionada con**: FR-015, edge case de contradicción.
- **Bloquea**: definir qué valor prevalece cuando dos fuentes discrepan.
- **Necesita**: definir prioridad de fuentes y regla temporal (más reciente vs más autoritativa).

## Q9 — Alcance futuro (autenticación, notificaciones, multi-región)

- **Relacionada con**: Restricciones de Producto.
- **Bloquea**: nada inmediato; explícitamente fuera del MVP.
- **Necesita**: especificación propia antes de implementar cualquier elemento.

## Q10 — Catálogos documentados de protección y vulnerabilidad

- **Relacionada con**: T004 (`protection_status`, `vulnerability_level`), FR-007, ADR 0005.
- **Bloquea**: asignar valores a `protection_status` y `vulnerability_level`: hoy no existe una
  clasificación documentada (figuras de protección, sensibilidad ecológica, niveles de
  vulnerabilidad) con la que poblarlas sin inventar. Las columnas se dejan `NULL` = desconocido.
- **Necesita**: identificar las figuras/niveles aplicables y su fuente (planes de gestión,
  normativa, cartografía de posidonia, etc.) y decidir si se modelan como catálogo cerrado
  (entonces habría que valorar `ENUM` y su migración).
- **Responsable**: producto (con apoyo de fuentes oficiales).
- **Nota**: `capacity_reference` y `capacity_method` dependen de Q1; `access_restrictions` describe
  restricciones **documentadas**, no su vigencia en tiempo real (esa verificación requiere el
  modelo de observaciones y una fuente oficial, Q2/Q4).

---

## Preguntas estratégicas (revisión del Product Blueprint 0.1, 2026-10-19)

Preguntas que el
[`PRODUCT_BLUEPRINT.md`](PRODUCT_BLUEPRINT.md) revela y que **todavía no** pueden resolverse con la
información disponible. Cada una indica **qué necesitamos saber**, **por qué afecta al producto**,
**qué evidencia la resolvería**, **si bloquea** alguna tarea, **cuándo** conviene resolverla y **qué
decisión temporal es segura** mientras siga abierta. No convierten una incertidumbre en una decisión
técnica arbitraria.

### Datos

#### Q11 — Metadatos y procedencia de cada fuente
- **Qué necesitamos saber**: para cada fuente futura, qué variable mide, con qué unidad, resolución
  espacial/temporal, retraso, caducidad y estado de validación.
- **Por qué afecta**: sin esto no puede cumplirse la trazabilidad (FR-015) ni la clasificación del
  dato (FR-004); un dato sin contexto se confundiría con una observación precisa.
- **Evidencia que la resuelve**: ficha por fuente (acceso, licencia, resolución, frecuencia,
  limitaciones) + una muestra real verificada.
- **Bloquea**: la integración de cualquier fuente (Fase B en adelante). **No** bloquea el MVP de la
  spec 001.
- **Cuándo**: Fase B (viabilidad de datos).
- **Decisión temporal segura**: usar solo datos ya etiquetados manualmente en el modelo; no exponer
  valores de fuente no verificada.

#### Q12 — Persistencia histórica necesaria para medir impacto
- **Qué necesitamos saber**: qué debe persistirse (recomendaciones emitidas por destino y franja,
  observaciones con su caducidad) para poder evaluar efectos, y qué puede ser efímero.
- **Por qué afecta**: sin histórico no se puede evaluar si SANDAM mejora o traslada la presión
  (§16.3 del blueprint); con demasiado histórico se retiene dato innecesario (Principio VIII).
- **Evidencia que la resuelve**: definir las métricas de §16 y derivar de ellas el mínimo
  imprescindible, agregado y sin ubicaciones individuales.
- **Bloquea**: la evaluación de impacto (Fase F). **No** bloquea el MVP.
- **Cuándo**: antes de la Fase F; revisar junto con privacidad (Q22).
- **Decisión temporal segura**: no persistir ubicaciones individuales; registrar solo agregados
  anónimos si llega a hacerse.

#### Q26 — Distinguir "servicio no disponible" de "servicio no documentado"
- **Qué necesitamos saber**: cómo representar en el modelo que un servicio (socorrista, sombra,
  aparcamiento, ducha, kiosco, accesibilidad) **no consta**, frente a "consta que no lo hay".
- **Por qué afecta**: los seis campos son `Boolean` con `default=False` tanto en el ORM
  (`src/models.py`) como en `BeachBase` (`src/schemas.py`), y la columna admite `NULL`. Un `False`
  puede significar **ausencia confirmada** o **dato no documentado**, y el modelo no los distingue.
  Puntuarlos trataría un valor por defecto como una observación verificada (FR-003) y haría que la
  comparación favoreciera o penalizara a una playa según su grado de documentación.
- **Evidencia que la resuelve**: decidir si los campos pasan a `NULL` cuando no consta (con `False`
  solo cuando la ausencia esté documentada) o si se añade un indicador de procedencia por servicio; y
  confirmar con qué fuente se documenta la ausencia.
- **Bloquea**: volver a puntuar los servicios en el score canónico. **No** bloquea el MVP: desde la
  auditoría de T006 el factor `services` **no** se puntúa ni cuenta para `coverage`
  (`research.md` §D2-ter). Los seis valores siguen exponiéndose tal cual en la respuesta, sin
  presentarlos como verificados.
- **Cuándo**: al definir la trazabilidad de cada campo (FR-015), en Fase B.
- **Decisión temporal segura**: no puntuar los servicios; registrar la limitación y no presentar el
  valor por defecto como una ausencia confirmada. Criterio de reintegración: solo si el modelo
  expresa de forma explícita la ausencia documentada (o existe procedencia por servicio).

#### Q27 — Valores por defecto del modelo indistinguibles de observaciones
- **Qué necesitamos saber**: qué campos deben ser `NULL`/desconocidos cuando nadie ha observado un
  valor, y cómo se registra su procedencia. Hoy conviven dos comportamientos: `flag_color` y
  `water_quality` usan `unknown` por defecto (sí expresan desconocido), mientras que
  `current_occupation` (`default=0`), `has_*` (`default=False`), `sargasso_level` (`default=0`) y
  `jellyfish_present` (`default=False`) producen un valor concreto que nadie ha observado.
- **Por qué afecta**: FR-003 (la ausencia de datos no equivale a una condición favorable),
  FR-004 (clasificar cada valor) y FR-015 (procedencia). Un `0` de ocupación por defecto se presenta
  igual que una observación real de 0 %, de modo que el indicador de presión relativa —y el campo
  `ocupacion` de la respuesta— podrían reflejar un valor no observado; del mismo modo, un `False` por
  defecto se lee como un hecho.
- **Evidencia que la resuelve**: ficha de procedencia por campo (quién lo observa, con qué método,
  con qué caducidad) y decisión explícita de modelo (`NULL` por defecto frente a valor por defecto
  documentado), con la migración correspondiente.
- **Bloquea**: ponderar la ocupación y etiquetar cada valor con su naturaleza real. **No** bloquea el
  MVP: desde la auditoría de T006 el score canónico no pondera la ocupación (`research.md` §D2-ter).
- **Cuándo**: junto con la trazabilidad (FR-015) y el etiquetado de valores (FR-004), en Fase B.
- **Decisión temporal segura**: no ponderar la ocupación; no presentar los indicadores derivados como
  mediciones verificadas y etiquetar como estimación lo que proceda.

#### Q28 — Validación de los métodos heurísticos de estimación
- **Qué necesitamos saber**: si los dos métodos heurísticos que quedan tras T008 — ocupación
  (`heuristic_hour_day_weather_v1`) y medusas (`heuristic_wind_tide_temperature_v1`) — son aceptables
  para uso público, o hay que sustituirlos o retirarlos.
- **Por qué afecta**: son **deterministas** y están etiquetados (`nature: "prediction"`,
  `method`, `validated: false`, `confidence: null`), pero **no están contrastados**: sus constantes
  (factores horarios/día, prior base de medusas 0.1/0.7, umbrales de viento y temperatura) no tienen
  fuente empírica en el repositorio. FR-005 admite etiquetar como predicción un método definido, pero
  eso no acredita que el resultado sea correcto.
- **Evidencia que la resuelve**: serie de observaciones reales por playa y franja horaria frente a las
  estimaciones (error, sesgo, calibración) más una ficha de método con fuente, supuestos y límites.
- **Bloquea**: presentar estas estimaciones con confianza o usarlas para decidir en producción.
  **No** bloquea el MVP: se exponen etiquetadas como predicción **no validada**, sin nivel de
  confianza.
- **Cuándo**: Fase B/C, junto con la integración de fuentes reales.
- **Decisión temporal segura**: mantenerlas etiquetadas y sin `confidence`; **no** sustituir el código
  aleatorio retirado por otra predicción inventada; no presentarlas nunca como observaciones.

### Fuentes y permisos

#### Q13 — Condiciones de uso de las fuentes públicas de ocupación
- **Qué necesitamos saber**: licencia, atribución, frecuencia, cobertura y límites de reutilización
  de las fuentes de ocupación (Calvià DTI, estimación UIB por cámaras, futuras oficiales).
- **Por qué afecta**: reutilizar sin base legítima compromete el producto y puede violar Principio
  VIII; además, fuentes distintas miden magnitudes distintas (no intercambiables).
- **Evidencia que la resuelve**: condiciones de uso publicadas o contacto con el organismo;
  confirmación de si existe API y con qué límites.
- **Bloquea**: la Fase B y el piloto. **No** bloquea el MVP.
- **Cuándo**: Fase B.
- **Decisión temporal segura**: tratar esas fuentes como **no disponibles** hasta verificar permisos;
  no raspado para eludir autenticación o límites.

### Capacidad ambiental

#### Q14 — Clasificación de vulnerabilidad de la **zona receptora**
- **Qué necesitamos saber**: cómo determinar que un destino que recibe visitantes no es más frágil ni
  tiene accesos insuficientes (regla anti-traslado, §9.4 del blueprint).
- **Por qué afecta**: el riesgo central del producto es resolver la saturación de un lugar
  empeorando otro; sin esto, la regla anti-traslado no es verificable.
- **Evidencia que la resuelve**: catálogo de vulnerabilidad (relacionado con Q10) + datos de acceso
  y capacidad del destino receptor.
- **Bloquea**: la evaluación de efectos colectivos (Fase E). **No** bloquea el MVP.
- **Cuándo**: antes de la Fase E.
- **Decisión temporal segura**: si falta el dato, **no** promover una alternativa solo por baja
  afluencia (FR-007) y declararlo.

### Aforo

#### Q15 — Tratamiento de fuentes de aforo heterogéneas
- **Qué necesitamos saber**: cómo combinar o distinguir fuentes con cobertura, retraso y precisión
  diferentes sin presentarlas como una misma magnitud.
- **Por qué afecta**: una cifra agregada que oculte incertidumbre significativa induce decisiones
  erróneas (§13 del blueprint).
- **Evidencia que la resuelve**: comparar fuentes sobre playas comunes y cuantificar la discrepancia;
  política de reconciliación (relacionada con Q8).
- **Bloquea**: pasar de "presión relativa etiquetada" a presión observada por playa.
- **Cuándo**: Fase B/D.
- **Decisión temporal segura**: mantener indicadores **relativos** etiquetados; nunca como umbral
  oficial (FR-014).

### Movilidad

#### Q16 — Proveedor de rutas/tráfico y su incertidumbre
- **Qué necesitamos saber**: si se integra un proveedor de ETA con tráfico y con qué condiciones de
  uso y coste, o si se mantiene la estimación etiquetada (Haversine × factor).
- **Por qué afecta**: el ETA es una entrada central para elegir destino y calcular tiempo útil
  (§7.1); su error afecta directamente a la utilidad.
- **Evidencia que la resuelve**: prueba técnica con recorridos reales en Mallorca (muestra) y
  comparación con tiempos observados.
- **Bloquea**: la Fase D. **No** bloquea el MVP (que degrada a estimación etiquetada).
- **Cuándo**: Fase D.
- **Decisión temporal segura**: presentar siempre `travel_time_is_estimate: true` y no atribuir
  precisión de ruta a una distancia geodésica (FR-013).

### Clima

#### Q17 — Índice de confort térmico: variables, fuente y método
- **Qué necesitamos saber**: qué índice (si alguno) usar, con qué variables de entrada, qué fuente
  y qué limitaciones declaradas.
- **Por qué afecta**: no se puede implementar un índice "de confort" sin definirlo; presentar una
  estimación como valoración médica sería engañoso (§8.2).
- **Evidencia que la resuelve**: fijar variables imprescindibles por actividad, su disponibilidad y
  el método de cálculo con su incertidumbre.
- **Bloquea**: la Fase D (confort). **No** bloquea el MVP.
- **Cuándo**: Fase D.
- **Decisión temporal segura**: no mostrar índice de confort; mostrar solo variables meteorológicas
  etiquetadas como observación/estimación.

### Reportes comunitarios

#### Q18 — Política de caducidad, credibilidad y anti-manipulación
- **Qué necesitamos saber**: caducidad por categoría de reporte, nivel de confianza, tratamiento de
  duplicados/contradicciones y condición para que un reporte afecte a una recomendación.
- **Por qué afecta**: un reporte anónimo **no** debe adquirir autoridad de un cierre oficial (§10.1);
  sin política, el sistema se vuelve manipulable.
- **Evidencia que la resuelve**: definir categorías y reglas; probar con escenarios de contradicción
  y de manipulación.
- **Bloquea**: la incorporación de reportes a la decisión. **No** bloquea el MVP.
- **Cuándo**: tras el MVP de 001, antes de usar reportes en recomendaciones.
- **Decisión temporal segura**: no permitir que un reporte excluya ni promueva por sí solo una playa.

### Interoperabilidad del portfolio

#### Q19 — Modo de integración real de Raspal/Climapp/GeoRisk
- **Qué necesitamos saber**: si se integran como servicio, como biblioteca o solo como *know-how*;
  qué datos intercambian y con qué contrato.
- **Por qué afecta**: integrar "para demostrar conexión" viola el espíritu del Principio IX; compartir
  BD o módulos internos por conveniencia tiene consecuencias (acoplamiento, seguridad).
- **Evidencia que la resuelve**: prototipo de contrato de observación con una fuente real
  (p. ej. ingestión de una página o normalización climática) y evaluación de coste.
- **Bloquea**: nada del MVP; habilita Fases B–E.
- **Cuándo**: Fase B.
- **Decisión temporal segura**: no integrar aún; documentar el *know-how* (H3/clustering de GeoRisk,
  validación climática de Climapp, ingestión de Raspal) y no compartir bases de datos.

### Arquitectura

#### Q20 — Necesidades reales de partición espacial y clustering
- **Qué necesitamos saber**: si la escala de playa exige una partición (H3 u otra) y si el clustering
  aporta valor con los datos reales disponibles.
- **Por qué afecta**: elegir tecnología sin datos es prematuro (§36); H3 res 3 (usada en GeoRisk)
  es demasiado gruesa para playa.
- **Evidencia que la resuelve**: comparación empírica con datos de prueba y criterios explícitos
  (precisión, escala, explicabilidad, representación de accesos).
- **Bloquea**: la Fase E. **No** bloquea el MVP.
- **Cuándo**: Fase E.
- **Decisión temporal segura**: no añadir dependencias geoespaciales; usar coordenadas y Haversine
  como hoy.

#### Q21 — Persistencia de decisiones y contrato del panel de gestión
- **Qué necesitamos saber**: qué expone el panel de gestores y con qué contrato de solo lectura, sin
  convertirlo en una segunda fuente de verdad.
- **Por qué afecta**: un núcleo y dos interfaces exigen definiciones compartidas de presión,
  elegibilidad y calidad del dato (§12 del blueprint).
- **Evidencia que la resuelve**: un gestor real interesado + definición del mínimo panel útil.
- **Bloquea**: el panel (Fase F). **No** bloquea el MVP.
- **Cuándo**: Fase F, con socio.
- **Decisión temporal segura**: no construir panel; la interfaz visitante consume el mismo núcleo.

### Privacidad

#### Q22 — Estimación por cámaras y minimización de datos
- **Qué necesitamos saber**: si consumir estimaciones agregadas de ocupación derivadas de cámaras
  (p. ej. UIB) es compatible con el Principio VIII y con qué salvaguardas.
- **Por qué afecta**: el Principio VIII prohíbe soluciones intrusivas por defecto; consumir un
  **agregado** externo es distinto de desplegar seguimiento propio, pero debe justificarse.
- **Evidencia que la resuelve**: confirmar que la fuente publica solo agregados, sus condiciones de
  uso y que SANDAM no conserva imágenes ni datos personales.
- **Bloquea**: la Fase B (fuentes de aforo). **No** bloquea el MVP.
- **Cuándo**: Fase B, junto con Q13.
- **Decisión temporal segura**: no usar cámaras propias; no almacenar ubicaciones individuales.

### Modelo de negocio

#### Q23 — Disposición a pagar y problema operativo del gestor
- **Qué necesitamos saber**: si un ayuntamiento/gestor valora y pagaría por el panel y por qué
  problema concreto (distribución entre destinos, accesos saturados, evaluación de intervenciones).
- **Por qué afecta**: la finalidad ambiental no garantiza viabilidad (§15 del blueprint); sin
  validación no se diseñan precios.
- **Evidencia que la resuelve**: entrevistas con 1–3 gestores + un prototipo del mínimo útil.
- **Bloquea**: el modelo de negocio (Fase G). **No** bloquea el MVP ni el piloto.
- **Cuándo**: Fase F/G.
- **Decisión temporal segura**: no fijar precios ni planes; mantener la recomendación libre de
  influencia comercial (§15.3).

### Evaluación del impacto

#### Q24 — Método para no confundir correlación con causalidad
- **Qué necesitamos saber**: qué diseño de evaluación permitiría atribuir cambios de presión a
  SANDAM y no a factores externos.
- **Por qué afecta**: prometer reducción de presión sin método es marketing, no producto (§16).
- **Evidencia que la resuelve**: diseño cuasi-experimental en el piloto (zonas/franjas de control)
  y métricas de §16.
- **Bloquea**: las afirmaciones de impacto (Fase F). **No** bloquea el MVP.
- **Cuándo**: Fase F, antes de comunicar resultados.
- **Decisión temporal segura**: no afirmar reducción de turistificación; hablar de **hipótesis de
  impacto a medir**.

#### Q25 — Criterios de entrada/salida y elección definitiva del piloto
- **Qué necesitamos saber**: si Calvià (u otro ámbito) cumple cobertura, reutilización permitida y
  datos suficientes, y cuándo ampliar.
- **Por qué afecta**: un modelo validado en pocas playas no se extrapola a toda Mallorca (§17.2).
- **Evidencia que la resuelve**: verificación de las fuentes en el ámbito candidato + un colaborador.
- **Bloquea**: la Fase F. **No** bloquea el MVP.
- **Cuándo**: Fase B/F.
- **Decisión temporal segura**: no declarar elegido ningún ámbito hasta verificar datos y permisos.
