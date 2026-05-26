"""Genesis Agent Protocol v0.1 - WebSocket message schemas."""
import uuid
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field
import secrets


def _new_msg_id() -> str:
    return secrets.token_hex(8)


class WsEnvelope(BaseModel):
    type: str
    msg_id: str = Field(default_factory=_new_msg_id)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: uuid.UUID | None = None
    payload: dict[str, Any] = {}


# ── Client → Server ──────────────────────────────────────────────────────────

class RegisterPayload(BaseModel):
    api_key: str
    manifest: dict[str, Any]


class HeartbeatPayload(BaseModel):
    status: str = "active"


class ActionData(BaseModel):
    name: str
    target: str | None = None
    content: str | None = None
    extra: dict[str, Any] = {}


class IntentPayload(BaseModel):
    intent: str
    action: ActionData
    confidence: float = 1.0


class MemorySummaryPayload(BaseModel):
    summary: str
    key_facts: list[str] = []


class PermissionRequestPayload(BaseModel):
    requested_level: int
    reason: str


# ── Server → Client ──────────────────────────────────────────────────────────

class NearbyAgentInfo(BaseModel):
    agent_id: uuid.UUID
    display_name: str
    agent_type: str
    status: str


class RecentEventInfo(BaseModel):
    event_type: str
    source: str
    content: str | None = None


class AccessibleLocation(BaseModel):
    location_id: uuid.UUID
    name: str
    travel_cost: int


class AgentWorldState(BaseModel):
    location_id: uuid.UUID | None
    location_name: str | None
    reputation: int
    influence: int


class ObservationPayload(BaseModel):
    tick: int
    agent: AgentWorldState
    nearby_agents: list[NearbyAgentInfo] = []
    recent_events: list[RecentEventInfo] = []
    available_actions: list[str] = []
    locations_accessible: list[AccessibleLocation] = []


class ActionResultPayload(BaseModel):
    action_name: str
    success: bool
    result_description: str
    side_effects: dict[str, Any] = {}


class EventNotificationPayload(BaseModel):
    event_id: uuid.UUID
    event_type: str
    location: str | None
    description: str
    can_participate: bool = False


class WarnCode(str):
    RATE_LIMIT = "RATE_LIMIT_EXCEEDED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INVALID_ACTION = "INVALID_ACTION"
    SCHEMA_ERROR = "SCHEMA_ERROR"


class WarningPayload(BaseModel):
    code: str
    message: str
    retry_after_seconds: int | None = None
    action_name: str | None = None


class WelcomePayload(BaseModel):
    world_id: uuid.UUID | None
    current_tick: int
    agent_status: str
