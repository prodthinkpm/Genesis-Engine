import logging
import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, _GENERATED_SECRETS
from app.database import engine
from app.models import *  # ensure all models registered
from app.redis_client import close_redis
from app.world import tick_engine

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


# ── Secret bootstrap helpers ─────────────────────────────────────────────────

def _persist_generated_secrets() -> None:
    """Write auto-generated secrets back into .env so they survive restarts.

    Strategy:
      • If .env already contains the key=... line → replace the placeholder value.
      • If .env doesn't contain the line → append it.
      • If .env doesn't exist at all → create it with just the generated lines.
    Idempotent: running twice produces the same file.
    """
    env_path = Path(".env")
    content = env_path.read_text(encoding="utf-8") if env_path.exists() else ""

    for key, value in _GENERATED_SECRETS.items():
        pattern = rf"^({re.escape(key)}\s*=).*$"
        replacement = rf"\g<1>{value}"
        if re.search(pattern, content, flags=re.MULTILINE):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        else:
            # Append with a blank line separator if file is non-empty
            if content and not content.endswith("\n"):
                content += "\n"
            content += f"\n# Auto-generated on first boot\n{key}={value}\n"

    env_path.write_text(content, encoding="utf-8")
    logger.info("Auto-generated secrets persisted to %s", env_path.resolve())


def _print_bootstrap_banner() -> None:
    """Log a prominent warning when secrets were auto-generated this run."""
    if not _GENERATED_SECRETS:
        return

    sep = "=" * 64
    lines = [
        sep,
        "  GENESIS ENGINE — FIRST-BOOT SECRET GENERATION",
        "  No secrets were found in .env; secure keys were generated",
        "  automatically and written to .env for future restarts.",
        sep,
    ]
    for key, value in _GENERATED_SECRETS.items():
        lines.append(f"  {key:<20} = {value}")
    lines += [
        sep,
        "  ⚠  These values are now in your .env file.",
        "  ⚠  Do NOT share them. Back up .env (or set the env vars",
        "     explicitly) before deploying to production.",
        sep,
    ]
    for line in lines:
        logger.warning(line)

    _persist_generated_secrets()


# ── Application lifespan ─────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    _print_bootstrap_banner()
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
