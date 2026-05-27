import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import Base, get_db
from app.redis_client import get_redis

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


def make_mock_redis():
    redis = MagicMock()
    redis.exists = AsyncMock(return_value=0)
    redis.setex = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.ping = AsyncMock(return_value=True)
    redis.hset = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=1)
    redis.incr = AsyncMock(return_value=1)
    redis.lpush = AsyncMock(return_value=1)
    redis.ltrim = AsyncMock(return_value=True)
    redis.lrange = AsyncMock(return_value=[])
    redis.zadd = AsyncMock(return_value=1)
    redis.zpopmin = AsyncMock(return_value=[])
    redis.zcard = AsyncMock(return_value=0)
    redis.publish = AsyncMock(return_value=1)
    return redis


@pytest_asyncio.fixture
async def mock_redis():
    """
    Standalone fixture that injects a fake Redis client via the module-level
    ``_redis`` singleton in ``app.redis_client``.

    Because many service modules do ``from app.redis_client import get_redis``
    (binding the function at import time), patching the function reference
    won't help — but ``get_redis()`` returns the module global ``_redis`` if it
    is already set, so injecting into that global *does* work for every caller.

    The fixture also supplies realistic LPUSH/LTRIM/LRANGE semantics so that
    proxy-queue round-trip tests pass without a live Redis.
    """
    import app.redis_client as rc

    # Simulate a realistic LPUSH/LTRIM/LRANGE so proxy queue tests work.
    _store: dict[str, list] = {}

    redis = make_mock_redis()

    async def _lpush(key, *values):
        _store.setdefault(key, [])
        for v in values:
            _store[key].insert(0, v)
        return len(_store[key])

    async def _ltrim(key, start, end):
        if key in _store:
            _store[key] = _store[key][start : end + 1]
        return True

    async def _lrange(key, start, end):
        data = _store.get(key, [])
        if end == -1:
            return list(data[start:])
        return list(data[start : end + 1])

    async def _delete(*keys):
        for k in keys:
            _store.pop(k, None)
        return len(keys)

    redis.lpush = _lpush
    redis.ltrim = _ltrim
    redis.lrange = _lrange
    redis.delete = _delete

    # Inject mock as the already-initialised Redis singleton.
    # get_redis() skips connection setup when _redis is not None.
    original = rc._redis
    rc._redis = redis
    yield redis
    rc._redis = original


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    mock_redis = make_mock_redis()

    async def override_get_db():
        yield db_session

    async def override_get_redis():
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    # Also patch module-level redis usage
    import app.redis_client as rc
    original_get_redis = rc.get_redis

    async def patched_get_redis():
        return mock_redis

    rc.get_redis = patched_get_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    rc.get_redis = original_get_redis
