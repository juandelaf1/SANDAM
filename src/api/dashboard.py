from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src import schemas
from src.deps import get_db
from src.models import Beach, FlagColor, WaterQuality

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=schemas.DashboardSummary)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count(Beach.id)))
    total_beaches = result.scalar() or 0

    result = await db.execute(
        select(func.avg(Beach.current_occupation))
    )
    avg_occupation = result.scalar() or 0

    quality_counts = {
        "excellent": 0,
        "good": 0,
        "sufficient": 0,
        "poor": 0,
        "unknown": 0
    }
    result = await db.execute(
        select(Beach.water_quality, func.count(Beach.id))
        .group_by(Beach.water_quality)
    )
    for quality, count in result.all():
        if quality:
            quality_counts[quality.value] = count

    flag_counts = {
        "green": 0,
        "yellow": 0,
        "red": 0,
        "unknown": 0
    }
    result = await db.execute(
        select(Beach.flag_color, func.count(Beach.id))
        .group_by(Beach.flag_color)
    )
    for flag, count in result.all():
        if flag:
            flag_counts[flag.value] = count

    active_alerts = flag_counts.get("red", 0)

    return {
        "total_beaches": total_beaches,
        "avg_occupation": round(float(avg_occupation), 1),
        "quality_distribution": quality_counts,
        "flag_distribution": flag_counts,
        "active_alerts": active_alerts,
        "last_updated": datetime.utcnow()
    }


@router.get("/alerts")
async def get_alerts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Beach).where(Beach.flag_color == FlagColor.red)
    )
    red_beaches = result.scalars().all()

    result = await db.execute(
        select(Beach).where(Beach.jellyfish_present == True)
    )
    jellyfish_beaches = result.scalars().all()

    alerts = []

    for beach in red_beaches:
        alerts.append({
            "beach_id": str(beach.id),
            "beach_name": beach.name,
            "alert_type": "danger",
            "message": "Bandera roja izgada",
            "timestamp": beach.last_updated.isoformat()
        })

    for beach in jellyfish_beaches:
        alerts.append({
            "beach_id": str(beach.id),
            "beach_name": beach.name,
            "alert_type": "warning",
            "message": f"Medusas detectadas{': ' + beach.jellyfish_species if beach.jellyfish_species else ''}",
            "timestamp": beach.last_updated.isoformat()
        })

    return {"alerts": alerts, "count": len(alerts)}


@router.get("/analytics/occupation")
async def get_occupation_analytics(
    region: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Beach.region, func.avg(Beach.current_occupation))
    if region:
        query = query.where(Beach.region == region)
    query = query.group_by(Beach.region)

    result = await db.execute(query)

    data = []
    for r, avg in result.all():
        data.append({"region": r, "avg_occupation": round(float(avg), 1)})

    return {"data": data}


@router.get("/analytics/quality")
async def get_quality_analytics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Beach.water_quality, func.count(Beach.id))
        .group_by(Beach.water_quality)
    )

    data = []
    for quality, count in result.all():
        if quality:
            data.append({"quality": quality.value, "count": count})

    return {"data": data}


@router.get("/analytics/safety")
async def get_safety_analytics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Beach.flag_color, func.count(Beach.id))
        .group_by(Beach.flag_color)
    )

    data = []
    for flag, count in result.all():
        if flag:
            data.append({"flag": flag.value, "count": count})

    return {"data": data}