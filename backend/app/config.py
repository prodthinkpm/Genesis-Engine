import secrets
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

# Keys considered "weak" / placeholder — will trigger auto-generation
_WEAK_SECRET_KEYS: frozenset[str] = frozenset({
    "dev-secret-key-change-in-production",
    "change-this-to-a-random-secret-key-in-production",
    "",
})

_WEAK_ADMIN_KEYS: frozenset[str] = frozenset({
    "dev-admin-key",
    "change-this-admin-key",
    "",
})

# Populated at Settings construction time if keys were auto-generated.
# Read by main.py to print the bootstrap banner and persist to .env.
_GENERATED_SECRETS: dict[str, str] = {}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://genesis:genesis_dev@localhost:5432/genesis_engine"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    WORLD_TICK_INTERVAL_SECONDS: int = 30

    LOG_LEVEL: str = "INFO"

    ADMIN_API_KEY: str = "dev-admin-key"

    # ── Auto-generate weak / placeholder keys ────────────────────────────

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def _auto_secret_key(cls, v: str) -> str:
        if v in _WEAK_SECRET_KEYS:
            key = secrets.token_hex(32)        # 256-bit, hex-encoded
            _GENERATED_SECRETS["SECRET_KEY"] = key
            return key
        return v

    @field_validator("ADMIN_API_KEY", mode="before")
    @classmethod
    def _auto_admin_key(cls, v: str) -> str:
        if v in _WEAK_ADMIN_KEYS:
            key = secrets.token_urlsafe(32)    # 256-bit, URL-safe base64
            _GENERATED_SECRETS["ADMIN_API_KEY"] = key
            return key
        return v


settings = Settings()
