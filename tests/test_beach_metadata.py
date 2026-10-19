"""Model tests for the documented beach metadata added in T004.

The values used here are **synthetic placeholders** that only exercise
field round-trips. They are NOT real environmental or capacity data and must
never be presented as observations (principle of data veracity).
"""

import uuid

import pytest

from src.models import Beach, CapacityProvenanceError

# Fields added by T004. All must stay nullable and default to NULL (= unknown).
NEW_FIELDS = (
    "protection_status",
    "access_restrictions",
    "capacity_reference",
    "capacity_method",
    "vulnerability_level",
)


def _beach(**overrides) -> Beach:
    data = {
        "id": uuid.uuid4(),
        "name": f"Platja sintètica {uuid.uuid4().hex[:8]}",
        "region": "Mallorca",
        "latitude": 39.5,
        "longitude": 2.6,
    }
    data.update(overrides)
    return Beach(**data)


async def test_metadata_is_unknown_by_default(db):
    """A beach created without metadata keeps every field unknown (NULL)."""
    beach = _beach()
    db.add(beach)
    await db.commit()
    await db.refresh(beach)

    for field in NEW_FIELDS:
        assert getattr(beach, field) is None


def test_new_columns_are_nullable_and_have_no_default():
    """No default may ever claim 'not protected' / 'no restrictions' / 'low risk'."""
    for field in NEW_FIELDS:
        column = Beach.__table__.c[field]
        assert column.nullable is True, field
        assert column.default is None, field
        assert column.server_default is None, field


async def test_metadata_values_roundtrip(db):
    """Each field accepts and returns an explicit documented value."""
    beach = _beach(
        protection_status="figura de proteccion sintetica",
        access_restrictions="acceso restringido en temporada (documentado)",
        capacity_reference="referencia sintetica de capacidad",
        capacity_method="metodologia sintetica de prueba",
        vulnerability_level="nivel sintetico documentado",
    )
    db.add(beach)
    await db.commit()
    beach_id = beach.id

    db.expire_all()
    stored = await db.get(Beach, beach_id)
    assert stored.protection_status == "figura de proteccion sintetica"
    assert stored.access_restrictions == "acceso restringido en temporada (documentado)"
    assert stored.capacity_reference == "referencia sintetica de capacidad"
    assert stored.capacity_method == "metodologia sintetica de prueba"
    assert stored.vulnerability_level == "nivel sintetico documentado"


async def test_capacity_reference_without_method_is_rejected(db):
    """T004 rule: capacity_reference without capacity_method is invalid."""
    db.add(_beach(capacity_reference="referencia sin metodologia"))

    with pytest.raises(CapacityProvenanceError):
        await db.commit()

    await db.rollback()


async def test_capacity_method_without_reference_is_allowed(db):
    """Documenting only the method (no reference) is valid."""
    beach = _beach(capacity_method="metodologia sintetica")
    db.add(beach)
    await db.commit()
    await db.refresh(beach)

    assert beach.capacity_method == "metodologia sintetica"
    assert beach.capacity_reference is None


async def test_pre_existing_row_can_be_updated_later(db):
    """A row created before T004 can receive explicit metadata afterwards."""
    beach = _beach()
    db.add(beach)
    await db.commit()

    beach.capacity_method = "metodologia sintetica posterior"
    beach.capacity_reference = "referencia sintetica posterior"
    beach.protection_status = "estado sintetico posterior"
    await db.commit()
    await db.refresh(beach)

    assert beach.capacity_reference == "referencia sintetica posterior"
    assert beach.capacity_method == "metodologia sintetica posterior"
    assert beach.protection_status == "estado sintetico posterior"


async def test_api_keeps_working_without_metadata(client):
    """The existing API contract is unchanged: it still creates/reads beaches.

    T004 does not expose the new metadata through the Pydantic schemas, so a
    beach is created and read without supplying it and the response keeps its
    previous shape (the new fields are neither required nor returned).
    """
    created = await client.post(
        "/api/v1/beaches/",
        json={
            "name": "Cala sense metadades",
            "region": "Mallorca",
            "latitude": 39.51,
            "longitude": 2.61,
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Cala sense metadades"
    assert "data_status" in body

    fetched = await client.get(f"/api/v1/beaches/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["id"]
