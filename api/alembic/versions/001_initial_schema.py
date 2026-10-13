"""initial schema with postgis and pgvector

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-10-13 07:05:00.000000

"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Enable required PostgreSQL extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Users table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("trust_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # 3. Sculptures table
    op.create_table(
        "sculptures",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("artist", sa.String(length=255), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("audio_url", sa.String(length=512), nullable=True),
        sa.Column("unlocked_content", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="on-site"),
        sa.Column(
            "location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"
            ),
            nullable=False,
        ),
        sa.Column("embedding", Vector(1280), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create HNSW index for vector cosine similarity
    op.execute(
        "CREATE INDEX idx_sculptures_embedding ON sculptures USING hnsw (embedding vector_cosine_ops);"
    )

    # 4. Check-ins table
    op.create_table(
        "check_ins",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("sculpture_id", sa.UUID(), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("photo_url", sa.String(length=512), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["sculpture_id"], ["sculptures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "sculpture_id", name="uq_user_sculpture_checkin"),
    )
    op.create_index(op.f("ix_check_ins_sculpture_id"), "check_ins", ["sculpture_id"], unique=False)
    op.create_index(op.f("ix_check_ins_user_id"), "check_ins", ["user_id"], unique=False)

    # 5. Tickets table
    op.create_table(
        "tickets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("reporter_id", sa.UUID(), nullable=False),
        sa.Column("sculpture_id", sa.UUID(), nullable=False),
        sa.Column("reported_status", sa.String(length=50), nullable=False),
        sa.Column(
            "location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"
            ),
            nullable=False,
        ),
        sa.Column("photo_url", sa.String(length=512), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("reporter_trust_score", sa.Float(), nullable=False),
        sa.Column("notes", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["sculpture_id"], ["sculptures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reporter_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tickets_reporter_id"), "tickets", ["reporter_id"], unique=False)
    op.create_index(op.f("ix_tickets_sculpture_id"), "tickets", ["sculpture_id"], unique=False)
    op.create_index(
        "idx_tickets_sculpture_status", "tickets", ["sculpture_id", "status"], unique=False
    )


def downgrade() -> None:
    op.drop_table("tickets")
    op.drop_table("check_ins")
    op.execute("DROP INDEX IF EXISTS idx_sculptures_embedding;")
    op.drop_table("sculptures")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
