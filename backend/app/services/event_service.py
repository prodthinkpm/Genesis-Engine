"""Event creation, persistence, and propagation."""
import uuid
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.event import Event
from app.models.agent import Agent
from app.models.location import LocationConnection
from app.models.relationship import Relationship
from app.models.behavior_log import BehaviorLog
from app.core.constants import LogType
from app.redis_client import get_redis
from app.services import gateway_service
from app.schemas.ws_messages import WsEnvelope, EventNotificationPayload

logger = logging.getLogger(__name__)

# Impact config per event type
EVENT_IMPACT = {
    "speech": {"reputation_delta": 1},
    "trade": {"reputation_delta": 2, "influence_delta": 1},
    "vote": {"influence_delta": 2},
    "join_org": {"reputation_delta": 1, "influence_delta": 1},
    "brawl": {"reputation_delta": -3},
    "festival_start": {"influence_delta": 1},
}


async def create_event(
    world_id: uuid.UUID,
    event_type: str,
    world_tick: int,
    db: AsyncSession,
    source_agent_id: uuid.UUID | None = None,
    location_id: uuid.UUID | None = None,
    participants: list[str] | None = None,
    payload: dict | None = None,
    is_public: bool = True,
) -> Event:
    impact = EVENT_IMPACT.get(event_type, {})

    event = Event(
        world_id=world_id,
        event_type=event_type,
        source_agent_id=source_agent_id,
        location_id=location_id,
        world_tick=world_tick,
        participants=participants or [],
        impact=impact,
        payload=payload or {},
        is_public=is_public,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)

    if source_agent_id and impact:
        await _apply_impact(source_agent_id, impact, db)

    await _publish_event(world_id, event, db)
    return event


async def _apply_impact(agent_id: uuid.UUID, impact: dict, db: AsyncSession):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        return
    agent.reputation += impact.get("reputation_delta", 0)
    agent.influence += impact.get("influence_delta", 0)
    await db.flush()


async def _publish_event(world_id: uuid.UUID, event: Event, db: AsyncSession):
    """Publish event to Redis Pub/Sub and notify agents in the same location."""
    redis = await get_redis()
    event_data = {
        "type": "event.notification",
        "agent_id": None,
        "payload": {
            "event_id": str(event.id),
            "event_type": event.event_type,
            "location": str(event.location_id) if event.location_id else None,
            "description": _describe_event(event),
            "can_participate": event.event_type in ("festival_start", "vote", "join_event"),
        },
    }
    await redis.publish(f"channel:world_events:{world_id}", json.dumps(event_data, default=str))


def _describe_event(event: Event) -> str:
    payload = event.payload or {}
    content = payload.get("content", "")
    match event.event_type:
        case "speech":
            return f"Agent spoke: {content}"
        case "move":
            return f"Agent moved to {payload.get('target_location', 'unknown')}"
        case "trade":
            return "A trade was conducted"
        case "vote":
            return f"Vote cast on: {content}"
        case "festival_start":
            return f"Festival has begun: {content}"
        case "brawl":
            return "A brawl broke out!"
        case _:
            return f"{event.event_type} event occurred"


async def log_behavior(
    agent_id: uuid.UUID,
    log_type: str,
    message: str,
    world_tick: int,
    db: AsyncSession,
    payload: dict | None = None,
):
    log = BehaviorLog(
        agent_id=agent_id,
        world_tick=world_tick,
        log_type=log_type,
        message=message,
        payload=payload or {},
    )
    db.add(log)
    await db.flush()
