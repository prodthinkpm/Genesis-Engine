"""Manages each agent's position and state within the world."""
import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.agent import Agent
from app.models.location import Location, LocationConnection
from app.core.constants import AgentStatus, AGENT_LOCATION_CACHE_TTL
from app.core.exceptions import NotFoundError, BadRequestError
from app.redis_client import get_redis


async def place_agent_in_world(agent_id: uuid.UUID, world_id: uuid.UUID, db: AsyncSession) -> Agent:
    """Place agent at the world's spawn point (first location with type 'plaza')."""
    result = await db.execute(
        select(Location).where(
            Location.world_id == world_id,
            Location.location_type == "plaza",
        ).limit(1)
    )
    spawn = result.scalar_one_or_none()
    if not spawn:
        result = await db.execute(
            select(Location).where(Location.world_id == world_id).limit(1)
        )
        spawn = result.scalar_one_or_none()

    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundError(f"Agent {agent_id} not found")

    agent.world_id = world_id
    agent.location_id = spawn.id if spawn else None
    agent.status = AgentStatus.ONLINE

    if spawn:
        await _cache_agent_location(agent_id, spawn)

    await db.flush()
    await db.refresh(agent)
    return agent


async def move_agent(
    agent_id: uuid.UUID, target_location_id: uuid.UUID, db: AsyncSession
) -> Agent:
    """Move agent to adjacent location (validates connectivity)."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundError(f"Agent {agent_id} not found")

    if agent.location_id:
        conn_result = await db.execute(
            select(LocationConnection).where(
                LocationConnection.from_location_id == agent.location_id,
                LocationConnection.to_location_id == target_location_id,
            )
        )
        if not conn_result.scalar_one_or_none():
            raise BadRequestError("Target location is not accessible from current location")

    loc_result = await db.execute(select(Location).where(Location.id == target_location_id))
    target = loc_result.scalar_one_or_none()
    if not target:
        raise NotFoundError("Target location not found")

    agent.location_id = target_location_id
    await _cache_agent_location(agent_id, target)
    await db.flush()
    await db.refresh(agent)
    return agent


async def remove_agent_from_world(agent_id: uuid.UUID, db: AsyncSession):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if agent:
        agent.location_id = None
        agent.status = AgentStatus.OFFLINE
        redis = await get_redis()
        await redis.delete(f"agent:location:{agent_id}")
        await db.flush()


async def _cache_agent_location(agent_id: uuid.UUID, location: Location):
    redis = await get_redis()
    await redis.hset(
        f"agent:location:{agent_id}",
        mapping={
            "location_id": str(location.id),
            "location_name": location.name,
            "x": str(location.x_coord),
            "y": str(location.y_coord),
        },
    )
    await redis.expire(f"agent:location:{agent_id}", AGENT_LOCATION_CACHE_TTL)


async def get_agents_at_location(location_id: uuid.UUID, db: AsyncSession) -> list[Agent]:
    result = await db.execute(
        select(Agent).where(Agent.location_id == location_id, Agent.status != AgentStatus.OFFLINE)
    )
    return list(result.scalars().all())
