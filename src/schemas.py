from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from src.models import Tide, FlagColor, WaterQuality, DataStatus


class StateFields(BaseModel):
    """Estado explícito de las variables heredadas (spec 002).

    Un valor legacy (``current_occupation=0``, ``jellyfish_present=False``, ...) no
    puede interpretarse sin su estado. El valor legado se conserva para compatibilidad
    y el estado dice cómo leerlo (FR-003/FR-004/FR-005).
    """

    occupancy_status: Optional[str] = None  # observed / estimated / stale / unknown / synthetic
    jellyfish_status: Optional[str] = None
    sargasso_status: Optional[str] = None
    posidonia_status: Optional[str] = None


class DataOrigin(str, Enum):
    seed = "seed"
    manual = "manual"
    imported = "imported"
    observed = "observed"
    unknown = "unknown"


class BeachBase(BaseModel):
    name: str = Field(..., max_length=255)
    region: str = Field(..., max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    max_capacity: Optional[int] = Field(None, gt=0)
    current_occupation: int = Field(default=0, ge=0, le=100)

    water_temp: Optional[float] = Field(None, ge=-10, le=50)
    air_temp: Optional[float] = Field(None, ge=-30, le=60)
    uv_index: Optional[int] = Field(None, ge=0, le=11)
    wind_speed: Optional[float] = Field(None, ge=0)
    wave_height: Optional[float] = Field(None, ge=0, le=20)

    tide: Optional[Tide] = None
    flag_color: FlagColor = FlagColor.unknown

    jellyfish_present: bool = False
    jellyfish_species: Optional[str] = None
    sargasso_level: int = Field(default=0, ge=0, le=3)
    posidonia_present: bool = False

    water_quality: WaterQuality = WaterQuality.unknown
    e_coli_count: Optional[int] = None
    enterococci_count: Optional[int] = None

    has_kiosk: bool = False
    has_shade: bool = False
    has_showers: bool = False
    has_parking: bool = False
    has_accessibility: bool = False
    has_lifeguard: bool = False
    # Estado explícito (spec 002) — se declara junto al valor legado
    occupancy_status: Optional[str] = None
    jellyfish_status: Optional[str] = None
    sargasso_status: Optional[str] = None
    posidonia_status: Optional[str] = None
    data_origin: Optional[str] = None


class BeachCreate(BeachBase):
    data_status: DataStatus = DataStatus.unavailable


class BeachUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    region: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    max_capacity: Optional[int] = Field(None, gt=0)
    current_occupation: Optional[int] = Field(None, ge=0, le=100)

    water_temp: Optional[float] = Field(None, ge=-10, le=50)
    air_temp: Optional[float] = Field(None, ge=-30, le=60)
    uv_index: Optional[int] = Field(None, ge=0, le=11)
    wind_speed: Optional[float] = Field(None, ge=0)
    wave_height: Optional[float] = Field(None, ge=0, le=20)

    tide: Optional[Tide] = None
    flag_color: Optional[FlagColor] = None

    jellyfish_present: Optional[bool] = None
    jellyfish_species: Optional[str] = None
    sargasso_level: Optional[int] = Field(None, ge=0, le=3)
    posidonia_present: Optional[bool] = None

    water_quality: Optional[WaterQuality] = None
    e_coli_count: Optional[int] = None
    enterococci_count: Optional[int] = None

    has_kiosk: Optional[bool] = None
    has_shade: Optional[bool] = None
    has_showers: Optional[bool] = None
    has_parking: Optional[bool] = None
    has_accessibility: Optional[bool] = None
    has_lifeguard: Optional[bool] = None

    data_status: Optional[DataStatus] = None


class BeachResponse(BeachBase):
    id: UUID
    data_status: DataStatus = DataStatus.unavailable
    created_at: datetime
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class BeachListResponse(BaseModel):
    total: int
    beaches: List[BeachResponse]


class NearbyBeachResponse(BaseModel):
    id: UUID
    name: str
    region: str
    latitude: float
    longitude: float
    current_occupation: int
    flag_color: FlagColor
    water_quality: WaterQuality
    has_lifeguard: bool
    distance_km: float

    model_config = ConfigDict(from_attributes=True)


class NearbyResponse(BaseModel):
    requested_lat: float
    requested_lon: float
    radius_km: float
    beaches: List[NearbyBeachResponse]


class BeachAlternative(BaseModel):
    beach: BeachResponse
    distance_km: float
    score: int
    improvements: List[str]


class RecommendationResponse(BaseModel):
    beach_id: UUID
    beach_name: str
    data_status: DataStatus
    recommendations: List[dict]
    alerts: List[dict]
    last_updated: datetime


class SearchResponse(BaseModel):
    requested_beach: Optional[BeachResponse]
    recommendation: Optional[dict]


class DashboardSummary(BaseModel):
    total_beaches: int
    avg_occupation: float
    quality_distribution: dict
    flag_distribution: dict
    active_alerts: int
    last_updated: datetime


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    timestamp: datetime


# ---------------------------------------------------------------------------
# Contrato aditivo de /donde-ir (tarea T005)
#
# Esquemas definidos conforme a
# ``specs/001-sustainable-beach-recommendation/contracts/donde-ir.openapi.yaml``.
# Alcance de T005: **solo** definir los esquemas de respuesta. No se cambia el
# scoring, la elegibilidad ni la política de selección de alternativas, y estos
# esquemas todavía **no** se conectan al endpoint (eso pertenece a T014/T018).
# Ningún valor se inventa: lo desconocido se representa de forma explícita
# (``nature=unknown`` / campos aditivos ausentes), nunca como condición favorable.
# ---------------------------------------------------------------------------


class DataNature(str, Enum):
    """Naturaleza de un valor (contrato: ``DataQuality.nature``; FR-004)."""

    observation = "observation"
    estimate = "estimate"
    prediction = "prediction"
    stale = "stale"
    unknown = "unknown"


class DataQuality(BaseModel):
    """Clasificación y procedencia de un valor (FR-004, FR-015).

    ``nature`` es obligatorio: todo valor relevante declara su naturaleza y
    ``unknown`` es un valor válido del enum, de modo que la ausencia de dato se
    expresa explícitamente y nunca se interpreta como favorable (FR-003).
    ``source`` puede faltar, porque un valor desconocido no tiene procedencia que
    citar.
    """

    nature: DataNature
    source: Optional[str] = None
    observed_at: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class Explanation(BaseModel):
    """Motivo legible por el que una playa se propone o descarta (FR-006)."""

    reason: str
    factors: List[str] = Field(default_factory=list)


class EligibilityCondition(BaseModel):
    """Condición de exclusión detectada (elemento de ``eligibility_conditions``)."""

    type: str
    reason: str
    source: Optional[str] = None


class PlayStatus(str, Enum):
    """Estado de una playa en la recomendación (contrato: ``Recommendation.status``)."""

    recomendada = "recomendada"
    marginal = "marginal"
    no_merece = "no_merece"


class ResponseStatus(str, Enum):
    """Estado global de la respuesta (contrato: ``DondeIrResponse.status``; FR-012)."""

    ok = "ok"
    no_suitable_alternatives = "no_suitable_alternatives"
    insufficient_data = "insufficient_data"


class UserLocation(BaseModel):
    """Ubicación del usuario (contrato: ``DondeIrResponse.ubicacion_usuario``)."""

    lat: float
    lon: float


class Recommendation(BaseModel):
    """Recomendación por playa (contrato: ``Recommendation``).

    Conserva íntegros los campos del contrato existente (FR-010) y añade los
    campos aditivos, todos opcionales: mientras las tareas posteriores no los
    calculen, se omiten y los clientes actuales siguen funcionando.
    """

    # --- Contrato existente (se preserva) ---
    nombre: str
    latitude: float
    longitude: float
    distancia_km: float
    tiempo_viaje_min: int
    hora_llegada: str
    score_original: float
    score_final: float
    status: PlayStatus
    color: str
    sol_restante_min: int
    flags: dict
    # --- Aditivo (opcional) ---
    eligible: Optional[bool] = None
    eligibility_conditions: Optional[List[EligibilityCondition]] = None
    pressure_relative: Optional[float] = None
    explanation: Optional[Explanation] = None
    data_quality: Optional[Dict[str, DataQuality]] = None


class DondeIrResponse(BaseModel):
    """Respuesta de ``/donde-ir/ahora`` (contrato: ``DondeIrResponse``).

    Los campos existentes se preservan; los aditivos son opcionales. Mientras no
    exista un cálculo de ruta real, ``travel_time_is_estimate`` es ``True`` por
    defecto para no atribuir al tiempo de viaje una precisión que no tiene
    (FR-013); T014 lo fijará de forma explícita.
    """

    # --- Contrato existente (se preserva) ---
    ubicacion_usuario: UserLocation
    hora_actual: str
    atardecer: str
    sol_restante: str
    total_playas: int
    recomendaciones: List[Recommendation]
    # --- Aditivo (opcional) ---
    status: Optional[ResponseStatus] = None
    travel_time_is_estimate: bool = True