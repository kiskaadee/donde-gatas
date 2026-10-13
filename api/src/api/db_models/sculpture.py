import uuid
from datetime import UTC, datetime

from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.base import Base


class SculptureDB(Base):
    """
    SQLAlchemy model for cat sculptures (The Oracle SSOT).
    """

    __tablename__ = "sculptures"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    artist: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    unlocked_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="on-site", nullable=False)

    # PostGIS spatial point (SRID 4326: WGS84)
    location = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False
    )

    # pgvector 1280-dimension embedding (MobileNetV2 feature vector)
    embedding = mapped_column(Vector(1280), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    check_ins = relationship("CheckInDB", back_populates="sculpture", cascade="all, delete-orphan")
    tickets = relationship("TicketDB", back_populates="sculpture", cascade="all, delete-orphan")
