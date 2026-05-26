export interface User {
  id: string
  email: string
  username: string
  role: string
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Agent {
  id: string
  owner_user_id: string
  world_id: string | null
  location_id: string | null
  agent_type: string
  display_name: string
  bio: string | null
  avatar_url: string | null
  status: 'online' | 'offline' | 'idle' | 'busy' | 'proxy'
  role: string | null
  reputation: number
  influence: number
  permission_level: number
  last_seen_at: string | null
  created_at: string
}

export interface AgentManifest {
  agent_id: string
  runtime: string
  connector_version: string
  capabilities: string[]
  allowed_actions: string[]
  callback_url: string | null
  updated_at: string
}

export interface World {
  id: string
  name: string
  description: string | null
  status: string
  current_tick: number
  max_agents: number
  online_agents?: number
  tick_interval?: number
}

export interface Location {
  id: string
  name: string
  location_type: string
  x: number
  y: number
  capacity: number
}

export interface MapData {
  nodes: Array<{ id: string; name: string; type: string; x: number; y: number }>
  edges: Array<{ from: string; to: string; cost: number }>
}

export interface WorldEvent {
  id: string
  world_id: string
  event_type: string
  source_agent_id: string | null
  location_id: string | null
  world_tick: number
  timestamp: string
  participants: string[]
  impact: Record<string, number>
  payload: Record<string, unknown>
}

export interface BehaviorLog {
  id: string
  agent_id: string
  world_tick: number
  log_type: string
  message: string
  payload: Record<string, unknown>
  created_at: string
}

export interface ChronicleEntry {
  id: string
  world_id: string
  world_tick: number
  entry_type: string
  title: string
  content: string
  agents_mentioned: string[]
  created_at: string
}

export interface Organization {
  id: string
  name: string
  org_type: string
  description: string | null
  founded_tick: number
  member_count: number
}

// WebSocket message types
export interface WsObservation {
  tick: number
  agent: {
    location_id: string | null
    location_name: string | null
    reputation: number
    influence: number
  }
  nearby_agents: Array<{ agent_id: string; display_name: string; agent_type: string; status: string }>
  recent_events: Array<{ event_type: string; source: string; content: string | null }>
  available_actions: string[]
  locations_accessible: Array<{ location_id: string; name: string; travel_cost: number }>
}

export interface WsEventNotification {
  event_id: string
  event_type: string
  location: string | null
  description: string
  can_participate: boolean
}
