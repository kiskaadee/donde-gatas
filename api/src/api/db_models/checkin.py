import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.base import Base


class CheckInDB(Base):
    """
    SQLAlchemy model for user check-in captures.
    """

    __tablename__ = "check_ins"
    __table_args__ = (
        UniqueConstraint("user_id", "sculpture_id", name="uq_user_sculpture_checkin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sculpture_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sculptures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    photo_url: Mapped[str] = mapped_column(String(512), nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    # Relationships
    user = relationship("UserDB", back_populates="check_ins")
    sculpture = relationship("SculptureDB", back_populates="check_ins")
