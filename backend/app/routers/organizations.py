import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.organization import Organization, OrganizationMember
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/worlds", tags=["organizations"])


@router.get("/{world_id}/organizations")
async def list_organizations(world_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Organization)
        .where(Organization.world_id == world_id)
        .options(selectinload(Organization.members))
    )
    orgs = result.scalars().all()
    return [
        {
            "id": str(o.id), "name": o.name, "org_type": o.org_type,
            "description": o.description, "founded_tick": o.founded_tick,
            "member_count": len(o.members),
        }
        for o in orgs
    ]


@router.get("/{world_id}/organizations/{org_id}")
async def get_organization(
    world_id: uuid.UUID, org_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Organization)
        .where(Organization.id == org_id, Organization.world_id == world_id)
        .options(selectinload(Organization.members))
    )
    org = result.scalar_one_or_none()
    if not org:
        raise NotFoundError("Organization not found")
    return {
        "id": str(org.id), "name": org.name, "org_type": org.org_type,
        "description": org.description, "founded_tick": org.founded_tick,
        "members": [
            {"agent_id": str(m.agent_id), "role": m.role, "joined_tick": m.joined_tick}
            for m in org.members
        ],
    }
