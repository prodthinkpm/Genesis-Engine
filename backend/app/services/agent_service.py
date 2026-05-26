import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.agent import Agent
from app.models.agent_manifest import AgentManifest
from app.models.world import World
from app.schemas.agent import AgentCreate, AgentUpdate, ManifestData
from app.core.security import hash_password, generate_api_key
from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError, BadRequestError
from app.core.constants import AgentStatus


async def create_agent(data: AgentCreate, owner_id: uuid.UUID, db: AsyncSession) -> Agent:
    agent = Agent(
        owner_user_id=owner_id,
        display_name=data.display_name,
        bio=data.bio,
        avatar_url=data.avatar_url,
        role=data.role,
        permission_level=data.permission_level,
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)
    return agent


async def get_agent(agent_id: uuid.UUID, db: AsyncSession) -> Agent:
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundError(f"Agent {agent_id} not found")
    return agent


async def list_agents_for_user(owner_id: uuid.UUID, db: AsyncSession, limit: int = 20, offset: int = 0) -> list[Agent]:
    result = await db.execute(
        select(Agent).where(Agent.owner_user_id == owner_id).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def update_agent(agent_id: uuid.UUID, data: AgentUpdate, requester_id: uuid.UUID, db: AsyncSession) -> Agent:
    agent = await get_agent(agent_id, db)
    if agent.owner_user_id != requester_id:
        raise ForbiddenError("Not the owner of this agent")

    if data.display_name is not None:
        agent.display_name = data.display_name
    if data.bio is not None:
        agent.bio = data.bio
    if data.avatar_url is not None:
        agent.avatar_url = data.avatar_url
    if data.role is not None:
        agent.role = data.role

    await db.flush()
    await db.refresh(agent)
    return agent


async def delete_agent(agent_id: uuid.UUID, requester_id: uuid.UUID, db: AsyncSession):
    agent = await get_agent(agent_id, db)
    if agent.owner_user_id != requester_id:
        raise ForbiddenError("Not the owner of this agent")
    await db.delete(agent)


async def join_world(agent_id: uuid.UUID, world_id: uuid.UUID, requester_id: uuid.UUID, db: AsyncSession) -> Agent:
    agent = await get_agent(agent_id, db)
    if agent.owner_user_id != requester_id:
        raise ForbiddenError("Not the owner of this agent")

    result = await db.execute(select(World).where(World.id == world_id, World.status == "active"))
    world = result.scalar_one_or_none()
    if not world:
        raise NotFoundError("World not found or inactive")

    agent.world_id = world_id
    agent.status = AgentStatus.OFFLINE
    await db.flush()
    await db.refresh(agent)
    return agent


async def leave_world(agent_id: uuid.UUID, requester_id: uuid.UUID, db: AsyncSession) -> Agent:
    agent = await get_agent(agent_id, db)
    if agent.owner_user_id != requester_id:
        raise ForbiddenError("Not the owner of this agent")

    agent.world_id = None
    agent.location_id = None
    agent.status = AgentStatus.OFFLINE
    await db.flush()
    await db.refresh(agent)
    return agent


async def upsert_manifest(
    agent_id: uuid.UUID, data: ManifestData, requester_id: uuid.UUID, db: AsyncSession
) -> AgentManifest:
    agent = await get_agent(agent_id, db)
    if agent.owner_user_id != requester_id:
        raise ForbiddenError("Not the owner of this agent")

    result = await db.execute(select(AgentManifest).where(AgentManifest.agent_id == agent_id))
    manifest = result.scalar_one_or_none()

    if manifest:
        manifest.runtime = data.runtime
        manifest.connector_version = data.connector_version
        manifest.capabilities = data.capabilities
        manifest.allowed_actions = data.allowed_actions
        manifest.callback_url = data.callback_url
    else:
        manifest = AgentManifest(
            agent_id=agent_id,
            runtime=data.runtime,
            connector_version=data.connector_version,
            capabilities=data.capabilities,
            allowed_actions=data.allowed_actions,
            callback_url=data.callback_url,
        )
        db.add(manifest)

    await db.flush()
    await db.refresh(manifest)
    return manifest


async def regenerate_api_key(
    agent_id: uuid.UUID, requester_id: uuid.UUID, db: AsyncSession
) -> str:
    agent = await get_agent(agent_id, db)
    if agent.owner_user_id != requester_id:
        raise ForbiddenError("Not the owner of this agent")

    result = await db.execute(select(AgentManifest).where(AgentManifest.agent_id == agent_id))
    manifest = result.scalar_one_or_none()
    if not manifest:
        raise BadRequestError("Agent has no manifest. Create manifest first.")

    raw_key = generate_api_key()
    manifest.api_key_hash = hash_password(raw_key)
    await db.flush()
    return raw_key
