import uuid
from sqlalchemy import String, Integer, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Relationship(Base):
    __tablename__ = "relationships"
    __table_args__ = (UniqueConstraint("agent_a_id", "agent_b_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_a_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_b_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rel_type: Mapped[str] = mapped_column(String(32), nullable=False, default="acquaintance")
    strength: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    formed_tick: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    last_interaction_tick: Mapped[int | None] = mapped_column(BigInteger)

    agent_a: Mapped["Agent"] = relationship("Agent", foreign_keys=[agent_a_id])
    agent_b: Mapped["Agent"] = relationship("Agent", foreign_keys=[agent_b_id])
