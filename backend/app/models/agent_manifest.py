import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy import JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AgentManifest(Base):
    __tablename__ = "agent_manifests"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True
    )
    runtime: Mapped[str] = mapped_column(String(64), nullable=False, default="python")
    connector_version: Mapped[str] = mapped_column(String(16), nullable=False, default="0.1")
    capabilities: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    allowed_actions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    callback_url: Mapped[str | None] = mapped_column(String(512))
    api_key_hash: Mapped[str | None] = mapped_column(String(255))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    agent: Mapped["Agent"] = relationship("Agent", back_populates="manifest")
