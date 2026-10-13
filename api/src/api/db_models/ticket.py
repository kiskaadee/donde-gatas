import uuid
from datetime import UTC, datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.base import Base


class TicketDB(Base):
    """
    SQLAlchemy model for crowdsourced status report tickets.
    """

    __tablename__ = "tickets"
    __table_args__ = (Index("idx_tickets_sculpture_status", "sculpture_id", "status"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sculpture_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sculptures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reported_status: Mapped[str] = mapped_column(String(50), nullable=False)

    # PostGIS spatial point for the reported location
    location = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False
    )

    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    reporter_trust_score: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(300), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    reporter = relationship("UserDB", back_populates="tickets")
    sculpture = relationship("SculptureDB", back_populates="tickets")
