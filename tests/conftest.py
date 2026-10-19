"""Shared pytest fixtures.

Tests run against an in-memory SQLite database, so they do not require
PostgreSQL. `src.database` is patched before the app is imported.
"""

import os
import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import src.database as database  # noqa: E402
from src.models import Beach, DataStatus, FlagColor, WaterQuality, utcnow  # noqa: E402

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def db(session_factory):
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(session_factory, monkeypatch):
    from src.main import app

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[database.get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_beach(db):
    beach = Beach(
        id=uuid.uuid4(),
        name="Platja de Palma",
        region="Mallorca",
        latitude=39.5345,
        longitude=2.7175,
        max_capacity=20000,
        current_occupation=72,
        water_temp=26.5,
        air_temp=30.0,
        uv_index=8,
        wind_speed=8.0,
        wave_height=0.3,
        flag_color=FlagColor.green.value,
        water_quality=WaterQuality.excellent.value,
        jellyfish_present=False,
        sargasso_level=0,
        has_kiosk=True,
        has_shade=True,
        has_showers=True,
        has_parking=True,
        has_accessibility=True,
        has_lifeguard=True,
        data_status=DataStatus.live.value,
        created_at=utcnow(),
        last_updated=utcnow(),
    )
    db.add(beach)
    await db.commit()
    await db.refresh(beach)
    return beach
