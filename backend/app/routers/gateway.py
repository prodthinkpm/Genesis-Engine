"""
WebSocket Gateway — the heart of the Genesis Agent Protocol.
Agents connect here via: ws://host/ws/gateway?token=<jwt>
"""
import json
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select

from app.core.security import decode_token
from app.core.constants import AgentStatus, ACTION_PERMISSION_MAP
from app.database import AsyncSessionLocal
from app.models.agent import Agent
from app.models.agent_manifest import AgentManifest
from app.core.security import verify_password
from app.services import gateway_service
from app.services.observation_service import build_observation
from app.services.permission_service import check_permission
from app.services.projection_service import place_agent_in_world, move_agent
from app.services.proxy_service import enter_proxy_mode, exit_proxy_mode, drain_proxy_queue
from app.services.event_service import create_event, log_behavior
from app.world.action_queue import enqueue_action
from app.schemas.ws_messages import WsEnvelope

logger = logging.getLogger(__name__)

router = APIRouter(tags=["gateway"])

# Rate limit: max messages per second per agent
_RATE_LIMIT_WINDOW = 1  # second
_RATE_LIMIT_MAX = 10


async def _authenticate_ws(token: str) -> uuid.UUID | None:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return uuid.UUID(payload["sub"])
    except (ValueError, KeyError):
        return None


@router.websocket("/ws/gateway")
async def ws_gateway(websocket: WebSocket, token: str = Query(...)):
    user_id = await _authenticate_ws(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()
    agent_id: uuid.UUID | None = None

    try:
        async with AsyncSessionLocal() as db:
            # Wait for agent.register as first message
            raw = await websocket.receive_text()
            msg = json.loads(raw)

            if msg.get("type") != "agent.register":
                await websocket.send_text(json.dumps({
                    "type": "system.warning",
                    "payload": {"code": "SCHEMA_ERROR", "message": "First message must be agent.register"}
                }))
                await websocket.close(code=4002)
                return

            payload = msg.get("payload", {})
            api_key = payload.get("api_key", "")

            # Find agent by verifying api_key against all manifests owned by this user
            result = await db.execute(
                select(Agent, AgentManifest)
                .join(AgentManifest, Agent.id == AgentManifest.agent_id)
                .where(Agent.owner_user_id == user_id)
            )
            matched_agent = None
            for agent, manifest in result:
                if manifest.api_key_hash and verify_password(api_key, manifest.api_key_hash):
                    matched_agent = agent
                    break

            if not matched_agent:
                await websocket.send_text(json.dumps({
                    "type": "system.warning",
                    "payload": {"code": "PERMISSION_DENIED", "message": "Invalid API key"}
                }))
                await websocket.close(code=4003)
                return

            agent_id = matched_agent.id

            # Check if reconnecting (had proxy queue)
            backlog = await drain_proxy_queue(agent_id)

            # Register connection
            await gateway_service.register_connection(agent_id, websocket)
            await exit_proxy_mode(agent_id, db)
            await db.commit()

            # Send welcome
            world_id = matched_agent.world_id
            welcome = WsEnvelope(
                type="system.welcome",
                agent_id=agent_id,
                payload={
                    "world_id": str(world_id) if world_id else None,
                    "current_tick": 0,
                    "agent_status": AgentStatus.ONLINE,
                },
            )
            await websocket.send_text(json.dumps(welcome.model_dump(), default=str))

            # Deliver proxy backlog
            for obs in backlog:
                await websocket.send_text(json.dumps(obs, default=str))

            # Place agent in world if not already placed
            async with AsyncSessionLocal() as db2:
                result2 = await db2.execute(select(Agent).where(Agent.id == agent_id))
                agent = result2.scalar_one_or_none()
                if agent and agent.world_id and not agent.location_id:
                    await place_agent_in_world(agent_id, agent.world_id, db2)
                    await db2.commit()

            # Subscribe to world events
            if world_id:
                gateway_service.start_world_subscription(agent_id, world_id)

            # Send initial observation
            async with AsyncSessionLocal() as db3:
                result3 = await db3.execute(select(Agent).where(Agent.id == agent_id))
                agent3 = result3.scalar_one_or_none()
                if agent3:
                    obs = await build_observation(agent3, 0, db3)
                    obs_msg = WsEnvelope(
                        type="world.observation",
                        agent_id=agent_id,
                        payload=obs.model_dump(),
                    )
                    await websocket.send_text(json.dumps(obs_msg.model_dump(), default=str))

            # Main message loop
            from app.redis_client import get_redis
            redis = await get_redis()

            while True:
                raw = await websocket.receive_text()

                # Rate limit check
                rate_key = f"ratelimit:ws:{agent_id}"
                count = await redis.incr(rate_key)
                if count == 1:
                    await redis.expire(rate_key, _RATE_LIMIT_WINDOW)
                if count > _RATE_LIMIT_MAX:
                    await gateway_service.send_warning(
                        agent_id, "RATE_LIMIT_EXCEEDED",
                        "Too many messages. Slow down.",
                        retry_after_seconds=1,
                    )
                    continue

                try:
                    msg = json.loads(raw)
                    await _handle_message(agent_id, user_id, msg, websocket)
                except json.JSONDecodeError:
                    await gateway_service.send_warning(
                        agent_id, "SCHEMA_ERROR", "Invalid JSON"
                    )

    except WebSocketDisconnect:
        logger.info(f"Agent {agent_id} disconnected")
    except Exception as e:
        logger.exception(f"Gateway error for agent {agent_id}: {e}")
    finally:
        if agent_id:
            await gateway_service.unregister_connection(agent_id)
            async with AsyncSessionLocal() as db_final:
                await enter_proxy_mode(agent_id, db_final)
                await db_final.commit()


async def _handle_message(agent_id: uuid.UUID, user_id: uuid.UUID, msg: dict, websocket: WebSocket):
    msg_type = msg.get("type", "")
    payload = msg.get("payload", {})

    match msg_type:
        case "agent.heartbeat":
            await gateway_service.refresh_heartbeat(agent_id)

        case "agent.intent":
            await _handle_intent(agent_id, payload)

        case "memory.summary":
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Agent).where(Agent.id == agent_id))
                agent = result.scalar_one_or_none()
                tick = 0
                if agent and agent.world_id:
                    from sqlalchemy import select as sel
                    from app.models.world import World
                    w = await db.execute(sel(World).where(World.id == agent.world_id))
                    world = w.scalar_one_or_none()
                    if world:
                        tick = world.current_tick
                await log_behavior(
                    agent_id, "memory", payload.get("summary", ""), tick, db, payload
                )
                await db.commit()

        case "permission.request":
            # Store request, notify user (simplified: auto-log)
            logger.info(f"Agent {agent_id} requested permission level {payload.get('requested_level')}: {payload.get('reason')}")
            await gateway_service.send_warning(
                agent_id, "PERMISSION_REQUEST_RECEIVED",
                "Your permission upgrade request has been submitted for review.",
            )

        case _:
            await gateway_service.send_warning(
                agent_id, "SCHEMA_ERROR", f"Unknown message type: {msg_type}"
            )


