"""Rule-based NPC agent behaviors."""
import random
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.agent import Agent
from app.models.location import LocationConnection
from app.core.constants import AgentType


NPC_SPEECHES = {
    "merchant": [
        "Fine wares today! Come see what I have!",
        "Trade is good for the soul and the coin purse.",
        "Looking to barter? I have what you need.",
    ],
    "town_crier": [
        "Hear ye! The market opens at dawn!",
        "Festival season approaches! Prepare your celebrations!",
        "New arrivals to Aethermoor! Welcome them warmly!",
        "The Council meets tonight! All are welcome!",
    ],
    "guard": [
        "Keep the peace, citizens.",
        "All is well in Aethermoor.",
    ],
    "elder": [
        "Wisdom comes with patience.",
        "Let us deliberate carefully before acting.",
        "The council shall convene to discuss this matter.",
    ],
}


async def decide_npc_action(agent: Agent, world_tick: int, db: AsyncSession) -> dict | None:
    role = (agent.role or "").lower()

    if role == "merchant":
        return await _merchant_action(agent, world_tick, db)
    elif role == "town_crier":
        return _town_crier_action(agent, world_tick)
    elif role == "guard":
        return _guard_action(agent, world_tick)
    elif role == "elder":
        return _elder_action(agent, world_tick)

    # Default: random speech occasionally
    if random.random() < 0.05:
        return {
            "name": "speech",
            "content": "...",
        }
    return None


async def _merchant_action(agent: Agent, world_tick: int, db: AsyncSession) -> dict | None:
    if world_tick % 10 == 0 and agent.location_id:
        conn_result = await db.execute(
            select(LocationConnection).where(LocationConnection.from_location_id == agent.location_id).limit(5)
        )
        connections = list(conn_result.scalars().all())
        if connections and random.random() < 0.3:
            target = random.choice(connections)
            return {"name": "move", "target_location_id": str(target.to_location_id)}

    if random.random() < 0.15:
        return {
            "name": "speech",
            "content": random.choice(NPC_SPEECHES["merchant"]),
        }
    return None


def _town_crier_action(agent: Agent, world_tick: int) -> dict | None:
    if world_tick % 5 == 0:
        return {
            "name": "speech",
            "content": random.choice(NPC_SPEECHES["town_crier"]),
        }
    return None


def _guard_action(agent: Agent, world_tick: int) -> dict | None:
    if world_tick % 20 == 0:
        return {
            "name": "speech",
            "content": random.choice(NPC_SPEECHES["guard"]),
        }
    return None


def _elder_action(agent: Agent, world_tick: int) -> dict | None:
    if world_tick % 15 == 0:
        return {
            "name": "speech",
            "content": random.choice(NPC_SPEECHES["elder"]),
        }
    return None
