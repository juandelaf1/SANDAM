"""observations, provenance and validity model (spec 002)

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-21

Adds the observation model of ``specs/002-trusted-observations-and-occupancy``:

* catalogs ``data_sources``, ``variables``, ``methods``, ``transformations``,
  ``validation_records`` and ``ingestion_runs``;
* the central ``observations`` table;
* explicit state columns on ``beaches`` (``occupancy_status``,
  ``jellyfish_status``, ``sargasso_status``, ``posidonia_status``) plus
  ``data_origin``.

Design notes
------------
* **Additive only.** No existing column is altered or dropped, no table is
  rebuilt and **no existing row is modified**: the classification of legacy
  rows is a separate, auditable step (``decision-review.md`` §13, Fase 1B).
  A legacy ``0``/``False`` is kept as-is and is *not* reinterpreted; the new
  state columns say how it must be read (FR-003/FR-005/FR-017).
* **Portable types only**: no PostgreSQL ``ENUM``, no ``JSON``/``JSONB``, no
  server-side defaults, consistent with ADR 0005. The textual vocabularies are
  validated in the domain layer (``src/utils/observations.py``) and in tests.
* The legacy columns keep their current types and defaults, so existing
  clients are unaffected until the compatibility phase (Fase 6) decides
  whether a value becomes ``NULL``.
* ``downgrade`` drops only what this revision adds.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (name, type) in the order they are added to ``beaches``.
_BEACH_COLUMNS: tuple[tuple[str, sa.types.TypeEngine], ...] = (
    ("occupancy_status", sa.String(length=20)),
    ("jellyfish_status", sa.String(length=20)),
    ("sargasso_status", sa.String(length=20)),
    ("posidonia_status", sa.String(length=20)),
    ("data_origin", sa.String(length=20)),
)


def upgrade() -> None:
    op.create_table(
        "data_sources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("kind", sa.String(length=50), nullable=False),
        sa.Column("uri", sa.Text(), nullable=True),
        sa.Column("license", sa.String(length=100), nullable=True),
        sa.Column("license_url", sa.Text(), nullable=True),
        sa.Column("terms_reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("terms_reviewed_by", sa.String(length=100), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("contact", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_sources_name", "data_sources", ["name"], unique=False)

    op.create_table(
        "variables",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column("value_type", sa.String(length=20), nullable=False),
        sa.Column("allowed_values", sa.Text(), nullable=True),
        sa.Column("default_validity_minutes", sa.Integer(), nullable=True),
        sa.Column("is_pressure_indicator", sa.Boolean(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("code"),
    )

    op.create_table(
        "methods",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("validated", sa.Boolean(), nullable=False),
        sa.Column("validation_id", sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "transformations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.String(length=20), nullable=True),
        sa.Column("input_units", sa.String(length=20), nullable=True),
        sa.Column("output_units", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "validation_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("method_id", sa.Uuid(), nullable=False),
        sa.Column("reference_source_id", sa.Uuid(), nullable=False),
        sa.Column("period_start", sa.DateTime(), nullable=False),
        sa.Column("period_end", sa.DateTime(), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("coverage", sa.Float(), nullable=False),
        sa.Column("metrics", sa.Text(), nullable=True),
        sa.Column("baseline", sa.String(length=255), nullable=True),
        sa.Column("decision", sa.String(length=20), nullable=True),
        sa.Column("decided_at", sa.DateTime(), nullable=True),
        sa.Column("decided_by", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("rows_read", sa.Integer(), nullable=False),
        sa.Column("rows_written", sa.Integer(), nullable=False),
        sa.Column("rows_rejected", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )

    op.create_table(
        "observations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("beach_id", sa.Uuid(), nullable=False),
        sa.Column("variable_code", sa.String(length=50), nullable=False),
        sa.Column("value_num", sa.Float(), nullable=True),
        sa.Column("value_bool", sa.Boolean(), nullable=True),
        sa.Column("value_text", sa.String(length=255), nullable=True),
        sa.Column("value_enum", sa.String(length=50), nullable=True),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column("nature", sa.String(length=20), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column("method_id", sa.Uuid(), nullable=True),
        sa.Column("observed_at", sa.DateTime(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), nullable=False),
        sa.Column("valid_from", sa.DateTime(), nullable=True),
        sa.Column("valid_until", sa.DateTime(), nullable=True),
        sa.Column("spatial_resolution_m", sa.Float(), nullable=True),
        sa.Column("uncertainty", sa.Float(), nullable=True),
        sa.Column("uncertainty_unit", sa.String(length=20), nullable=True),
        sa.Column("validation_status", sa.String(length=20), nullable=False),
        sa.Column("validation_id", sa.Uuid(), nullable=True),
        sa.Column("transformation_id", sa.Uuid(), nullable=True),
        sa.Column("privacy_level", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_observations_beach_id", "observations", ["beach_id"], unique=False)
    op.create_index(
        "ix_observations_variable_code", "observations", ["variable_code"], unique=False
    )
    op.create_index(
        "idx_obs_beach_variable_observed",
        "observations",
        ["beach_id", "variable_code", "observed_at"],
        unique=False,
    )
    op.create_index(
        "idx_obs_status_valid_until", "observations", ["status", "valid_until"], unique=False
    )
    op.create_index(
        "idx_obs_source_fetched", "observations", ["source_id", "fetched_at"], unique=False
    )

    for name, type_ in _BEACH_COLUMNS:
        op.add_column("beaches", sa.Column(name, type_, nullable=True))


def downgrade() -> None:
    for name, _ in reversed(_BEACH_COLUMNS):
        op.drop_column("beaches", name)

    op.drop_index("idx_obs_source_fetched", table_name="observations")
    op.drop_index("idx_obs_status_valid_until", table_name="observations")
    op.drop_index("idx_obs_beach_variable_observed", table_name="observations")
    op.drop_index("ix_observations_variable_code", table_name="observations")
    op.drop_index("ix_observations_beach_id", table_name="observations")
    op.drop_table("observations")

    op.drop_table("ingestion_runs")
    op.drop_table("validation_records")
    op.drop_table("transformations")
    op.drop_table("methods")
    op.drop_table("variables")

    op.drop_index("ix_data_sources_name", table_name="data_sources")
    op.drop_table("data_sources")
