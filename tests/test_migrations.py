"""Alembic migration tests for revision 0002 (T004).

These tests run the **real migration chain** against a temporary SQLite file,
so they exercise what ``alembic upgrade head`` does to a database that already
contains rows, not just the ORM metadata used by the other tests.

The connection URL is injected by patching ``src.config.get_settings`` (which
``alembic/env.py`` imports and calls), so no credential is ever involved.
"""

from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path

from alembic import command
from alembic.config import Config

import src.config as config_module
from src.config import Settings

REPO_ROOT = Path(__file__).resolve().parents[1]

NEW_FIELDS = (
    "protection_status",
    "access_restrictions",
    "capacity_reference",
    "capacity_method",
    "vulnerability_level",
)

LEGACY_ROW = {
    "id": uuid.uuid4().hex,
    "name": "Platja heretada",
    "region": "Mallorca",
    "latitude": "39.5",
    "longitude": "2.6",
    "current_occupation": "42",
    "max_capacity": "1000",
}


def _alembic_config(monkeypatch, db_path: Path) -> Config:
    url = f"sqlite+aiosqlite:///{db_path}"
    monkeypatch.setattr(config_module, "get_settings", lambda: Settings(database_url=url))
    config = Config(str(REPO_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "alembic"))
    return config


def _table_names(db_path: Path) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {row[0] for row in rows}


def _columns(db_path: Path) -> list[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("PRAGMA table_info(beaches)").fetchall()
    return [row[1] for row in rows]


def _insert_legacy_row(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO beaches (id, name, region, latitude, longitude, "
            "current_occupation, max_capacity) VALUES (:id, :name, :region, "
            ":latitude, :longitude, :current_occupation, :max_capacity)",
            LEGACY_ROW,
        )


def _fetch_row(db_path: Path) -> dict:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM beaches").fetchone()
    return dict(row)


def test_upgrade_adds_columns_and_preserves_existing_rows(tmp_path, monkeypatch):
    db_path = tmp_path / "t004_upgrade.db"
    config = _alembic_config(monkeypatch, db_path)

    # Base state: revision 0001 only.
    command.upgrade(config, "0001")
    assert "beaches" in _table_names(db_path)
    for field in NEW_FIELDS:
        assert field not in _columns(db_path)

    # A row that exists before T004 (task scenario B).
    _insert_legacy_row(db_path)

    command.upgrade(config, "head")

    columns = _columns(db_path)
    for field in NEW_FIELDS:
        assert field in columns

    row = _fetch_row(db_path)
    # The pre-existing data survives unchanged...
    assert row["name"] == LEGACY_ROW["name"]
    assert row["region"] == LEGACY_ROW["region"]
    assert int(row["current_occupation"]) == 42
    # ...and the new metadata is NOT invented: it stays unknown (NULL).
    for field in NEW_FIELDS:
        assert row[field] is None


def test_downgrade_removes_only_new_columns_and_can_be_reapplied(tmp_path, monkeypatch):
    db_path = tmp_path / "t004_downgrade.db"
    config = _alembic_config(monkeypatch, db_path)

    command.upgrade(config, "0001")
    _insert_legacy_row(db_path)
    # This test targets revision 0002 explicitly: it must not depend on how
    # many revisions come after it (0003, spec 002).
    command.upgrade(config, "0002")

    # Task scenario C: revert exactly one revision.
    command.downgrade(config, "0001")

    columns = _columns(db_path)
    assert "beaches" in _table_names(db_path)
    for field in NEW_FIELDS:
        assert field not in columns
    # The rest of the schema (0001) is untouched.
    assert {"id", "name", "region", "latitude", "longitude"} <= set(columns)
    assert _fetch_row(db_path)["name"] == LEGACY_ROW["name"]

    # Re-apply 0002 and confirm the schema is coherent again.
    command.upgrade(config, "0002")
    for field in NEW_FIELDS:
        assert field in _columns(db_path)
