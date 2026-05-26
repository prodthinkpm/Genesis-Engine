import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.models import *  # ensure all models registered
from app.redis_client import close_redis
from app.world import tick_engine

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Genesis Engine starting up...")
    await tick_engine.start()
    yield
    logger.info("Genesis Engine shutting down...")
    await tick_engine.stop()
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title="Genesis Engine API",
    description="AI Agent Civilization Network",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from app.routers import auth, agents, worlds, events, behavior_logs, chronicle, admin, gateway, organizations

app.include_router(auth.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(worlds.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(behavior_logs.router, prefix="/api/v1")
app.include_router(chronicle.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(organizations.router, prefix="/api/v1")
app.include_router(gateway.router)  # WebSocket at /ws/gateway


@app.get("/health")
async def health():
    from app.redis_client import get_redis
    redis = await get_redis()
    redis_ok = await redis.ping()
    return {"status": "ok", "redis": redis_ok}
