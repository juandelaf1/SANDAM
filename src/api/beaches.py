from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src import schemas
from src.deps import get_db
from src.models import FlagColor, WaterQuality

router = APIRouter(prefix="/beaches", tags=["beaches"])


@router.post("/", response_model=schemas.BeachResponse, status_code=status.HTTP_201_CREATED)
async def create_beach(
    beach_data: schemas.BeachCreate,
    db: AsyncSession = Depends(get_db)
):
    beach = await crud.create_beach(db, beach_data)
    return beach


@router.get("/", response_model=schemas.BeachListResponse)
async def list_beaches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    region: Optional[str] = None,
    flag_color: Optional[FlagColor] = None,
    water_quality: Optional[WaterQuality] = None,
    has_lifeguard: Optional[bool] = None,
    has_shade: Optional[bool] = None,
    occupation_min: Optional[int] = Query(None, ge=0, le=100),
    occupation_max: Optional[int] = Query(None, ge=0, le=100),
    db: AsyncSession = Depends(get_db)
):
    beaches = await crud.get_beaches(
        db, skip, limit, region, flag_color, water_quality,
        has_lifeguard, has_shade, occupation_min, occupation_max
    )
    total = await crud.get_beaches_count(
        db, region, flag_color, water_quality
    )
    return {"total": total, "beaches": beaches}


@router.get("/{beach_id}", response_model=schemas.BeachResponse)
async def get_beach(
    beach_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    beach = await crud.get_beach(db, beach_id)
    if not beach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beach not found"
        )
    return beach


@router.put("/{beach_id}", response_model=schemas.BeachResponse)
async def update_beach(
    beach_id: UUID,
    beach_data: schemas.BeachUpdate,
    db: AsyncSession = Depends(get_db)
):
    beach = await crud.get_beach(db, beach_id)
    if not beach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beach not found"
        )
    beach = await crud.update_beach(db, beach, beach_data)
    return beach


@router.delete("/{beach_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_beach(
    beach_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    beach = await crud.get_beach(db, beach_id)
    if not beach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beach not found"
        )
    await crud.delete_beach(db, beach)