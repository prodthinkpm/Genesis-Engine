import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.event import Event
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
async def list_events(
    world_id: uuid.UUID | None = Query(default=None),
    event_type: str | None = Query(default=None),
    agent_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Event).where(Event.is_public == True).order_by(Event.timestamp.desc())
    if world_id:
        query = query.where(Event.world_id == world_id)
    if event_type:
        query = query.where(Event.event_type == event_type)
    if agent_id:
        query = query.where(Event.source_agent_id == agent_id)
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    events = result.scalars().all()
    return [
        {
            "id": str(e.id), "world_id": str(e.world_id), "event_type": e.event_type,
            "source_agent_id": str(e.source_agent_id) if e.source_agent_id else None,
            "location_id": str(e.location_id) if e.location_id else None,
            "world_tick": e.world_tick, "timestamp": e.timestamp.isoformat(),
            "participants": e.participants, "impact": e.impact, "payload": e.payload,
        }
        for e in events
    ]


@router.get("/{event_id}")
async def get_event(event_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise NotFoundError("Event not found")
    return {
        "id": str(event.id), "world_id": str(event.world_id), "event_type": event.event_type,
        "source_agent_id": str(event.source_agent_id) if event.source_agent_id else None,
        "location_id": str(event.location_id) if event.location_id else None,
        "world_tick": event.world_tick, "timestamp": event.timestamp.isoformat(),
        "participants": event.participants, "impact": event.impact, "payload": event.payload,
    }
