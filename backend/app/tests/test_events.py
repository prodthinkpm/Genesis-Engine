"""Integration tests for event creation, impact, and propagation."""
import uuid
import json
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.world import World
from app.models.agent import Agent
from app.models.location import Location
from app.models.event import Event
from app.core.constants import AgentType, AgentStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _make_user(db: AsyncSession, tag: str = "ev") -> "User":
    from app.models.user import User
    from app.core.security import hash_password

    u = User(
        email=f"{tag}@events.test",
        username=tag,
        password_hash=hash_password("pw"),
    )
    db.add(u)
    await db.flush()
    await db.refresh(u)
    return u


async def _make_world(db: AsyncSession, name: str = "EventWorld") -> World:
    w = World(name=name, status="active", tick_interval=30, max_agents=100)
    db.add(w)
    await db.flush()
    await db.refresh(w)
    return w


async def _make_location(db: AsyncSession, world: World, name: str = "Plaza") -> Location:
    loc = Location(
        world_id=world.id,
        name=name,
        location_type="plaza",
        x_coord=0.5,
        y_coord=0.5,
        capacity=50,
    )
    db.add(loc)
    await db.flush()
    await db.refresh(loc)
    return loc


async def _make_agent(
    db: AsyncSession,
    user: "User",
    world: World,
    loc: Location | None = None,
    name: str = "TestAgent",
) -> Agent:
    a = Agent(
        owner_user_id=user.id,
        world_id=world.id,
        location_id=loc.id if loc else None,
        display_name=name,
        agent_type=AgentType.EXTERNAL,
        status=AgentStatus.ONLINE,
        permission_level=2,
        reputation=10,
        influence=5,
    )
    db.add(a)
    await db.flush()
    await db.refresh(a)
    return a


# ---------------------------------------------------------------------------
# Event creation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_speech_event(db_session: AsyncSession, mock_redis):
    """create_event() persists a speech event to the database."""
    from app.services.event_service import create_event

    user = await _make_user(db_session, "speech_user")
    world = await _make_world(db_session, "SpeechWorld")
    loc = await _make_location(db_session, world)
    agent = await _make_agent(db_session, user, world, loc, "Speaker")

    event = await create_event(
        world_id=world.id,
        event_type="speech",
        world_tick=1,
        db=db_session,
        source_agent_id=agent.id,
        location_id=loc.id,
        payload={"content": "Hello, Aethermoor!"},
    )

    assert event.id is not None
    assert event.event_type == "speech"
    assert event.world_tick == 1
    assert event.source_agent_id == agent.id
    assert event.payload["content"] == "Hello, Aethermoor!"

    # Verify it landed in DB
    db_event = (await db_session.execute(
        select(Event).where(Event.id == event.id)
    )).scalar_one()
    assert db_event.event_type == "speech"


@pytest.mark.asyncio
async def test_create_event_without_source(db_session: AsyncSession, mock_redis):
    """System events with no source_agent_id are valid."""
    from app.services.event_service import create_event

    user = await _make_user(db_session, "nosrc_user")
    world = await _make_world(db_session, "NoSrcWorld")

    event = await create_event(
        world_id=world.id,
        event_type="festival_start",
        world_tick=5,
        db=db_session,
        payload={"content": "Grand Festival"},
    )

    assert event.source_agent_id is None
    assert event.event_type == "festival_start"


# ---------------------------------------------------------------------------
# Impact calculation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_speech_event_increases_reputation(db_session: AsyncSession, mock_redis):
    """speech event applies +1 reputation to the source agent."""
    from app.services.event_service import create_event

    user = await _make_user(db_session, "rep_user")
    world = await _make_world(db_session, "RepWorld")
    loc = await _make_location(db_session, world)
    agent = await _make_agent(db_session, user, world, loc, "Orator")
    initial_rep = agent.reputation

    await create_event(
        world_id=world.id,
        event_type="speech",
        world_tick=1,
        db=db_session,
        source_agent_id=agent.id,
        location_id=loc.id,
        payload={"content": "Make Aethermoor great again!"},
    )
    await db_session.flush()
    await db_session.refresh(agent)

    assert agent.reputation == initial_rep + 1


