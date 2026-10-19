"""initial schema: beaches table

Revision ID: 0001
Revises:
Create Date: 2026-10-19

Reflects the schema declared in ``src/models.py`` (table ``beaches``) using
SQLAlchemy 2.0's generic ``Uuid`` type, targeting PostgreSQL. This revision
contains ONLY what already exists in the models at the moment of writing.

It deliberately does NOT include the observation/provenance metadata
(``protection_status``, ``access_restrictions``, ``capacity_reference``,
``capacity_method``, ``vulnerability_level``) or any ``Observation`` /
``Prediction`` table: those belong to a later revision (task T004 and the
observation data model).

``downgrade`` reverses ``upgrade`` exactly (drops the indexes and the table).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "beaches",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("region", sa.String(length=100), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("max_capacity", sa.Integer(), nullable=True),
        sa.Column("current_occupation", sa.Integer(), nullable=True),
        sa.Column("water_temp", sa.Float(), nullable=True),
        sa.Column("air_temp", sa.Float(), nullable=True),
        sa.Column("uv_index", sa.Integer(), nullable=True),
        sa.Column("wind_speed", sa.Float(), nullable=True),
        sa.Column("wave_height", sa.Float(), nullable=True),
        sa.Column("tide", sa.String(length=20), nullable=True),
        sa.Column("flag_color", sa.String(length=20), nullable=True),
        sa.Column("jellyfish_present", sa.Boolean(), nullable=True),
        sa.Column("jellyfish_species", sa.String(length=100), nullable=True),
        sa.Column("sargasso_level", sa.Integer(), nullable=True),
        sa.Column("posidonia_present", sa.Boolean(), nullable=True),
        sa.Column("water_quality", sa.String(length=20), nullable=True),
        sa.Column("e_coli_count", sa.Integer(), nullable=True),
        sa.Column("enterococci_count", sa.Integer(), nullable=True),
        sa.Column("has_kiosk", sa.Boolean(), nullable=True),
        sa.Column("has_shade", sa.Boolean(), nullable=True),
        sa.Column("has_showers", sa.Boolean(), nullable=True),
        sa.Column("has_parking", sa.Boolean(), nullable=True),
        sa.Column("has_accessibility", sa.Boolean(), nullable=True),
        sa.Column("has_lifeguard", sa.Boolean(), nullable=True),
        sa.Column("data_status", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # Unique index backing Beach.name (unique=True, index=True).
    op.create_index("ix_beaches_name", "beaches", ["name"], unique=True)
    # Indexes declared in Beach.__table_args__.
    op.create_index("idx_beach_location", "beaches", ["latitude", "longitude"], unique=False)
    op.create_index("idx_beach_region", "beaches", ["region"], unique=False)
    op.create_index("idx_beach_flag", "beaches", ["flag_color"], unique=False)
    op.create_index("idx_beach_quality", "beaches", ["water_quality"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_beach_quality", table_name="beaches")
    op.drop_index("idx_beach_flag", table_name="beaches")
    op.drop_index("idx_beach_region", table_name="beaches")
    op.drop_index("idx_beach_location", table_name="beaches")
    op.drop_index("ix_beaches_name", table_name="beaches")
    op.drop_table("beaches")
