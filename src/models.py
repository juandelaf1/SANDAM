import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from src.database import Base


class Tide(str, Enum):
    alta = "alta"
    baja = "baja"
    media = "media"


class FlagColor(str, Enum):
    green = "green"
    yellow = "yellow"
    red = "red"
    unknown = "unknown"


class WaterQuality(str, Enum):
    excellent = "excellent"
    good = "good"
    sufficient = "sufficient"
    poor = "poor"
    unknown = "unknown"


class DataStatus(str, Enum):
    live = "live"
    estimated = "estimated"
    unavailable = "unavailable"


class Beach(Base):
    __tablename__ = "beaches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    region = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    max_capacity = Column(Integer, nullable=True)
    current_occupation = Column(Integer, default=0)

    water_temp = Column(Float, nullable=True)
    air_temp = Column(Float, nullable=True)
    uv_index = Column(Integer, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wave_height = Column(Float, nullable=True)

    tide = Column(Enum(Tide), nullable=True)
    flag_color = Column(Enum(FlagColor), default=FlagColor.unknown)

    jellyfish_present = Column(Boolean, default=False)
    jellyfish_species = Column(String(100), nullable=True)

    sargasso_level = Column(Integer, default=0)
    posidonia_present = Column(Boolean, default=False)

    water_quality = Column(Enum(WaterQuality), default=WaterQuality.unknown)
    e_coli_count = Column(Integer, nullable=True)
    enterococci_count = Column(Integer, nullable=True)

    has_kiosk = Column(Boolean, default=False)
    has_shade = Column(Boolean, default=False)
    has_showers = Column(Boolean, default=False)
    has_parking = Column(Boolean, default=False)
    has_accessibility = Column(Boolean, default=False)
    has_lifeguard = Column(Boolean, default=False)

    data_status = Column(Enum(DataStatus), default=DataStatus.unavailable)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_beach_location", "latitude", "longitude"),
        Index("idx_beach_region", "region"),
        Index("idx_beach_flag", "flag_color"),
        Index("idx_beach_quality", "water_quality"),
    )