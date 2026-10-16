"""Initial schema with FKs, unique owner/name pairs, wider password hash

Revision ID: 3f8a1c2d4e5b
Revises:
Create Date: 2026-10-16

Covers Phase 2 model changes:
- Riders.passw String(50) -> String(255)
- added_by / event_owner / pic_owner -> FK to Users_Tab.email, NOT NULL, indexed
- unique (owner, name) on TripRecords and Mechanical_Tab
- NOT NULL on owner/name/email columns

For pre-existing databases created by db.create_all(), mark instead of running:
    flask db stamp head
"""

import sqlalchemy as sa
from alembic import op

revision = "3f8a1c2d4e5b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "Users_Tab",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("passw", sa.String(length=255), nullable=True),
        sa.Column("joined_on", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_Users_Tab_email", "Users_Tab", ["email"], unique=True)

    op.create_table(
        "TripRecords",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trip_name", sa.String(length=100), nullable=False),
        sa.Column("trip_date", sa.Date(), nullable=True),
        sa.Column("area_name", sa.String(length=50), nullable=True),
        sa.Column("km_travelled", sa.Integer(), nullable=True),
        sa.Column("h_travelled", sa.Integer(), nullable=True),
        sa.Column("km_initial", sa.Integer(), nullable=True),
        sa.Column("km_final", sa.Integer(), nullable=True),
        sa.Column("added_by", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(["added_by"], ["Users_Tab.email"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("added_by", "trip_name", name="uq_trips_owner_name"),
    )
    op.create_index("ix_TripRecords_added_by", "TripRecords", ["added_by"])

    op.create_table(
        "Mechanical_Tab",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_name", sa.String(length=100), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=True),
        sa.Column("event_details", sa.String(length=200), nullable=True),
        sa.Column("event_km", sa.Integer(), nullable=True),
        sa.Column("event_cost", sa.Float(), nullable=True),
        sa.Column("event_owner", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(["event_owner"], ["Users_Tab.email"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_owner", "event_name", name="uq_events_owner_name"),
    )
    op.create_index("ix_Mechanical_Tab_event_owner", "Mechanical_Tab", ["event_owner"])

    op.create_table(
        "Trip_Pictures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pic_name", sa.String(length=100), nullable=True),
        sa.Column("pic_location", sa.String(length=100), nullable=True),
        sa.Column("pic_blob", sa.LargeBinary(), nullable=True),
        sa.Column("pic_owner", sa.String(length=100), nullable=False),
        sa.Column("pic_posted_on", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["pic_owner"], ["Users_Tab.email"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_Trip_Pictures_pic_owner", "Trip_Pictures", ["pic_owner"])


def downgrade() -> None:
    op.drop_index("ix_Trip_Pictures_pic_owner", table_name="Trip_Pictures")
    op.drop_table("Trip_Pictures")
    op.drop_index("ix_Mechanical_Tab_event_owner", table_name="Mechanical_Tab")
    op.drop_table("Mechanical_Tab")
    op.drop_index("ix_TripRecords_added_by", table_name="TripRecords")
    op.drop_table("TripRecords")
    op.drop_index("ix_Users_Tab_email", table_name="Users_Tab")
    op.drop_table("Users_Tab")
