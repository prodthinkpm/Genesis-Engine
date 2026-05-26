"""Offline proxy mode: keeps disconnected agents alive in the world."""
import asyncio
import json
import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.constants import AgentStatus, PROXY_QUEUE_MAX_SIZE
from app.models.agent import Agent
from app.redis_client import get_redis

logger = logging.getLogger(__name__)


async def enter_proxy_mode(agent_id: uuid.UUID, db: AsyncSession):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if agent:
        agent.status = AgentStatus.PROXY
        await db.flush()


async def exit_proxy_mode(agent_id: uuid.UUID, db: AsyncSession):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if agent:
        agent.status = AgentStatus.ONLINE
        await db.flush()


async def queue_proxy_observation(agent_id: uuid.UUID, observation: dict):
    redis = await get_redis()
    key = f"proxy:queue:{agent_id}"
    await redis.lpush(key, json.dumps(observation, default=str))
    await redis.ltrim(key, 0, PROXY_QUEUE_MAX_SIZE - 1)


async def drain_proxy_queue(agent_id: uuid.UUID) -> list[dict]:
    redis = await get_redis()
    key = f"proxy:queue:{agent_id}"
    items = await redis.lrange(key, 0, -1)
    if items:
        await redis.delete(key)
    return [json.loads(item) for item in reversed(items)]
