"""Integration tests for world seeding, observation service, and proxy mode."""
import uuid
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.models.world import World
from app.models.location import Location, LocationConnection
from app.models.organization import Organization
from app.models.agent import Agent
from app.core.constants import AgentType, AgentStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _create_world(db: AsyncSession, name: str = "Test World") -> World:
    world = World(name=name, status="active", tick_interval=30, max_agents=200)
    db.add(world)
    await db.flush()
    await db.refresh(world)
    return world


async def _create_user(db: AsyncSession, email: str = "seed@example.com") -> "User":
    from app.models.user import User
    from app.core.security import hash_password

    user = User(
        email=email,
        username=email.split("@")[0],
        password_hash=hash_password("password"),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# World seeder
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_world_seeder_creates_aethermoor(db_session: AsyncSession):
    """seed_world() creates 9 locations, 3 organisations and 50 NPC agents."""
    from app.world.world_seeder import seed_world

    user = await _create_user(db_session, "seeder@example.com")
    world = await _create_world(db_session, "Aethermoor")

    await seed_world(world.id, db_session, user.id)
    await db_session.flush()

    locs = list((await db_session.execute(
        select(Location).where(Location.world_id == world.id)
    )).scalars())
    assert len(locs) == 9, f"Expected 9 locations, got {len(locs)}"

    orgs = list((await db_session.execute(
        select(Organization).where(Organization.world_id == world.id)
    )).scalars())
    assert len(orgs) == 3, f"Expected 3 organisations, got {len(orgs)}"

    npcs = list((await db_session.execute(
        select(Agent).where(
            Agent.world_id == world.id,
            Agent.agent_type == AgentType.NPC,
        )
    )).scalars())
    assert len(npcs) == 50, f"Expected 50 NPC agents, got {len(npcs)}"


@pytest.mark.asyncio
async def test_world_seeder_is_idempotent(db_session: AsyncSession):
    """Calling seed_world() twice does not double-create locations."""
    from app.world.world_seeder import seed_world

    user = await _create_user(db_session, "idempotent@example.com")
    world = await _create_world(db_session, "IdempotentWorld")

    await seed_world(world.id, db_session, user.id)
    await db_session.flush()
    await seed_world(world.id, db_session, user.id)  # second call – should no-op
    await db_session.flush()

    locs = list((await db_session.execute(
        select(Location).where(Location.world_id == world.id)
    )).scalars())
    assert len(locs) == 9


@pytest.mark.asyncio
async def test_locations_have_bidirectional_connections(db_session: AsyncSession):
    """Every connection seeded by world_seeder is bidirectional."""
    from app.world.world_seeder import seed_world, CONNECTIONS

    user = await _create_user(db_session, "bidir@example.com")
    world = await _create_world(db_session, "BiDirWorld")

    await seed_world(world.id, db_session, user.id)
    await db_session.flush()

    all_conns = list((await db_session.execute(
        select(LocationConnection)
        .join(Location, LocationConnection.from_location_id == Location.id)
        .where(Location.world_id == world.id)
    )).scalars())

    # 12 pairs → 24 directed edges
    assert len(all_conns) == len(CONNECTIONS) * 2


# ---------------------------------------------------------------------------
# Observation service
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_observation_service_returns_nearby_agents(db_session: AsyncSession):
    """build_observation() lists agents sharing the same location."""
    from app.services.observation_service import build_observation
    from app.world.world_seeder import seed_world

    user = await _create_user(db_session, "obs@example.com")
    world = await _create_world(db_session, "ObsWorld")
    await seed_world(world.id, db_session, user.id)
    await db_session.flush()

    # Pick the Town Square location
    loc_result = await db_session.execute(
        select(Location).where(
            Location.world_id == world.id,
            Location.name == "Town Square",
        )
    )
    town_square = loc_result.scalar_one()

    # Create two external agents at the same spot
    agent_a = Agent(
        owner_user_id=user.id,
        world_id=world.id,
        location_id=town_square.id,
        display_name="AlphaAgent",
        agent_type=AgentType.EXTERNAL,
        status=AgentStatus.ONLINE,
        permission_level=2,
    )
    agent_b = Agent(
        owner_user_id=user.id,
        world_id=world.id,
        location_id=town_square.id,
        display_name="BetaAgent",
        agent_type=AgentType.EXTERNAL,
        status=AgentStatus.ONLINE,
        permission_level=2,
    )
    db_session.add(agent_a)
    db_session.add(agent_b)
    await db_session.flush()
    await db_session.refresh(agent_a)
    await db_session.refresh(agent_b)

    obs = await build_observation(agent_a, world_tick=1, db=db_session)

    nearby_ids = {str(a.agent_id) for a in obs.nearby_agents}
    assert str(agent_b.id) in nearby_ids
    assert str(agent_a.id) not in nearby_ids  # self not listed


@pytest.mark.asyncio
async def test_observation_includes_accessible_locations(db_session: AsyncSession):
    """build_observation() includes connected locations in locations_accessible."""
    from app.services.observation_service import build_observation
    from app.world.world_seeder import seed_world

    user = await _create_user(db_session, "accsloc@example.com")
    world = await _create_world(db_session, "AccessWorld")
    await seed_world(world.id, db_session, user.id)
    await db_session.flush()

    loc = (await db_session.execute(
        select(Location).where(
            Location.world_id == world.id, Location.name == "Town Square"
        )
    )).scalar_one()

    agent = Agent(
        owner_user_id=user.id,
        world_id=world.id,
        location_id=loc.id,
        display_name="Navigator",
        agent_type=AgentType.EXTERNAL,
        status=AgentStatus.ONLINE,
        permission_level=2,
    )
    db_session.add(agent)
    await db_session.flush()
    await db_session.refresh(agent)

    obs = await build_observation(agent, world_tick=1, db=db_session)
    # Town Square connects to Market, Tavern, Park, Council Hall
    assert len(obs.locations_accessible) >= 4


# ---------------------------------------------------------------------------
# Proxy service
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_proxy_queue_round_trip(db_session: AsyncSession, mock_redis):
    """enter_proxy_mode + queue_proxy_observation + drain_proxy_queue work end-to-end."""
    from app.services.proxy_service import (
        enter_proxy_mode, queue_proxy_observation, drain_proxy_queue,
    )

    user = await _create_user(db_session, "proxy@example.com")
    world = await _create_world(db_session, "ProxyWorld")

    agent = Agent(
        owner_user_id=user.id,
        world_id=world.id,
        display_name="ProxyAgent",
        agent_type=AgentType.EXTERNAL,
        status=AgentStatus.ONLINE,
        permission_level=1,
    )
    db_session.add(agent)
    await db_session.flush()
    await db_session.refresh(agent)

    await enter_proxy_mode(agent.id, db_session)
    await db_session.refresh(agent)
    assert agent.status == AgentStatus.PROXY

    obs1 = {"type": "world.observation", "payload": {"tick": 1}}
    obs2 = {"type": "world.observation", "payload": {"tick": 2}}
    await queue_proxy_observation(agent.id, obs1)
    await queue_proxy_observation(agent.id, obs2)

    drained = await drain_proxy_queue(agent.id)
    assert len(drained) == 2
    # Chronological order: tick 1 first, tick 2 second
    assert drained[0]["payload"]["tick"] == 1
    assert drained[1]["payload"]["tick"] == 2

    # Queue should now be empty
    drained_again = await drain_proxy_queue(agent.id)
    assert drained_again == []


@pytest.mark.asyncio
async def test_proxy_queue_respects_max_size(mock_redis):
    """Proxy queue silently drops oldest observations beyond PROXY_QUEUE_MAX_SIZE."""
    from app.services.proxy_service import queue_proxy_observation, drain_proxy_queue
    from app.core.constants import PROXY_QUEUE_MAX_SIZE

    agent_id = uuid.uuid4()
    # Push more items than the cap
    for i in range(PROXY_QUEUE_MAX_SIZE + 5):
        await queue_proxy_observation(agent_id, {"tick": i})

    drained = await drain_proxy_queue(agent_id)
    assert len(drained) <= PROXY_QUEUE_MAX_SIZE
