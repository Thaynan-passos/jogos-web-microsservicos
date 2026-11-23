from datetime import UTC, datetime

from app.db.base import Base
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class ConsumedRecoveryToken(Base):
    __tablename__ = "consumed_recovery_tokens"

    token_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    consumed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
