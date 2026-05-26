import uuid
from datetime import datetime
from pydantic import BaseModel, HttpUrl


class ManifestData(BaseModel):
    runtime: str = "python"
    connector_version: str = "0.1"
    capabilities: list[str] = []
    allowed_actions: list[str] = []
    callback_url: str | None = None


class AgentCreate(BaseModel):
    display_name: str
    bio: str | None = None
    avatar_url: str | None = None
    role: str | None = None
    permission_level: int = 1


class AgentUpdate(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    role: str | None = None


class AgentResponse(BaseModel):
    id: uuid.UUID
    owner_user_id: uuid.UUID
    world_id: uuid.UUID | None
    location_id: uuid.UUID | None
    agent_type: str
    display_name: str
    bio: str | None
    avatar_url: str | None
    status: str
    role: str | None
    reputation: int
    influence: int
    permission_level: int
    last_seen_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ManifestResponse(BaseModel):
    agent_id: uuid.UUID
    runtime: str
    connector_version: str
    capabilities: list[str]
    allowed_actions: list[str]
    callback_url: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyResponse(BaseModel):
    agent_id: uuid.UUID
    api_key: str
