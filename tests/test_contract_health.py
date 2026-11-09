"""Smoke de contrato /health (P1/P8). No requiere BD para /health."""
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_has_contract_and_honest_capabilities():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["contract_version"] == "sandam-api/0.1"
    caps = body.get("capabilities") or {}
    assert caps.get("capacity_verified") is False
    assert caps.get("occupancy_realtime_verified") is False
    assert caps.get("provenance_required") is True
