"""Genesis Agent Protocol v0.1 — message models for the Connector SDK."""
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class ActionData(BaseModel):
    name: str
    target: str | None = None
    content: str | None = None
    extra: dict[str, Any] = {}


class ActionIntent(BaseModel):
    intent: str
    action: ActionData
    confidence: float = 1.0


class NearbyAgent(BaseModel):
    agent_id: uuid.UUID
    display_name: str
    agent_type: str
    status: str


class RecentEvent(BaseModel):
    event_type: str
    source: str
    content: str | None = None


class AccessibleLocation(BaseModel):
    location_id: uuid.UUID
    name: str
    travel_cost: int


class AgentState(BaseModel):
    location_id: uuid.UUID | None
    location_name: str | None
    reputation: int
    influence: int


class Observation(BaseModel):
    tick: int
    agent: AgentState
    nearby_agents: list[NearbyAgent] = []
    recent_events: list[RecentEvent] = []
    available_actions: list[str] = []
    locations_accessible: list[AccessibleLocation] = []


class ActionResult(BaseModel):
    action_name: str
    success: bool
    result_description: str
    side_effects: dict[str, Any] = {}


class EventNotification(BaseModel):
    event_id: uuid.UUID
    event_type: str
    location: str | None
    description: str
    can_participate: bool = False


class MemorySummary(BaseModel):
    summary: str
    key_facts: list[str] = []


class Warning(BaseModel):
    code: str
    message: str
    retry_after_seconds: int | None = None
    action_name: str | None = None


MESSAGE_TYPES = {
    "world.observation": Observation,
    "action.result": ActionResult,
    "event.notification": EventNotification,
    "system.warning": Warning,
}
