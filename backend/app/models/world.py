import uuid
from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class World(Base):
    __tablename__ = "worlds"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    tick_interval: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    current_tick: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    max_agents: Mapped[int] = mapped_column(Integer, nullable=False, default=150)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    locations: Mapped[list["Location"]] = relationship("Location", back_populates="world", lazy="select")
    agents: Mapped[list["Agent"]] = relationship("Agent", back_populates="world", lazy="select")
    organizations: Mapped[list["Organization"]] = relationship("Organization", back_populates="world", lazy="select")
