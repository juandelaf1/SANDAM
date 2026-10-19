"""Database engine and session factory.

Schema management is owned by Alembic (see ``alembic/`` and
``docs/MIGRATIONS.md``). The application MUST NOT create or alter tables at
startup: migrations are an explicit, documented operator step. Tests, which run
against an in-memory SQLite database, create the schema explicitly through
``Base.metadata.create_all`` in ``tests/conftest.py``.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from src.config import get_settings

settings = get_settings()

_engine_kwargs = {"echo": settings.log_level == "DEBUG", "pool_pre_ping": True}
if not settings.database_url.startswith("sqlite"):
    _engine_kwargs.update(pool_size=10, max_overflow=20)

engine = create_async_engine(settings.database_url, **_engine_kwargs)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