@pytest.mark.asyncio
async def test_trade_event_increases_reputation_and_influence(db_session: AsyncSession, mock_redis):
    """trade event applies +2 reputation and +1 influence."""
    from app.services.event_service import create_event

    user = await _make_user(db_session, "trade_user")
    world = await _make_world(db_session, "TradeWorld")
    loc = await _make_location(db_session, world)
    agent = await _make_agent(db_session, user, world, loc, "Merchant")
    init_rep = agent.reputation
    init_inf = agent.influence

    await create_event(
        world_id=world.id,
        event_type="trade",
        world_tick=2,
        db=db_session,
        source_agent_id=agent.id,
        location_id=loc.id,
        payload={"item": "iron_ore", "quantity": 10},
    )
    await db_session.flush()
    await db_session.refresh(agent)

    assert agent.reputation == init_rep + 2
    assert agent.influence == init_inf + 1


@pytest.mark.asyncio
async def test_brawl_event_decreases_reputation(db_session: AsyncSession, mock_redis):
    """brawl event applies -3 reputation."""
    from app.services.event_service import create_event

    user = await _make_user(db_session, "brawl_user")
    world = await _make_world(db_session, "BrawlWorld")
    loc = await _make_location(db_session, world)
    agent = await _make_agent(db_session, user, world, loc, "Thug")
    init_rep = agent.reputation

    await create_event(
        world_id=world.id,
        event_type="brawl",
        world_tick=3,
        db=db_session,
        source_agent_id=agent.id,
        location_id=loc.id,
    )
    await db_session.flush()
    await db_session.refresh(agent)

    assert agent.reputation == init_rep - 3


@pytest.mark.asyncio
async def test_unknown_event_type_has_no_impact(db_session: AsyncSession, mock_redis):
    """Events not in EVENT_IMPACT dict do not change agent stats."""
    from app.services.event_service import create_event

    user = await _make_user(db_session, "noop_user")
    world = await _make_world(db_session, "NoopWorld")
    agent = await _make_agent(db_session, user, world, None, "NoopAgent")
    init_rep = agent.reputation
    init_inf = agent.influence

    await create_event(
        world_id=world.id,
        event_type="custom_unknown_type",
        world_tick=1,
        db=db_session,
        source_agent_id=agent.id,
    )
    await db_session.flush()
    await db_session.refresh(agent)

    assert agent.reputation == init_rep
    assert agent.influence == init_inf


# ---------------------------------------------------------------------------
# Behavior logging
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_log_behavior_persists(db_session: AsyncSession):
    """log_behavior() writes a BehaviorLog entry."""
    from app.services.event_service import log_behavior
    from app.models.behavior_log import BehaviorLog

    user = await _make_user(db_session, "log_user")
    world = await _make_world(db_session, "LogWorld")
    agent = await _make_agent(db_session, user, world, None, "Logger")

    await log_behavior(
        agent_id=agent.id,
        log_type="action",
        message="Test log entry",
        world_tick=7,
        db=db_session,
        payload={"detail": "unit test"},
    )
    await db_session.flush()

    log = (await db_session.execute(
        select(BehaviorLog).where(BehaviorLog.agent_id == agent.id)
    )).scalar_one()

    assert log.message == "Test log entry"
    assert log.world_tick == 7
    assert log.payload == {"detail": "unit test"}


# ---------------------------------------------------------------------------
# Observation source-name resolution
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_observation_recent_events_show_display_name(db_session: AsyncSession, mock_redis):
    """build_observation() shows agent display_name in recent_events, not raw UUID."""
    from app.services.event_service import create_event
    from app.services.observation_service import build_observation
    from app.world.world_seeder import seed_world

    user = await _make_user(db_session, "srcname_user")
    world = await _make_world(db_session, "SrcNameWorld")
    await seed_world(world.id, db_session, user.id)
    await db_session.flush()

    loc = (await db_session.execute(
        select(Location).where(
            Location.world_id == world.id, Location.name == "Town Square"
        )
    )).scalar_one()

    speaker = await _make_agent(db_session, user, world, loc, "Famous Speaker")
    observer = await _make_agent(db_session, user, world, loc, "Observer")

    await create_event(
        world_id=world.id,
        event_type="speech",
        world_tick=1,
        db=db_session,
        source_agent_id=speaker.id,
        location_id=loc.id,
        payload={"content": "I have a dream!"},
    )
    await db_session.flush()

    obs = await build_observation(observer, world_tick=1, db=db_session)
    sources = [ev.source for ev in obs.recent_events]
    assert "Famous Speaker" in sources
    # Make sure the raw UUID is NOT surfaced as source
    assert str(speaker.id) not in sources
