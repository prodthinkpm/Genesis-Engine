import uuid
from datetime import datetime
from sqlalchemy import String, BigInteger, ForeignKey, DateTime, func, Text
from sqlalchemy import JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ChronicleEntry(Base):
    __tablename__ = "chronicle_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    world_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    world_tick: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    entry_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    agents_mentioned: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    source_event_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    world: Mapped["World"] = relationship("World")
