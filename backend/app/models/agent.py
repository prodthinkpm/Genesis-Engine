import uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    world_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("worlds.id", ondelete="SET NULL"), index=True
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL")
    )

    agent_type: Mapped[str] = mapped_column(String(32), nullable=False, default="external")
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    bio: Mapped[str | None] = mapped_column(String(1024))

    status: Mapped[str] = mapped_column(String(16), nullable=False, default="offline", index=True)
    role: Mapped[str | None] = mapped_column(String(64))

    reputation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    influence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    permission_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User"] = relationship("User", back_populates="agents")
    world: Mapped["World | None"] = relationship("World", back_populates="agents")
    location: Mapped["Location | None"] = relationship("Location", back_populates="agents")
    manifest: Mapped["AgentManifest | None"] = relationship(
        "AgentManifest", back_populates="agent", uselist=False, lazy="select"
    )
