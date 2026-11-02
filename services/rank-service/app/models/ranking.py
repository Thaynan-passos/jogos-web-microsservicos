import uuid
from datetime import UTC, datetime

from app.db.base import Base
from sqlalchemy import DateTime, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class RankingEntry(Base):
    __tablename__ = "rank_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, index=True
    )
    username: Mapped[str] = mapped_column(String(50))
    game_slug: Mapped[str] = mapped_column(String(50), index=True)
    score: Mapped[int] = mapped_column(Integer)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    achieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    matches_played: Mapped[int] = mapped_column(Integer, default=1)
    win_rate: Mapped[str] = mapped_column(String(10), default="100%")
    __table_args__ = (
        Index("uq_rank_user_game", func.lower(username), game_slug, unique=True),
    )
