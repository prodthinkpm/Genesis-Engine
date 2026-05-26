import { defineStore } from 'pinia'
import type { World, Location, MapData } from '~/types/api'

export const useWorldStore = defineStore('world', {
  state: () => ({
    world: null as World | null,
    locations: [] as Location[],
    mapData: null as MapData | null,
    agentPositions: {} as Record<string, { locationId: string; x: number; y: number; name: string }>,
    worldAgents: [] as Array<{ id: string; display_name: string; status: string; agent_type: string; location_id: string | null }>,
  }),

  actions: {
    setWorld(world: World) { this.world = world },
    setLocations(locations: Location[]) { this.locations = locations },
    setMapData(data: MapData) { this.mapData = data },
    updateAgentPosition(agentId: string, locationId: string, x: number, y: number, name: string) {
      this.agentPositions[agentId] = { locationId, x, y, name }
    },
    setWorldAgents(agents: typeof this.worldAgents) { this.worldAgents = agents },
  },
})
