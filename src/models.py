import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    event,
)
from sqlalchemy.orm import Session

from src.database import Base


def utcnow() -> datetime:
    """Naive UTC timestamp (compatible with the existing DateTime columns)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


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


class CapacityProvenanceError(ValueError):
    """`capacity_reference` was recorded without `capacity_method` (T004 rule).

    A capacity figure/reference without a documented method would look like a
    validated capacity, which the product must never imply (FR-014; ADR 0002).
    """


class Beach(Base):
    __tablename__ = "beaches"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
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

    tide = Column(String(20), nullable=True)
    flag_color = Column(String(20), default=FlagColor.unknown.value)

    jellyfish_present = Column(Boolean, default=False)
    jellyfish_species = Column(String(100), nullable=True)

    sargasso_level = Column(Integer, default=0)
    posidonia_present = Column(Boolean, default=False)

    water_quality = Column(String(20), default=WaterQuality.unknown.value)
    e_coli_count = Column(Integer, nullable=True)
    enterococci_count = Column(Integer, nullable=True)

    has_kiosk = Column(Boolean, default=False)
    has_shade = Column(Boolean, default=False)
    has_showers = Column(Boolean, default=False)
    has_parking = Column(Boolean, default=False)
    has_accessibility = Column(Boolean, default=False)
    has_lifeguard = Column(Boolean, default=False)

    # --- Metadatos documentados de capacidad y sensibilidad (tarea T004) ---
    # Todos anulables a propósito: NULL = "desconocido / no documentado". Nunca
    # un valor por defecto que afirme que la playa no está protegida, no tiene
    # restricciones o presenta riesgo bajo (FR-003, FR-014; ADR 0002/0005).
    # `access_restrictions` describe restricciones documentadas, NO su vigencia
    # en tiempo real (esa verificación pertenece al modelo de observaciones).
    protection_status = Column(String(100), nullable=True)
    access_restrictions = Column(Text, nullable=True)
    capacity_reference = Column(String(255), nullable=True)
    capacity_method = Column(String(255), nullable=True)
    vulnerability_level = Column(String(50), nullable=True)

    data_status = Column(String(20), default=DataStatus.unavailable.value)

    created_at = Column(DateTime, default=utcnow)
    last_updated = Column(DateTime, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index("idx_beach_location", "latitude", "longitude"),
        Index("idx_beach_region", "region"),
        Index("idx_beach_flag", "flag_color"),
        Index("idx_beach_quality", "water_quality"),
    )


@event.listens_for(Session, "before_flush")
def _enforce_capacity_provenance(session: Session, flush_context, instances) -> None:
    """Rule T004: `capacity_reference` without `capacity_method` is invalid.

    Checked on flush rather than with ``@validates`` because it is a
    cross-field invariant: setting the two attributes in either order (as the
    ORM constructor does) must not raise a false positive, while partial
    updates must still be validated against the resulting state.

    It is intentionally **not** a database CHECK constraint: adding one to an
    existing table is not supported by SQLite, and dropping a column referenced
    by it would force a full table rebuild (see ADR 0005).
    """
    for obj in list(session.new) + list(session.dirty):
        if isinstance(obj, Beach) and obj.capacity_reference is not None:
            if obj.capacity_method is None:
                raise CapacityProvenanceError(
                    "capacity_reference requiere capacity_method "
                    "(procedencia/metodología); no se admite una capacidad de "
                    "referencia sin su método"
                )