import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database import init_db
from src.api import (
    beaches,
    search,
    recommendations,
    dashboard,
    weather,
    external_data,
    predictions,
    donde_ir,
    scraper_endpoints,
)
from src.models import utcnow
from src.schemas import HealthResponse

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as exc:
        # Keep the API available in degraded mode (health/ready reports the DB state).
        logger.warning("Database initialisation failed; starting in degraded mode: %s", exc)
    yield


app = FastAPI(
    title="SANDAM API",
    description="Smart Beach Management API - Gestión inteligente de playas",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=settings.allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/v1")
app.include_router(beaches.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(external_data.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(donde_ir.router, prefix="/api/v1")
app.include_router(scraper_endpoints.router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": utcnow(),
    }


@app.get("/health/ready")
async def readiness_check():
    from sqlalchemy import text

    from src.database import engine

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        return {"ready": False, "database": "unavailable", "detail": str(exc)}
    return {"ready": True, "database": "connected"}


@app.get("/")
async def root():
    return {
        "message": "SANDAM API - Smart Beach Management",
        "version": "1.0.0",
        "docs": "/docs",
    }
