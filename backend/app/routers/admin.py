import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.models.agent import Agent
from app.models.world import World
from app.models.event import Event
from app.schemas.agent import AgentCreate
from app.world.world_seeder import seed_world

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def system_stats(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    from app.services.gateway_service import get_online_agent_ids
    from app.redis_client import get_redis

    total_users = (await db.execute(select(func.count()).select_from(User))).scalar()
    total_agents = (await db.execute(select(func.count()).select_from(Agent))).scalar()
    total_events = (await db.execute(select(func.count()).select_from(Event))).scalar()
    online_count = len(get_online_agent_ids())

    redis = await get_redis()
    redis_ping = await redis.ping()

    return {
        "total_users": total_users,
        "total_agents": total_agents,
        "total_events": total_events,
        "ws_connections": online_count,
        "redis_ok": redis_ping,
    }


@router.get("/agents")
async def list_all_agents(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
    limit: int = 50,
    offset: int = 0,
):
    result = await db.execute(select(Agent).limit(limit).offset(offset))
    agents = result.scalars().all()
    return [
        {"id": str(a.id), "display_name": a.display_name, "agent_type": a.agent_type,
         "status": a.status, "permission_level": a.permission_level, "owner_user_id": str(a.owner_user_id)}
        for a in agents
    ]


@router.post("/worlds", status_code=201)
async def create_world(
    name: str,
    description: str = "",
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    world = World(name=name, description=description)
    db.add(world)
    await db.flush()
    await db.refresh(world)
    return {"id": str(world.id), "name": world.name}


@router.post("/worlds/{world_id}/seed", status_code=200)
async def seed_world_endpoint(
    world_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    await seed_world(world_id, db, admin.id)
    return {"status": "seeded", "world_id": str(world_id)}


@router.patch("/agents/{agent_id}/permission")
async def set_agent_permission(
    agent_id: uuid.UUID,
    level: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    from app.core.exceptions import NotFoundError
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundError("Agent not found")
    agent.permission_level = max(1, min(4, level))
    await db.flush()
    return {"agent_id": str(agent_id), "permission_level": agent.permission_level}


@router.post("/agents/{agent_id}/ban")
async def ban_agent(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    from app.core.exceptions import NotFoundError
    from app.core.constants import AgentStatus
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundError("Agent not found")
    agent.status = "banned"
    await db.flush()
    return {"agent_id": str(agent_id), "status": "banned"}
