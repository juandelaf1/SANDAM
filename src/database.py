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


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
