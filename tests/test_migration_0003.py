"""Alembic migration tests for revision 0003 (spec 002 observations).

These tests apply the real migration chain to a temporary SQLite file,
so they exercise ``upgrade head`` / ``downgrade -1`` without touching
production data.
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

BEACH_NEW_COLUMNS = (
    "occupancy_status",
    "jellyfish_status",
    "sargasso_status",
    "posidonia_status",
    "data_origin",
)

NEW_TABLES = (
    "data_sources",
    "variables",
    "methods",
    "transformations",
    "validation_records",
    "ingestion_runs",
    "observations",
)


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


def test_upgrade_adds_0003_and_preserves_legacy_rows(tmp_path, monkeypatch):
    db_path = tmp_path / "t003_upgrade.db"
    config = _alembic_config(monkeypatch, db_path)

    # Start from 0001 and add a legacy row.
    command.upgrade(config, "0001")
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO beaches (id, name, region, latitude, longitude, current_occupation) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), "Legacy Beach", "Mallorca", 39.5, 2.6, 42),
        )

    # Before 0003: new tables absent, new columns absent.
    for t in NEW_TABLES:
        assert t not in _table_names(db_path)
    for col in BEACH_NEW_COLUMNS:
        assert col not in _columns(db_path)

    # Apply 0003 (aditive only).
    command.upgrade(config, "0003")

    # New tables present.
    for t in NEW_TABLES:
        assert t in _table_names(db_path)

    # New state columns present and nullable.
    columns = _columns(db_path)
    for col in BEACH_NEW_COLUMNS:
        assert col in columns

    # Legacy row untouched (current_occupation unchanged, new columns NULL).
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM beaches").fetchone()
        assert dict(row)["name"] == "Legacy Beach"
        assert int(dict(row)["current_occupation"]) == 42
        for col in BEACH_NEW_COLUMNS:
            assert dict(row)[col] is None


def test_downgrade_removes_0003_only(tmp_path, monkeypatch):
    db_path = tmp_path / "t003_downgrade.db"
    config = _alembic_config(monkeypatch, db_path)

    command.upgrade(config, "head")
    for col in BEACH_NEW_COLUMNS:
        assert col in _columns(db_path)
    for t in NEW_TABLES:
        assert t in _table_names(db_path)

    command.downgrade(config, "-1")
    for col in BEACH_NEW_COLUMNS:
        assert col not in _columns(db_path)
    for t in NEW_TABLES:
        assert t not in _table_names(db_path)

    # Legacy data preserved.
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        # There is no legacy row in this test; just confirm schema is coherent.
        tables_before = _table_names(db_path)
        assert "beaches" in tables_before
