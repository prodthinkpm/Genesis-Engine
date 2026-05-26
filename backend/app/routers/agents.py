import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, pagination_params
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, ApiKeyResponse, ManifestData, ManifestResponse
from app.services import agent_service
from app.schemas.pagination import Page

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentResponse])
async def list_my_agents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pagination: dict = Depends(pagination_params),
):
    return await agent_service.list_agents_for_user(
        current_user.id, db, pagination["limit"], pagination["offset"]
    )


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(
    data: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await agent_service.create_agent(data, current_user.id, db)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await agent_service.get_agent(agent_id, db)


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: uuid.UUID,
    data: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await agent_service.update_agent(agent_id, data, current_user.id, db)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await agent_service.delete_agent(agent_id, current_user.id, db)


@router.post("/{agent_id}/join-world/{world_id}", response_model=AgentResponse)
async def join_world(
    agent_id: uuid.UUID,
    world_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await agent_service.join_world(agent_id, world_id, current_user.id, db)


@router.post("/{agent_id}/leave-world", response_model=AgentResponse)
async def leave_world(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await agent_service.leave_world(agent_id, current_user.id, db)


@router.get("/{agent_id}/manifest", response_model=ManifestResponse)
async def get_manifest(agent_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.agent_manifest import AgentManifest
    from app.core.exceptions import NotFoundError
    result = await db.execute(select(AgentManifest).where(AgentManifest.agent_id == agent_id))
    manifest = result.scalar_one_or_none()
    if not manifest:
        raise NotFoundError("No manifest for this agent")
    return manifest


@router.put("/{agent_id}/manifest", response_model=ManifestResponse)
async def upsert_manifest(
    agent_id: uuid.UUID,
    data: ManifestData,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await agent_service.upsert_manifest(agent_id, data, current_user.id, db)


@router.post("/{agent_id}/api-key", response_model=ApiKeyResponse)
async def regenerate_api_key(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw_key = await agent_service.regenerate_api_key(agent_id, current_user.id, db)
    return ApiKeyResponse(agent_id=agent_id, api_key=raw_key)
