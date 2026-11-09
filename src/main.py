import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database import engine
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
    # The schema is managed by Alembic (see docs/MIGRATIONS.md). The application
    # never creates tables at startup; migrations are an explicit operator step.
    # We only probe connectivity so an unavailable database is visible in the
    # logs (degraded mode); /health/ready reports it too.
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("Database unavailable; starting in degraded mode: %s", exc)
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


from fastapi import Request


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    if os.getenv("SANDAM_HSTS", "").lower() == "true":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "contract_version": "sandam-api/0.1",
        "timestamp": utcnow(),
        "capabilities": {
            "openapi": "/docs",
            "recommendations": "experimental",
            "capacity_verified": False,
            "occupancy_realtime_verified": False,
            "provenance_required": True,
        },
    }


@app.get("/health/ready")
async def readiness_check():
    from sqlalchemy import text

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
