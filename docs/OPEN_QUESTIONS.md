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
