"""Alembic environment for SANDAM.

Design notes
------------
* The database URL is read from the application ``Settings`` (``DATABASE_URL``
  env var or ``.env``). It is **never** hardcoded here and **never** printed,
  so credentials do not leak into Alembic logs or reports.
* The application uses SQLAlchemy's async engine (asyncpg in production,
  aiosqlite in tests), so migrations run through an async connection and
  ``connection.run_sync``.
* Applying migrations is always an explicit operator step
  (``alembic upgrade head``); the FastAPI application never runs migrations on
  startup.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.config import get_settings
from src.database import Base
import src.models  # noqa: F401  # registers the ORM models on Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _database_url() -> str:
    """Return the configured database URL without exposing it in logs."""
    return get_settings().database_url


def run_migrations_offline() -> None:
    """Run migrations without a DB connection (SQL emitted to stdout)."""
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _database_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
