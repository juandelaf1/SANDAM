# AGENTS.md — Reglas operativas para agentes en SANDAM

Este archivo contiene **reglas operativas** para agentes que trabajen en este repositorio.
No duplica la visión del producto ni los principios: la autoridad son
[`docs/PRODUCT_VISION.md`](docs/PRODUCT_VISION.md) (visión y alcance) y
[`.specify/memory/constitution.md`](.specify/memory/constitution.md) (principios y gobernanza).
Las especificaciones viven en `specs/`.

---

## 1. Qué es SANDAM y ámbito actual

- SANDAM es una plataforma de información y apoyo a la decisión que ayuda a **distribuir mejor
  la demanda turística** en el litoral dentro de límites ambientales, de seguridad y operativos
  razonables. No es una app para llenar más playas.
- **Ámbito geográfico inicial: Mallorca (Illes Balears).** No ampliar a Cataluña, Valencia,
  Andalucía ni al resto de Baleares sin una especificación y una decisión explícita
  (ver `docs/adr/0001-ambito-mallorca.md`).

## 2. Jerarquía de prioridades (no negociable)

1. Protección ambiental y seguridad.
2. Reducción de la presión turística.
3. Calidad de la experiencia (visitantes y residentes).
4. Conveniencia individual.

Las restricciones de seguridad o ambientales actúan como **condiciones de exclusión**: ninguna
ventaja de comodidad puede compensarlas. Detalle y consecuencias en la constitución.

## 3. Arquitectura real y límites entre capas

- `src/main.py` — app FastAPI, routers, `/health` y `/health/ready`.
- `src/api/*` — routers (transporte HTTP). Sin lógica de dominio relevante.
- `src/crud.py` — acceso a datos.
- `src/models.py` / `src/schemas.py` — modelo de datos y contratos Pydantic.
- `src/utils/*` — lógica de dominio (scoring, distancia, recomendación).
- `src/integrations/*` — clientes de fuentes externas.
- `src/config.py` — configuración vía `Settings` (pydantic-settings).

Reglas de capa: `src/utils` no accede a la base de datos ni a la red; `src/crud` no conoce HTTP.

## 4. Comandos verificados

Ejecutados y comprobados en este repositorio (Windows PowerShell, Python 3.13, ver `README.md`):

- **Tests**: `pytest` — usan SQLite en memoria (`sqlite+aiosqlite:///:memory:`), no requieren PostgreSQL.
- **Lint**: `ruff check src tests seed_data.py`.
- **Arrancar la API**: `uvicorn src.main:app --reload` — `http://localhost:8000`, docs en `/docs`.
- **Docker (API + PostgreSQL)**: `docker compose up --build -d` y `docker compose exec api python seed_data.py`.

## 5. Desarrollo guiado por especificaciones (SDD)

- Todo cambio funcional relevante pasa por una especificación en `specs/NNN-<nombre>/`.
- Flujo: `constitution` (una vez) → `specify` → `clarify` → `plan` → `tasks` → `analyze` →
  `implement` → `converge`.
- Los comandos Spec Kit están en `.opencode/commands/` y se invocan como `/speckit.<comando>`.
- No implementar una funcionalidad funcional relevante sin una spec aprobada.

## 6. Convenciones de código

- Python 3.11+, tipado, Pydantic v2, `async/await` en rutas.
- Respetar la estructura, nombres y estilo existentes.
- Los cambios de comportamiento deben ir acompañados de tests.

## 7. Política de secretos y privacidad

- **Nunca** escribir secretos en código, docs, tests, logs, informes ni mensajes de commit.
- Las claves se leen de variables de entorno vía `Settings`; los ejemplos van vacíos en `.env.example`.
- No imprimir el valor de un secreto, ni siquiera en tareas de diagnóstico.
- Minimización de datos personales, agregación y no almacenar ubicaciones individuales.
- Estado de la credencial SOCIB: ver `docs/OPEN_QUESTIONS.md` (rotación pendiente del propietario).

## 8. Migraciones y cambios de esquema

- Todo cambio de esquema exige una **migración explícita y reproducible** (ver
  `docs/adr/0003-migraciones-alembic.md`).
- Las migraciones deben poder revertirse. No usar `create_all()` como sustituto de una migración.
- Mientras Alembic no esté operativo, **no introducir cambios de esquema**: documentarlos.

## 9. Cambios en la API

- Preservar el contrato existente. Un cambio incompatible debe justificarse y documentarse en
  `specs/NNN-*/contracts/`.
- Los endpoints deben declarar `response_model` cuando sea posible.

## 10. Veracidad del dato (obligatorio)

- Prohibido presentar datos simulados, aleatorios o procedentes del seed como observaciones
  reales.
- Etiquetar cada valor relevante como: **observación / estimación / predicción / caducado /
  desconocido**.
- La ausencia de datos **no** equivale a una condición favorable.
- Prohibido usar `random` (o equivalentes) en rutas que devuelvan lo que parezca un dato real.

## 11. Registro de excepciones

- Cualquier excepción a la constitución se registra como ADR en `docs/adr/` (contexto,
  justificación, consecuencias y plan de reversión).
