"""Add TripPicture.pic_preview thumbnail column (Frontend Phase 2)

Revision ID: 7c2d9a1b4f6e
Revises: 3f8a1c2d4e5b
Create Date: 2026-10-16

Nullable ADD COLUMN: safe on existing databases, legacy rows get previews
generated lazily by the image route.
"""

import sqlalchemy as sa
from alembic import op

revision = "7c2d9a1b4f6e"
down_revision = "3f8a1c2d4e5b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    cols = [c["name"] for c in sa.inspect(bind).get_columns("Trip_Pictures")]
    if "pic_preview" not in cols:
        op.add_column(
            "Trip_Pictures", sa.Column("pic_preview", sa.LargeBinary(), nullable=True)
        )


def downgrade() -> None:
    bind = op.get_bind()
    cols = [c["name"] for c in sa.inspect(bind).get_columns("Trip_Pictures")]
    if "pic_preview" in cols:
        op.drop_column("Trip_Pictures", "pic_preview")
