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
    synthetic = "synthetic"


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

    # --- Spec 002: estado explícito de las variables heredadas (T008) ---
    # El valor legado (`current_occupation`, `jellyfish_present`, ...) se conserva
    # por compatibilidad, pero **no** puede interpretarse sin su estado: un `0`
    # o un `False` heredados no son una observación (FR-003/FR-004/FR-005).
    # Estos estados son anulables: NULL = "sin estado clasificado todavía".
    # Valores: `observed`, `estimated`, `stale`, `unknown`, `synthetic`.
    occupancy_status = Column(String(20), nullable=True)
    jellyfish_status = Column(String(20), nullable=True)
    sargasso_status = Column(String(20), nullable=True)
    posidonia_status = Column(String(20), nullable=True)
    # Procedencia del registro: `seed`, `manual`, `imported`, `observed`, `unknown`.
    data_origin = Column(String(20), nullable=True)

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


# --- Spec 002: observations, provenance, validity ---

class DataSource(Base):
    __tablename__ = "data_sources"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    kind = Column(String(50), nullable=False)
    uri = Column(Text, nullable=True)
    license = Column(String(100), nullable=True)
    license_url = Column(Text, nullable=True)
    terms_reviewed_at = Column(DateTime, nullable=True)
    terms_reviewed_by = Column(String(100), nullable=True)
    priority = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="blocked")
    contact = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class Variable(Base):
    __tablename__ = "variables"
    code = Column(String(50), primary_key=True)
    unit = Column(String(20), nullable=False)
    value_type = Column(String(20), nullable=False)
    allowed_values = Column(Text, nullable=True)
    default_validity_minutes = Column(Integer, nullable=True)
    is_pressure_indicator = Column(Boolean, default=False)
    description = Column(Text, nullable=True)


class Method(Base):
    __tablename__ = "methods"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    kind = Column(String(20), nullable=False)
    version = Column(String(20), nullable=True)
    description = Column(Text, nullable=True)
    validated = Column(Boolean, default=False)
    validation_id = Column(Uuid(as_uuid=True), nullable=True)


class Transformation(Base):
    __tablename__ = "transformations"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), nullable=True)
    input_units = Column(String(20), nullable=True)
    output_units = Column(String(20), nullable=True)


class ValidationRecord(Base):
    __tablename__ = "validation_records"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    method_id = Column(Uuid(as_uuid=True), nullable=False)
    reference_source_id = Column(Uuid(as_uuid=True), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    sample_size = Column(Integer, nullable=False)
    coverage = Column(Float, nullable=False)
    metrics = Column(Text, nullable=True)
    baseline = Column(String(255), nullable=True)
    decision = Column(String(20), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    decided_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(Uuid(as_uuid=True), nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="success")
    rows_read = Column(Integer, default=0)
    rows_written = Column(Integer, default=0)
    rows_rejected = Column(Integer, default=0)
    error = Column(Text, nullable=True)
    idempotency_key = Column(String(255), unique=True, nullable=True)


class Observation(Base):
    __tablename__ = "observations"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beach_id = Column(Uuid(as_uuid=True), nullable=False, index=True)
    variable_code = Column(String(50), nullable=False, index=True)
    value_num = Column(Float, nullable=True)
    value_bool = Column(Boolean, nullable=True)
    value_text = Column(String(255), nullable=True)
    value_enum = Column(String(50), nullable=True)
    unit = Column(String(20), nullable=False, default="unknown")
    nature = Column(String(20), nullable=False, default="unknown")
    source_id = Column(Uuid(as_uuid=True), nullable=True)
    method_id = Column(Uuid(as_uuid=True), nullable=True)
    observed_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, nullable=False, default=utcnow)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    spatial_resolution_m = Column(Float, nullable=True)
    uncertainty = Column(Float, nullable=True)
    uncertainty_unit = Column(String(20), nullable=True)
    validation_status = Column(String(20), nullable=False, default="unvalidated")
    validation_id = Column(Uuid(as_uuid=True), nullable=True)
    transformation_id = Column(Uuid(as_uuid=True), nullable=True)
    privacy_level = Column(String(20), nullable=False, default="aggregate")
    status = Column(String(20), nullable=False, default="current")
    created_at = Column(DateTime, default=utcnow)

    __table_args__ = (
        Index("idx_obs_beach_variable_observed", "beach_id", "variable_code", "observed_at"),
        Index("idx_obs_status_valid_until", "status", "valid_until"),
        Index("idx_obs_source_fetched", "source_id", "fetched_at"),
    )