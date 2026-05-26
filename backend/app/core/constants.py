from enum import IntEnum, StrEnum


class PermissionLevel(IntEnum):
    OBSERVE = 1
    CIVILIZATION = 2
    EXTENDED = 3
    REAL_WORLD = 4


class AgentStatus(StrEnum):
    OFFLINE = "offline"
    ONLINE = "online"
    IDLE = "idle"
    BUSY = "busy"
    PROXY = "proxy"


class AgentType(StrEnum):
    EXTERNAL = "external"
    SYSTEM = "system"
    NPC = "npc"


class EventType(StrEnum):
    SPEECH = "speech"
    MOVE = "move"
    TRADE = "trade"
    VOTE = "vote"
    JOIN_EVENT = "join_event"
    JOIN_ORG = "join_org"
    BRAWL = "brawl"
    FESTIVAL_START = "festival_start"


class LogType(StrEnum):
    OBSERVATION = "observation"
    INTENT = "intent"
    ACTION = "action"
    RESULT = "result"
    ERROR = "error"
    MEMORY = "memory"


class OrgType(StrEnum):
    GUILD = "guild"
    COUNCIL = "council"
    FACTION = "faction"
    RESEARCH = "research"
    MERCHANT = "merchant"


# Maps action name → minimum permission level required
ACTION_PERMISSION_MAP: dict[str, PermissionLevel] = {
    # Level 1: observe only
    "observe": PermissionLevel.OBSERVE,
    # Level 2: in-civilization actions
    "speech": PermissionLevel.CIVILIZATION,
    "move": PermissionLevel.CIVILIZATION,
    "trade": PermissionLevel.CIVILIZATION,
    "vote": PermissionLevel.CIVILIZATION,
    "join_event": PermissionLevel.CIVILIZATION,
    "join_org": PermissionLevel.CIVILIZATION,
    # Level 3: extended capabilities
    "web_query": PermissionLevel.EXTENDED,
    "api_call": PermissionLevel.EXTENDED,
    "knowledge_write": PermissionLevel.EXTENDED,
    # Level 4: real world actions (default OFF)
    "send_email": PermissionLevel.REAL_WORLD,
    "file_access": PermissionLevel.REAL_WORLD,
    "calendar_op": PermissionLevel.REAL_WORLD,
    "code_commit": PermissionLevel.REAL_WORLD,
}

# Redis TTLs (seconds)
AGENT_CONNECTION_TTL = 90
PERMISSION_CACHE_TTL = 60
AGENT_LOCATION_CACHE_TTL = 300
PROXY_QUEUE_MAX_SIZE = 100

# World simulation
MAX_ACTIONS_PER_TICK_EXTERNAL = 20
MAX_ACTIONS_PER_TICK_SYSTEM = 30
CHRONICLE_WRITE_INTERVAL_TICKS = 10
