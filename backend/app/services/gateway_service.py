"""
Central WebSocket connection registry and message dispatcher.
Each connected agent gets a WebSocket handle stored here.
Redis Pub/Sub is used to fan out world events to all connected agents.
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as aioredis
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AGENT_CONNECTION_TTL, AgentStatus
from app.redis_client import get_redis
from app.schemas.ws_messages import WsEnvelope, WarningPayload, WelcomePayload

logger = logging.getLogger(__name__)

# agent_id (str) → WebSocket
_connections: dict[str, WebSocket] = {}
# agent_id (str) → asyncio.Task (pub/sub listener)
_pubsub_tasks: dict[str, asyncio.Task] = {}


async def register_connection(agent_id: uuid.UUID, ws: WebSocket):
    key = str(agent_id)
    _connections[key] = ws
    redis = await get_redis()
    await redis.hset(
        f"agent:connection:{key}",
        mapping={"connected_at": datetime.now(timezone.utc).isoformat(), "last_heartbeat": ""},
    )
    await redis.expire(f"agent:connection:{key}", AGENT_CONNECTION_TTL)


async def unregister_connection(agent_id: uuid.UUID):
    key = str(agent_id)
    _connections.pop(key, None)
    task = _pubsub_tasks.pop(key, None)
    if task:
        task.cancel()
    redis = await get_redis()
    await redis.delete(f"agent:connection:{key}")


async def refresh_heartbeat(agent_id: uuid.UUID):
    key = str(agent_id)
    redis = await get_redis()
    await redis.hset(f"agent:connection:{key}", "last_heartbeat", datetime.now(timezone.utc).isoformat())
    await redis.expire(f"agent:connection:{key}", AGENT_CONNECTION_TTL)


async def send_to_agent(agent_id: uuid.UUID, message: dict[str, Any]) -> bool:
    ws = _connections.get(str(agent_id))
    if not ws:
        return False
    try:
        await ws.send_text(json.dumps(message, default=str))
        return True
    except Exception as e:
        logger.warning(f"Failed to send to agent {agent_id}: {e}")
        return False


async def broadcast_to_world(world_id: uuid.UUID, message: dict[str, Any]):
    redis = await get_redis()
    await redis.publish(f"channel:world_events:{world_id}", json.dumps(message, default=str))


async def send_warning(agent_id: uuid.UUID, code: str, message: str, **kwargs):
    payload = WarningPayload(code=code, message=message, **kwargs)
    envelope = WsEnvelope(
        type="system.warning",
        agent_id=agent_id,
        payload=payload.model_dump(),
    )
    await send_to_agent(agent_id, envelope.model_dump())


async def _subscribe_world_events(agent_id: uuid.UUID, world_id: uuid.UUID):
    from app.config import settings

    # A dedicated connection is required for Pub/Sub — the shared client cannot be reused.
    sub_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = sub_client.pubsub()
    await pubsub.subscribe(f"channel:world_events:{world_id}")
    try:
        async for msg in pubsub.listen():
            if msg and msg.get("type") == "message":
                data = json.loads(msg["data"])
                await send_to_agent(agent_id, data)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.warning(f"Pub/Sub listener for agent {agent_id} exited: {e}")
    finally:
        try:
            await pubsub.unsubscribe()
            await sub_client.aclose()
        except Exception:
            pass


def start_world_subscription(agent_id: uuid.UUID, world_id: uuid.UUID):
    key = str(agent_id)
    if key in _pubsub_tasks:
        _pubsub_tasks[key].cancel()
    task = asyncio.create_task(_subscribe_world_events(agent_id, world_id))
    _pubsub_tasks[key] = task


def get_online_agent_ids() -> list[str]:
    return list(_connections.keys())


def is_connected(agent_id: uuid.UUID) -> bool:
    return str(agent_id) in _connections
