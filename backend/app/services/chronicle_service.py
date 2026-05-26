"""Chronicle system: generates narrative history from world events."""
import uuid
import random
from jinja2 import Template
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.chronicle import ChronicleEntry
from app.models.event import Event

TEMPLATES = [
    "On tick {{ tick }}, {{ agent_name }} performed a {{ event_type }} at {{ location }}. The act was noted by those present.",
    "At tick {{ tick }}, the world witnessed {{ agent_name }} engaging in {{ event_type }} near {{ location }}.",
    "Chronicles record that around tick {{ tick }}, {{ event_type }} transpired near {{ location }}, with {{ agent_name }} at the center.",
    "Historians note that {{ agent_name }}'s {{ event_type }} at tick {{ tick }} near {{ location }} left a lasting impression.",
]


async def write_tick_summary(
    world_id: uuid.UUID,
    world_tick: int,
    db: AsyncSession,
):
    result = await db.execute(
        select(Event).where(
            Event.world_id == world_id,
            Event.world_tick >= world_tick - 10,
            Event.world_tick <= world_tick,
            Event.is_public == True,
        ).order_by(Event.world_tick.desc()).limit(5)
    )
    events = list(result.scalars().all())
    if not events:
        return

    agent_ids = list({str(e.source_agent_id) for e in events if e.source_agent_id})
    event_types = list({e.event_type for e in events})

    tpl = Template(random.choice(TEMPLATES))
    content = tpl.render(
        tick=world_tick,
        agent_name=f"Agent-{agent_ids[0][:8]}" if agent_ids else "Unknown",
        event_type=event_types[0] if event_types else "activity",
        location="Aethermoor",
    )

    entry = ChronicleEntry(
        world_id=world_id,
        world_tick=world_tick,
        entry_type="event_summary",
        title=f"Tick {world_tick} Chronicle",
        content=content,
        agents_mentioned=agent_ids[:5],
        source_event_ids=[str(e.id) for e in events[:5]],
    )
    db.add(entry)
    await db.flush()


async def get_chronicle(
    world_id: uuid.UUID,
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
) -> list[ChronicleEntry]:
    result = await db.execute(
        select(ChronicleEntry)
        .where(ChronicleEntry.world_id == world_id)
        .order_by(ChronicleEntry.world_tick.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())
