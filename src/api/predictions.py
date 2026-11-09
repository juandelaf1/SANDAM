"""Prediction endpoints for SANDAM API (T008).

* ``/ideal-score`` uses the **canonical** scoring (``src.utils.scoring``); the
  divergent ``calculate_ideal_score`` is retired (FR-016).
* ``/forecast`` and ``/shade`` return an explicit ``insufficient_data`` result:
  there is no defined method or data source for them, so they no longer fabricate
  values (FR-005, FR-012).
* Occupation and jellyfish estimates are deterministic heuristics labelled with
  ``nature``/``method``/``validated``; when their base observation is unknown they
  return ``insufficient_data`` instead of defaulting to an invented value (FR-003).

Observed values are read as-is from the model: this module does not invent
defaults (no ``or 50``, no ``or "unknown"``).
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.deps import get_db
from src.models import Beach
from src.schemas import ResponseStatus
from src.utils.predictions import (
    REASON_NO_METHOD_FORECAST,
    REASON_NO_METHOD_NATURAL_SHADE,
    STATUS_OK,
    predict_jellyfish_presence,
    predict_occupation_advanced,
)
from src.utils.scoring import PRESSURE_LABEL, evaluate_beach

router = APIRouter(prefix="/predictions", tags=["predictions"])

# Etiqueta de presentación del score canónico. Son **bandas de presentación**, no
# umbrales ecológicos ni de capacidad (research.md §D9). Con score desconocido la
# etiqueta es ``None``: no se inventa una valoración.
RATING_BANDS = ((80, "EXCELENTE"), (60, "BUENA"), (40, "REGULAR"))


def _rating(score: Optional[float]) -> Optional[str]:
    if score is None:
        return None
    for threshold, label in RATING_BANDS:
        if score >= threshold:
            return label
    return "NO RECOMENDADA"


async def _find_beach(db: AsyncSession, beach_name: str) -> Optional[Beach]:
    result = await db.execute(
        select(Beach).where(Beach.name.ilike(f"%{beach_name}%")).limit(1)
    )
    return result.scalar_one_or_none()


def _beach_observations(beach: Beach) -> dict:
    """Valores observados pasados tal cual: sin valores por defecto inventados."""
    return {
        "name": beach.name,
        "current_occupation": beach.current_occupation,
        "flag_color": beach.flag_color,
        "water_quality": beach.water_quality,
        "jellyfish_present": beach.jellyfish_present,
        "jellyfish_species": beach.jellyfish_species,
        "water_temp": beach.water_temp,
        "wave_height": beach.wave_height,
        "uv_index": beach.uv_index,
        "has_lifeguard": beach.has_lifeguard,
        "has_parking": beach.has_parking,
        "has_accessibility": beach.has_accessibility,
        "has_showers": beach.has_showers,
        "has_shade": beach.has_shade,
        "has_kiosk": beach.has_kiosk,
    }


def _unavailable(beach: Beach, reason: str) -> dict:
    """Resultado explícito de indisponibilidad (FR-012) para las rutas sin método."""
    return {
        "contract_version": "sandam-predictions/0.1",
        "beach": beach.name,
        "beach_id": str(beach.id),
        "status": ResponseStatus.insufficient_data.value,
        "reason": reason,
        "nature": "unknown",
        "validated": False,
        "procedencia": "estimacion/no disponible (sin metodo/fuente verificada; Modo B)",
        "timestamp": datetime.now().isoformat(),
    }


def _estimation_block(estimation: dict) -> dict:
    """Envuelve una estimación con su naturaleza, método y estado (FR-004/FR-005)."""
    return {
        "status": estimation["status"],
        "nature": estimation.get("nature"),
        "method": estimation.get("method"),
        "validated": estimation.get("validated", False),
        "confidence": estimation.get("confidence"),
        "reason": estimation.get("reason"),
    }


@router.get("/occupation/{beach_name}")
async def predict_beach_occupation(
    beach_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Estimación determinista de ocupación (método heurístico no validado)."""
    beach = await _find_beach(db, beach_name)

    if not beach:
        return {"error": "Beach not found"}

    prediction = predict_occupation_advanced(_beach_observations(beach))

    if prediction["status"] != STATUS_OK:
        return {**_unavailable(beach, prediction["reason"]), "method": prediction["method"]}

    return {
        "contract_version": "sandam-predictions/0.1",
        "beach": beach.name,
        "beach_id": str(beach.id),
        **_estimation_block(prediction),
        "current_occupation": beach.current_occupation,
        "predicted_occupation": prediction["predicted"],
        "recommendation": prediction["recommendation"],
        "best_time": prediction["best_time"],
        "factors": prediction["factors"],
        "procedencia": "prediccion/estimacion heuristica no validada (ver nature/method/validated); ocupacion base segun estado disponible",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/jellyfish/{beach_name}")
async def predict_jellyfish_risk(
    beach_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Estimación determinista del riesgo de medusas (método heurístico no validado)."""
    beach = await _find_beach(db, beach_name)

    if not beach:
        return {"error": "Beach not found"}

    prediction = predict_jellyfish_presence(_beach_observations(beach))

    if prediction["status"] != STATUS_OK:
        return {**_unavailable(beach, prediction["reason"]), "method": prediction["method"]}

    return {
        "contract_version": "sandam-predictions/0.1",
        "beach": beach.name,
        "beach_id": str(beach.id),
        **_estimation_block(prediction),
        "risk_level": prediction["risk_level"],
        "level": prediction["level"],
        "prediction": prediction["prediction"],
        "recommendation": prediction["recommendation"],
        "expected_species": prediction["expected_species"],
        "factors": prediction["factors"],
        "procedencia": "prediccion/estimacion heuristica no validada (ver nature/method/validated); base segun estado disponible",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/shade/{beach_name}")
async def get_shade_availability(
    beach_name: str,
    hour: int = Query(None, ge=0, le=23, description="Hour of day (0-23)"),
    db: AsyncSession = Depends(get_db)
):
    """Sin método ni fuente para la sombra natural: se declara indisponible."""
    beach = await _find_beach(db, beach_name)

    if not beach:
        return {"error": "Beach not found"}

    current_hour = hour if hour is not None else datetime.now().hour

    return {
        **_unavailable(beach, REASON_NO_METHOD_NATURAL_SHADE),
        "current_hour": current_hour,
    }


@router.get("/forecast/{beach_name}")
async def get_beach_forecast(
    beach_name: str,
    days: int = Query(3, ge=1, le=7),
    db: AsyncSession = Depends(get_db)
):
    """Sin método ni datos de pronóstico: se declara indisponible (FR-005)."""
    beach = await _find_beach(db, beach_name)

    if not beach:
        return {"error": "Beach not found"}

    return {
        **_unavailable(beach, REASON_NO_METHOD_FORECAST),
        "days": days,
        "forecast": None,
    }


@router.get("/ideal-score/{beach_name}")
async def get_ideal_score(
    beach_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Score **canónico** de la playa (FR-016) y estimaciones etiquetadas.

    ``status`` usa ``ResponseStatus``: ``ok`` si hay score, ``no_suitable_alternatives``
    si la playa queda excluida (motivos en ``eligibility_conditions``) e
    ``insufficient_data`` si faltan datos. ``eligible`` es la señal principal.
    """
    beach = await _find_beach(db, beach_name)

    if not beach:
        return {"error": "Beach not found"}

    observations = _beach_observations(beach)
    evaluation = evaluate_beach(observations)
    occ_pred = predict_occupation_advanced(observations)
    jelly_pred = predict_jellyfish_presence(observations)

    if evaluation.exclusions:
        status = ResponseStatus.no_suitable_alternatives.value
    elif evaluation.score is None:
        status = ResponseStatus.insufficient_data.value
    else:
        status = ResponseStatus.ok.value

    return {
        "contract_version": "sandam-predictions/0.1",
        "beach": beach.name,
        "beach_id": str(beach.id),
        "status": status,
        "eligible": not evaluation.exclusions,
        "eligibility_conditions": [
            {"type": "safety_risk", "reason": reason, "source": None}
            for reason in evaluation.exclusions
        ],
        "score": evaluation.score,
        "rating": _rating(evaluation.score),
        "coverage": evaluation.coverage,
        "factors": evaluation.factors,
        "relative_pressure": {"value": evaluation.relative_pressure, "label": PRESSURE_LABEL},
        "prediction": {
            **_estimation_block(occ_pred),
            "occupation": occ_pred.get("predicted"),
            "recommendation": occ_pred.get("recommendation"),
        },
        "jellyfish": {
            **_estimation_block(jelly_pred),
            "risk": jelly_pred.get("level"),
            "recommendation": jelly_pred.get("recommendation"),
            "expected_species": jelly_pred.get("expected_species"),
        },
        "procedencia": "score canonico + estimaciones heuristicas no validadas (ver nature/method/validated/coverage); presion relativa, no capacidad oficial",
        "timestamp": datetime.now().isoformat(),
    }
