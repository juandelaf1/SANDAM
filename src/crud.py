from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Beach, FlagColor, WaterQuality, DataStatus
from src.schemas import BeachCreate, BeachUpdate
from src.utils.distance import haversine_distance, sort_by_distance
from src.utils.scoring import calculate_overall_score


async def create_beach(db: AsyncSession, beach_data: BeachCreate) -> Beach:
    beach = Beach(**beach_data.model_dump())
    beach.data_status = DataStatus.live
    db.add(beach)
    await db.commit()
    await db.refresh(beach)
    return beach


async def get_beach(db: AsyncSession, beach_id: UUID) -> Optional[Beach]:
    result = await db.execute(select(Beach).where(Beach.id == beach_id))
    return result.scalar_one_or_none()


async def get_beaches(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    region: Optional[str] = None,
    flag_color: Optional[FlagColor] = None,
    water_quality: Optional[WaterQuality] = None,
    has_lifeguard: Optional[bool] = None,
    has_shade: Optional[bool] = None,
    occupation_min: Optional[int] = None,
    occupation_max: Optional[int] = None,
) -> List[Beach]:
    query = select(Beach)

    filters = []
    if region:
        filters.append(Beach.region == region)
    if flag_color:
        filters.append(Beach.flag_color == flag_color)
    if water_quality:
        filters.append(Beach.water_quality == water_quality)
    if has_lifeguard is not None:
        filters.append(Beach.has_lifeguard == has_lifeguard)
    if has_shade is not None:
        filters.append(Beach.has_shade == has_shade)
    if occupation_min is not None:
        filters.append(Beach.current_occupation >= occupation_min)
    if occupation_max is not None:
        filters.append(Beach.current_occupation <= occupation_max)

    if filters:
        query = query.where(and_(*filters))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_beaches_count(
    db: AsyncSession,
    region: Optional[str] = None,
    flag_color: Optional[FlagColor] = None,
    water_quality: Optional[WaterQuality] = None,
) -> int:
    query = select(Beach)

    filters = []
    if region:
        filters.append(Beach.region == region)
    if flag_color:
        filters.append(Beach.flag_color == flag_color)
    if water_quality:
        filters.append(Beach.water_quality == water_quality)

    if filters:
        query = query.where(and_(*filters))

    result = await db.execute(query)
    return len(result.scalars().all())


async def update_beach(db: AsyncSession, beach: Beach, beach_data: BeachUpdate) -> Beach:
    update_data = beach_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(beach, field, value)

    beach.last_updated = datetime.utcnow()
    await db.commit()
    await db.refresh(beach)
    return beach


async def delete_beach(db: AsyncSession, beach: Beach) -> None:
    await db.delete(beach)
    await db.commit()


async def get_beaches_nearby(
    db: AsyncSession,
    lat: float,
    lon: float,
    radius_km: float = 10,
    limit: int = 10
) -> List[dict]:
    beaches = await get_beaches(db, limit=500)

    nearby = []
    for beach in beaches:
        distance = haversine_distance(lat, lon, beach.latitude, beach.longitude)
        if distance <= radius_km:
            beach_dict = {
                "id": beach.id,
                "name": beach.name,
                "region": beach.region,
                "latitude": beach.latitude,
                "longitude": beach.longitude,
                "current_occupation": beach.current_occupation,
                "flag_color": beach.flag_color,
                "water_quality": beach.water_quality,
                "has_lifeguard": beach.has_lifeguard,
                "distance_km": round(distance, 2)
            }
            nearby.append(beach_dict)

    return sorted(nearby, key=lambda x: x["distance_km"])[:limit]


async def get_best_beaches_nearby(
    db: AsyncSession,
    lat: float,
    lon: float,
    radius_km: float = 10,
    limit: int = 5
) -> List[dict]:
    beaches = await get_beaches_nearby(db, lat, lon, radius_km, limit=50)

    for beach in beaches:
        beach["score"] = calculate_overall_score(beach)

    return sorted(beaches, key=lambda x: x.get("score", 0), reverse=True)[:limit]


async def search_beach_with_alternatives(
    db: AsyncSession,
    name: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: float = 10,
    max_occupation: Optional[int] = None,
    min_quality: Optional[WaterQuality] = None,
    avoid_jellyfish: bool = True
) -> dict:
    if name:
        result = await db.execute(
            select(Beach).where(Beach.name.ilike(f"%{name}%")).limit(1)
        )
        beach = result.scalar_one_or_none()
    elif lat and lon:
        nearby = await get_beaches_nearby(db, lat, lon, radius_km, limit=1)
        beach = await get_beach(db, nearby[0]["id"]) if nearby else None
    else:
        return {"requested_beach": None, "recommendation": None}

    if not beach:
        all_beaches = await get_beaches(db, limit=20)
        return {
            "requested_beach": None,
            "recommendation": {
                "reason": "No se encontró la playa especificada",
                "alternatives": [
                    {
                        "beach": b,
                        "distance_km": haversine_distance(lat or 0, lon or 0, b.latitude, b.longitude) if lat and lon else 0,
                        "score": calculate_overall_score(b),
                        "improvements": ["Nueva opción"]
                    }
                    for b in all_beaches[:5]
                ]
            }
        }

    beach_dict = {
        "id": beach.id,
        "name": beach.name,
        "region": beach.region,
        "latitude": beach.latitude,
        "longitude": beach.longitude,
        "current_occupation": beach.current_occupation,
        "flag_color": beach.flag_color,
        "water_quality": beach.water_quality,
        "jellyfish_present": beach.jellyfish_present
    }

    problems = []
    if beach.current_occupation and max_occupation and beach.current_occupation > max_occupation:
        problems.append(f"Ocupación alta ({beach.current_occupation}%)")
    if beach.flag_color in [FlagColor.red, FlagColor.yellow]:
        problems.append(f"Bandera {beach.flag_color.value}")
    if beach.water_quality in [WaterQuality.poor, WaterQuality.sufficient] and min_quality:
        if beach.water_quality.value != min_quality.value:
            problems.append(f"Calidad {beach.water_quality.value}")
    if avoid_jellyfish and beach.jellyfish_present:
        problems.append("Medusas presentes")

    if not problems:
        return {
            "requested_beach": beach,
            "recommendation": None
        }

    alternatives = await get_best_beaches_nearby(db, beach.latitude, beach.longitude, radius_km, limit=5)
    for alt in alternatives:
        if str(alt["id"]) != str(beach.id):
            improvements = []
            if alt["current_occupation"] < beach.current_occupation:
                improvements.append("Ocupación menor")
            if alt["flag_color"] == FlagColor.green and beach.flag_color != FlagColor.green:
                improvements.append("Bandera verde")
            if alt["water_quality"] in [WaterQuality.excellent, WaterQuality.good] and beach.water_quality not in [WaterQuality.excellent, WaterQuality.good]:
                improvements.append("Mejor calidad")
            if not alt["jellyfish_present"] and beach.jellyfish_present:
                improvements.append("Sin medusas")

            alt["improvements"] = improvements if improvements else ["Mejor opción"]

    return {
        "requested_beach": beach,
        "recommendation": {
            "reason": ", ".join(problems),
            "alternatives": [a for a in alternatives if str(a["id"]) != str(beach.id)]
        }
    }