<template>
  <div class="h-[calc(100vh-5rem)] flex flex-col">
    <!-- World stats bar -->
    <div class="flex items-center gap-6 mb-4 text-sm">
      <span class="text-genesis-muted">World: <strong class="text-white">{{ world?.name || 'Loading...' }}</strong></span>
      <span class="text-genesis-muted">Tick: <strong class="text-genesis-accent">{{ world?.current_tick ?? '—' }}</strong></span>
      <span class="text-genesis-muted">Agents: <strong class="text-green-400">{{ world?.online_agents ?? '—' }}</strong></span>
      <span class="flex items-center gap-1 text-xs text-green-400 ml-auto">
        <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
        Live
      </span>
    </div>

    <!-- Main split -->
    <div class="flex-1 grid grid-cols-5 gap-4 min-h-0">
      <!-- Map (3/5) -->
      <div class="col-span-3">
        <WorldMap :map-data="mapData" @location-click="onLocationClick" />
      </div>

      <!-- Events (2/5) -->
      <div class="col-span-2 genesis-card flex flex-col min-h-0">
        <EventStream />
      </div>
    </div>

    <!-- Location detail modal -->
    <div v-if="selectedLocation" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50" @click.self="selectedLocation = null">
      <div class="genesis-card w-80">
        <h3 class="font-semibold mb-2">{{ selectedLocation.name }}</h3>
        <p class="text-xs text-genesis-muted uppercase mb-3">{{ selectedLocation.type }}</p>
        <p class="text-sm text-genesis-muted">
          {{ agentsAtLocation(selectedLocation.id).length }} agents present
        </p>
        <div class="mt-3 space-y-1">
          <div v-for="a in agentsAtLocation(selectedLocation.id)" :key="a.id" class="flex items-center gap-2 text-sm">
            <span :class="a.status === 'online' ? 'text-green-400' : 'text-amber-400'">●</span>
            {{ a.display_name }}
          </div>
        </div>
        <button @click="selectedLocation = null" class="mt-4 genesis-btn-secondary w-full text-sm">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import { useWorldStore } from '~/stores/world'
import { useEventStream } from '~/composables/useEventStream'
import type { World, MapData } from '~/types/api'

definePageMeta({ middleware: 'auth' })

const api = useApi()
const worldStore = useWorldStore()
const world = ref<World | null>(null)
const mapData = ref<MapData | null>(null)
const selectedLocation = ref<{ id: string; name: string; type: string } | null>(null)
let streamController: { stop: () => void } | null = null

onMounted(async () => {
  try {
    const worldsResp = await api.get('/worlds')
    if (worldsResp.data.length === 0) return
    const w = worldsResp.data[0]
    world.value = w
    worldStore.setWorld(w)

    const mapResp = await api.get(`/worlds/${w.id}/map`)
    mapData.value = mapResp.data
    worldStore.setMapData(mapResp.data)

    const { start } = useEventStream(w.id)
    await start()

    // Load agents
    const agentsResp = await api.get(`/worlds/${w.id}/agents`)
    worldStore.setWorldAgents(agentsResp.data)

    // Poll world + agents
    setInterval(async () => {
      try {
        const wResp = await api.get(`/worlds/${w.id}`)
        world.value = wResp.data

        const aResp = await api.get(`/worlds/${w.id}/agents`)
        worldStore.setWorldAgents(aResp.data)
      } catch {}
    }, 10000)
  } catch (e) {
    console.error('Failed to load world:', e)
  }
})

function onLocationClick(loc: { id: string; name: string; type: string }) {
  selectedLocation.value = loc
}

function agentsAtLocation(locationId: string) {
  return worldStore.worldAgents.filter(a => a.location_id === locationId && a.status !== 'offline')
}
</script>