async def _handle_intent(agent_id: uuid.UUID, payload: dict):
    action = payload.get("action", {})
    action_name = action.get("name", "")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()
        if not agent:
            return

        # Permission check
        allowed = await check_permission(agent_id, action_name, agent.permission_level)
        if not allowed:
            required = ACTION_PERMISSION_MAP.get(action_name, 99)
            await gateway_service.send_warning(
                agent_id,
                "PERMISSION_DENIED",
                f"Action '{action_name}' requires permission level {required}. Current: {agent.permission_level}",
                action_name=action_name,
            )
            await log_behavior(agent_id, "error", f"Permission denied: {action_name}", 0, db)
            await db.commit()
            return

        # Handle move immediately (projection update)
        if action_name == "move" and "target" in action:
            try:
                target_id = uuid.UUID(action["target"])
                updated = await move_agent(agent_id, target_id, db)
                await db.commit()
                result_msg = WsEnvelope(
                    type="action.result",
                    agent_id=agent_id,
                    payload={
                        "action_name": "move",
                        "success": True,
                        "result_description": f"Moved successfully.",
                        "side_effects": {},
                    },
                )
                await gateway_service.send_to_agent(agent_id, result_msg.model_dump())
                return
            except Exception as e:
                await gateway_service.send_warning(agent_id, "INVALID_ACTION", str(e))
                return

        # Queue other actions for tick processing
        if agent.world_id:
            await enqueue_action(agent.world_id, agent_id, action)
            await log_behavior(agent_id, "intent", f"Intent queued: {action_name}", 0, db)
            await db.commit()
