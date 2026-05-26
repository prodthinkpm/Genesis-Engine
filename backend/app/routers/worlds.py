import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.world import World
from app.models.location import Location, LocationConnection
from app.models.agent import Agent
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/worlds", tags=["worlds"])


@router.get("")
async def list_worlds(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(World).where(World.status == "active"))
    worlds = result.scalars().all()
    return [
        {
            "id": str(w.id), "name": w.name, "description": w.description,
            "status": w.status, "current_tick": w.current_tick, "max_agents": w.max_agents,
        }
        for w in worlds
    ]


@router.get("/{world_id}")
async def get_world(world_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(World).where(World.id == world_id))
    world = result.scalar_one_or_none()
    if not world:
        raise NotFoundError("World not found")

    agent_count = await db.execute(
        select(Agent).where(Agent.world_id == world_id, Agent.status != "offline")
    )
    online = len(list(agent_count.scalars().all()))

    return {
        "id": str(world.id), "name": world.name, "description": world.description,
        "status": world.status, "current_tick": world.current_tick,
        "max_agents": world.max_agents, "online_agents": online,
        "tick_interval": world.tick_interval,
    }


@router.get("/{world_id}/agents")
async def list_world_agents(world_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Agent).where(Agent.world_id == world_id, Agent.status != "offline").limit(100)
    )
    return [
        {"id": str(a.id), "display_name": a.display_name, "status": a.status,
         "agent_type": a.agent_type, "location_id": str(a.location_id) if a.location_id else None}
        for a in result.scalars()
    ]


@router.get("/{world_id}/locations")
async def list_locations(world_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Location).where(Location.world_id == world_id))
    return [
        {"id": str(l.id), "name": l.name, "location_type": l.location_type,
         "x": l.x_coord, "y": l.y_coord, "capacity": l.capacity}
        for l in result.scalars()
    ]


@router.get("/{world_id}/map")
async def get_map(world_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    loc_result = await db.execute(select(Location).where(Location.world_id == world_id))
    locations = list(loc_result.scalars().all())
    loc_ids = {l.id for l in locations}

    conn_result = await db.execute(
        select(LocationConnection).where(
            LocationConnection.from_location_id.in_(loc_ids)
        )
    )
    connections = list(conn_result.scalars().all())

    return {
        "nodes": [
            {"id": str(l.id), "name": l.name, "type": l.location_type, "x": l.x_coord, "y": l.y_coord}
            for l in locations
        ],
        "edges": [
            {"from": str(c.from_location_id), "to": str(c.to_location_id), "cost": c.travel_cost}
            for c in connections
        ],
    }
