"""Builds world.observation packets for each agent every tick."""
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.agent import Agent
from app.models.location import Location, LocationConnection
from app.models.event import Event
from app.schemas.ws_messages import (
    ObservationPayload, AgentWorldState, NearbyAgentInfo,
    RecentEventInfo, AccessibleLocation,
)
from app.services.permission_service import get_available_actions


async def build_observation(agent: Agent, world_tick: int, db: AsyncSession) -> ObservationPayload:
    location_name = None
    nearby_agents: list[NearbyAgentInfo] = []
    recent_events: list[RecentEventInfo] = []
    accessible_locations: list[AccessibleLocation] = []

    if agent.location_id:
        loc_result = await db.execute(select(Location).where(Location.id == agent.location_id))
        location = loc_result.scalar_one_or_none()
        if location:
            location_name = location.name

        # Nearby agents at same location
        nearby_result = await db.execute(
            select(Agent).where(
                Agent.location_id == agent.location_id,
                Agent.id != agent.id,
                Agent.status != "offline",
            ).limit(20)
        )
        for a in nearby_result.scalars():
            nearby_agents.append(NearbyAgentInfo(
                agent_id=a.id,
                display_name=a.display_name,
                agent_type=a.agent_type,
                status=a.status,
            ))

        # Recent events at this location (last 5)
        events_result = await db.execute(
            select(Event).where(
                Event.location_id == agent.location_id,
                Event.world_tick >= world_tick - 5,
            ).order_by(Event.world_tick.desc()).limit(5)
        )
        for ev in events_result.scalars():
            content = ev.payload.get("content") if ev.payload else None
            source_name = str(ev.source_agent_id) if ev.source_agent_id else "System"
            recent_events.append(RecentEventInfo(
                event_type=ev.event_type,
                source=source_name,
                content=content,
            ))

        # Accessible locations (connected)
        conns_result = await db.execute(
            select(LocationConnection, Location)
            .join(Location, LocationConnection.to_location_id == Location.id)
            .where(LocationConnection.from_location_id == agent.location_id)
        )
        for conn, loc in conns_result:
            accessible_locations.append(AccessibleLocation(
                location_id=loc.id,
                name=loc.name,
                travel_cost=conn.travel_cost,
            ))

    available_actions = await get_available_actions(agent.permission_level)

    return ObservationPayload(
        tick=world_tick,
        agent=AgentWorldState(
            location_id=agent.location_id,
            location_name=location_name,
            reputation=agent.reputation,
            influence=agent.influence,
        ),
        nearby_agents=nearby_agents,
        recent_events=recent_events,
        available_actions=available_actions,
        locations_accessible=accessible_locations,
    )
