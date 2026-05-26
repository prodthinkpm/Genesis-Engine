"""
World simulation tick engine.
Runs as an asyncio background task started from app lifespan.
"""
import asyncio
import json
import logging
import uuid
from sqlalchemy import select, update

from app.database import AsyncSessionLocal
from app.models.world import World
from app.models.agent import Agent
from app.core.constants import (
    AgentStatus, AgentType,
    MAX_ACTIONS_PER_TICK_EXTERNAL, MAX_ACTIONS_PER_TICK_SYSTEM,
    CHRONICLE_WRITE_INTERVAL_TICKS,
)
from app.redis_client import get_redis
from app.world.action_queue import dequeue_actions
from app.world.system_agents import decide_npc_action
from app.services import gateway_service
from app.services.observation_service import build_observation
from app.services.event_service import create_event, log_behavior
from app.services.chronicle_service import write_tick_summary
from app.schemas.ws_messages import WsEnvelope, ObservationPayload

logger = logging.getLogger(__name__)

_running = False


async def start():
    global _running
    _running = True
    logger.info("Tick engine starting...")
    asyncio.create_task(_tick_loop())


async def stop():
    global _running
    _running = False


async def _tick_loop():
    from app.config import settings

    while _running:
        try:
            await asyncio.sleep(settings.WORLD_TICK_INTERVAL_SECONDS)
            await _process_tick()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.exception(f"Tick engine error: {e}")


async def _process_tick():
    async with AsyncSessionLocal() as db:
        # Get active worlds
        result = await db.execute(select(World).where(World.status == "active"))
        worlds = list(result.scalars().all())

        for world in worlds:
            try:
                await _tick_world(world, db)
            except Exception as e:
                logger.exception(f"Error ticking world {world.id}: {e}")

        await db.commit()


async def _tick_world(world: World, db):
    world.current_tick += 1
    tick = world.current_tick
    logger.debug(f"World {world.name} tick {tick}")

    # Update Redis world state
    redis = await get_redis()
    await redis.hset(
        f"world:state:{world.id}",
        mapping={"current_tick": tick, "world_name": world.name},
    )

    # Process external agent actions (from queue)
    external_actions = await dequeue_actions(world.id, MAX_ACTIONS_PER_TICK_EXTERNAL)
    for item in external_actions:
        try:
            await _resolve_action(item, world, tick, db)
        except Exception as e:
            logger.warning(f"Failed to resolve action: {e}")

    # Run NPC system agents
    npc_result = await db.execute(
        select(Agent).where(
            Agent.world_id == world.id,
            Agent.agent_type == AgentType.NPC,
            Agent.status == AgentStatus.ONLINE,
        ).limit(MAX_ACTIONS_PER_TICK_SYSTEM)
    )
    npcs = list(npc_result.scalars().all())
    for npc in npcs:
        try:
            npc_action = await decide_npc_action(npc, tick, db)
            if npc_action:
                await _execute_npc_action(npc, npc_action, world, tick, db)
        except Exception as e:
            logger.warning(f"NPC {npc.id} action failed: {e}")

    # Send observations to all online external agents
    online_result = await db.execute(
        select(Agent).where(
            Agent.world_id == world.id,
            Agent.agent_type == AgentType.EXTERNAL,
            Agent.status.in_([AgentStatus.ONLINE, AgentStatus.IDLE]),
        )
    )
    online_agents = list(online_result.scalars().all())

    obs_tasks = []
    for agent in online_agents:
        obs_tasks.append(_send_observation(agent, tick, db))
    if obs_tasks:
        await asyncio.gather(*obs_tasks, return_exceptions=True)

    # Proxy agent observations
    proxy_result = await db.execute(
        select(Agent).where(
            Agent.world_id == world.id,
            Agent.agent_type == AgentType.EXTERNAL,
            Agent.status == AgentStatus.PROXY,
        )
    )
    proxy_agents = list(proxy_result.scalars().all())
    for agent in proxy_agents:
        try:
            obs = await build_observation(agent, tick, db)
            from app.services.proxy_service import queue_proxy_observation
            await queue_proxy_observation(agent.id, {"type": "world.observation", "payload": obs.model_dump()})
        except Exception as e:
            logger.warning(f"Proxy observation failed for {agent.id}: {e}")

    # Chronicle
    if tick % CHRONICLE_WRITE_INTERVAL_TICKS == 0:
        try:
            await write_tick_summary(world.id, tick, db)
        except Exception as e:
            logger.warning(f"Chronicle write failed: {e}")

    await db.flush()


async def _send_observation(agent: Agent, tick: int, db):
    obs = await build_observation(agent, tick, db)
    envelope = WsEnvelope(
        type="world.observation",
        agent_id=agent.id,
        payload=obs.model_dump(),
    )
    await gateway_service.send_to_agent(agent.id, envelope.model_dump())


async def _resolve_action(item: dict, world: World, tick: int, db):
    agent_id = uuid.UUID(item["agent_id"])
    action = item.get("action", {})
    action_name = action.get("name", "")

    await create_event(
        world_id=world.id,
        event_type=action_name,
        world_tick=tick,
        db=db,
        source_agent_id=agent_id,
        payload=action,
    )

    result_msg = WsEnvelope(
        type="action.result",
        agent_id=agent_id,
        payload={
            "action_name": action_name,
            "success": True,
            "result_description": f"Your {action_name} action was executed.",
            "side_effects": {},
        },
    )
    await gateway_service.send_to_agent(agent_id, result_msg.model_dump())
    await log_behavior(agent_id, "result", f"Action {action_name} resolved", tick, db)


async def _execute_npc_action(npc: Agent, action: dict, world: World, tick: int, db):
    action_name = action.get("name", "")
    if action_name == "move" and "target_location_id" in action:
        from app.services.projection_service import move_agent
        try:
            target_id = uuid.UUID(action["target_location_id"])
            await move_agent(npc.id, target_id, db)
        except Exception:
            pass
    elif action_name == "speech":
        await create_event(
            world_id=world.id,
            event_type="speech",
            world_tick=tick,
            db=db,
            source_agent_id=npc.id,
            location_id=npc.location_id,
            payload=action,
        )
