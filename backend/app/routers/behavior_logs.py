import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.behavior_log import BehaviorLog
from app.models.agent import Agent
from app.core.exceptions import ForbiddenError, NotFoundError

router = APIRouter(prefix="/agents", tags=["behavior_logs"])


@router.get("/{agent_id}/logs")
async def get_agent_logs(
    agent_id: uuid.UUID,
    log_type: str | None = Query(default=None),
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent_result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = agent_result.scalar_one_or_none()
    if not agent:
        raise NotFoundError("Agent not found")
    if agent.owner_user_id != current_user.id and current_user.role != "admin":
        raise ForbiddenError("Access denied")

    query = select(BehaviorLog).where(BehaviorLog.agent_id == agent_id).order_by(
        BehaviorLog.created_at.desc()
    )
    if log_type:
        query = query.where(BehaviorLog.log_type == log_type)
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    logs = result.scalars().all()
    return [
        {
            "id": str(l.id), "agent_id": str(l.agent_id), "world_tick": l.world_tick,
            "log_type": l.log_type, "message": l.message, "payload": l.payload,
            "created_at": l.created_at.isoformat(),
        }
        for l in logs
    ]
