from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src import crud
from src import schemas
from src.deps import get_db
from src.utils.recommendations import generate_recommendations, generate_alerts

router = APIRouter(prefix="/beaches", tags=["recommendations"])


@router.get("/{beach_id}/recommendations", response_model=schemas.RecommendationResponse)
async def get_beach_recommendations(
    beach_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    beach = await crud.get_beach(db, beach_id)
    if not beach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beach not found"
        )

    beach_dict = {
        "name": beach.name,
        "current_occupation": beach.current_occupation,
        "flag_color": beach.flag_color,
        "water_quality": beach.water_quality,
        "jellyfish_present": beach.jellyfish_present,
        "jellyfish_species": beach.jellyfish_species,
        "uv_index": beach.uv_index,
        "wave_height": beach.wave_height,
        "has_lifeguard": beach.has_lifeguard,
        "sargasso_level": beach.sargasso_level
    }

    recommendations = generate_recommendations(beach_dict)
    alerts = generate_alerts(beach_dict)

    return {
        "beach_id": beach.id,
        "beach_name": beach.name,
        "data_status": beach.data_status,
        "recommendations": recommendations,
        "alerts": alerts,
        "last_updated": beach.last_updated
    }