import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.chronicle_service import get_chronicle

router = APIRouter(prefix="/worlds", tags=["chronicle"])


@router.get("/{world_id}/chronicle")
async def list_chronicle(
    world_id: uuid.UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    entries = await get_chronicle(world_id, db, limit, offset)
    return [
        {
            "id": str(e.id), "world_id": str(e.world_id), "world_tick": e.world_tick,
            "entry_type": e.entry_type, "title": e.title, "content": e.content,
            "agents_mentioned": e.agents_mentioned, "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]
