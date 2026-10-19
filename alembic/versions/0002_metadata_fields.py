"""beach capacity and environmental metadata fields

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-19

Adds the five documented metadata fields required by task T004 to ``beaches``:

* ``protection_status``
* ``access_restrictions``
* ``capacity_reference``
* ``capacity_method``
* ``vulnerability_level``

Design notes
------------
* All five columns are **nullable** on purpose: ``NULL`` means
  "unknown / not documented" and MUST NOT be read as a favourable value. The
  migration preserves every existing row and invents no value for them
  (FR-003, FR-014; ADR 0002 and ADR 0005).
* Only portable SQL types are used (``VARCHAR`` / ``TEXT``): no PostgreSQL
  ``ENUM``, no ``JSON``/``JSONB`` and no server-side defaults. Each column is a
  plain ``ALTER TABLE beaches ADD COLUMN``, supported unchanged by PostgreSQL
  and by SQLite, so **no table is rebuilt** and no existing data is touched.
* The rule "``capacity_reference`` requires ``capacity_method``" is enforced by
  the ORM invariant in ``src/models.py`` instead of a ``CHECK`` constraint: SQLite
  cannot ``ALTER TABLE ... ADD CONSTRAINT`` and dropping a column referenced by
  a check would force a table rebuild (ADR 0005).
* ``downgrade`` drops only these five columns; it does not touch the rest of the
  schema (which keeps `0001`-era data intact).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (name, type) in the order they are added. Removing them in reverse order keeps
# upgrade/downgrade symmetric.
_NEW_COLUMNS: tuple[tuple[str, sa.types.TypeEngine], ...] = (
    ("protection_status", sa.String(length=100)),
    ("access_restrictions", sa.Text()),
    ("capacity_reference", sa.String(length=255)),
    ("capacity_method", sa.String(length=255)),
    ("vulnerability_level", sa.String(length=50)),
)


def upgrade() -> None:
    for name, type_ in _NEW_COLUMNS:
        op.add_column("beaches", sa.Column(name, type_, nullable=True))


def downgrade() -> None:
    for name, _ in reversed(_NEW_COLUMNS):
        op.drop_column("beaches", name)
