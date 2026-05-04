from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database import init_db
from src.api import beaches, search, recommendations, dashboard
from src.schemas import HealthResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="SANDAM API",
    description="Smart Beach Management API - Gestión inteligente de playas",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(beaches.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow()
    }


@app.get("/health/ready")
async def readiness_check():
    return {"ready": True, "database": "connected"}


@app.get("/")
async def root():
    return {
        "message": "SANDAM API - Smart Beach Management",
        "version": "1.0.0",
        "docs": "/docs"
    }