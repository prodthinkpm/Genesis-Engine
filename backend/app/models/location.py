import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy import JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    world_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    location_type: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512))
    x_coord: Mapped[float] = mapped_column(Float, nullable=False)
    y_coord: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    world: Mapped["World"] = relationship("World", back_populates="locations")
    agents: Mapped[list["Agent"]] = relationship("Agent", back_populates="location", lazy="select")

    outgoing_connections: Mapped[list["LocationConnection"]] = relationship(
        "LocationConnection",
        foreign_keys="LocationConnection.from_location_id",
        back_populates="from_location",
        lazy="select",
    )


class LocationConnection(Base):
    __tablename__ = "location_connections"

    from_location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("locations.id"), primary_key=True
    )
    to_location_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("locations.id"), primary_key=True
    )
    travel_cost: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    from_location: Mapped["Location"] = relationship(
        "Location", foreign_keys=[from_location_id], back_populates="outgoing_connections"
    )
    to_location: Mapped["Location"] = relationship(
        "Location", foreign_keys=[to_location_id]
    )
