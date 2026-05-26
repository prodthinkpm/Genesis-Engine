"""Redis ZSET-backed action queue."""
import json
import time
import uuid
from app.redis_client import get_redis


async def enqueue_action(world_id: uuid.UUID, agent_id: uuid.UUID, action: dict, priority: float = 0.0):
    redis = await get_redis()
    key = f"world:action_queue:{world_id}"
    score = time.time() + priority
    entry = json.dumps({"agent_id": str(agent_id), "action": action}, default=str)
    await redis.zadd(key, {entry: score})


async def dequeue_actions(world_id: uuid.UUID, max_count: int = 50) -> list[dict]:
    redis = await get_redis()
    key = f"world:action_queue:{world_id}"
    items = await redis.zpopmin(key, max_count)
    results = []
    for item, _score in items:
        try:
            results.append(json.loads(item))
        except Exception:
            pass
    return results


async def queue_size(world_id: uuid.UUID) -> int:
    redis = await get_redis()
    return await redis.zcard(f"world:action_queue:{world_id}")
