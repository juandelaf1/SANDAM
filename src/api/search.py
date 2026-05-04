from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src import schemas
from src.deps import get_db
from src.models import WaterQuality

router = APIRouter(prefix="/beaches", tags=["search"])


@router.get("/nearby", response_model=schemas.NearbyResponse)
async def get_beaches_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10, gt=0, le=100),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    beaches = await crud.get_beaches_nearby(db, lat, lon, radius_km, limit)
    return {
        "requested_lat": lat,
        "requested_lon": lon,
        "radius_km": radius_km,
        "beaches": beaches
    }


@router.get("/best-nearby")
async def get_best_beaches_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10, gt=0, le=100),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    beaches = await crud.get_best_beaches_nearby(db, lat, lon, radius_km, limit)
    return {
        "requested_lat": lat,
        "requested_lon": lon,
        "radius_km": radius_km,
        "beaches": beaches
    }


@router.get("/search", response_model=schemas.SearchResponse)
async def search_beach(
    name: Optional[str] = None,
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lon: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: float = Query(10, gt=0, le=100),
    max_occupation: Optional[int] = Query(None, ge=0, le=100),
    min_quality: Optional[WaterQuality] = None,
    avoid_jellyfish: bool = True,
    db: AsyncSession = Depends(get_db)
):
    if not name and not (lat and lon):
        return {"requested_beach": None, "recommendation": None}

    result = await crud.search_beach_with_alternatives(
        db, name, lat, lon, radius_km,
        max_occupation, min_quality, avoid_jellyfish
    )
    return result