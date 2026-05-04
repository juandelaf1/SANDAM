from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from src.models import Tide, FlagColor, WaterQuality, DataStatus


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


class BeachCreate(BeachBase):
    pass


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


class BeachResponse(BeachBase):
    id: UUID
    data_status: DataStatus = DataStatus.unavailable
    created_at: datetime
    last_updated: datetime

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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