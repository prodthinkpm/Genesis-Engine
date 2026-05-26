import uuid
from app.core.constants import ACTION_PERMISSION_MAP, PERMISSION_CACHE_TTL, PermissionLevel
from app.redis_client import get_redis


async def check_permission(agent_id: uuid.UUID, action_name: str, agent_permission_level: int) -> bool:
    required = ACTION_PERMISSION_MAP.get(action_name)
    if required is None:
        return False
    return agent_permission_level >= required


async def get_available_actions(permission_level: int) -> list[str]:
    return [
        action for action, required_level in ACTION_PERMISSION_MAP.items()
        if permission_level >= required_level
    ]


async def cache_permission(agent_id: uuid.UUID, level: int):
    redis = await get_redis()
    await redis.setex(f"permission:{agent_id}", PERMISSION_CACHE_TTL, str(level))


async def get_cached_permission(agent_id: uuid.UUID) -> int | None:
    redis = await get_redis()
    val = await redis.get(f"permission:{agent_id}")
    return int(val) if val else None
