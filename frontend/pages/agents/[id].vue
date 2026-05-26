<template>
  <div v-if="agent" class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="genesis-card mb-6">
      <div class="flex items-start justify-between">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-full bg-genesis-accent2/20 flex items-center justify-center text-2xl font-bold text-genesis-accent2">
            {{ agent.display_name[0].toUpperCase() }}
          </div>
          <div>
            <h1 class="text-xl font-bold">{{ agent.display_name }}</h1>
            <p class="text-genesis-muted text-sm">{{ agent.role || agent.agent_type }}</p>
            <span :class="statusClass(agent.status)" class="mt-1 inline-block">{{ agent.status }}</span>
          </div>
        </div>
        <div class="text-right text-sm text-genesis-muted">
          <p>Permission: Level {{ agent.permission_level }}</p>
          <p v-if="agent.last_seen_at">Last seen: {{ formatDate(agent.last_seen_at) }}</p>
        </div>
      </div>
      <p v-if="agent.bio" class="mt-4 text-genesis-muted text-sm">{{ agent.bio }}</p>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-3 mt-4">
        <div class="text-center bg-genesis-bg rounded p-2">
          <p class="text-xl font-bold text-genesis-accent">{{ agent.reputation }}</p>
          <p class="text-xs text-genesis-muted">Reputation</p>
        </div>
        <div class="text-center bg-genesis-bg rounded p-2">
          <p class="text-xl font-bold text-genesis-accent2">{{ agent.influence }}</p>
          <p class="text-xs text-genesis-muted">Influence</p>
        </div>
        <div class="text-center bg-genesis-bg rounded p-2">
          <p class="text-xl font-bold text-white">L{{ agent.permission_level }}</p>
          <p class="text-xs text-genesis-muted">Permission</p>
        </div>
        <div class="text-center bg-genesis-bg rounded p-2">
          <p class="text-xl font-bold text-green-400">{{ agent.world_id ? '✓' : '—' }}</p>
          <p class="text-xs text-genesis-muted">In World</p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 mb-4 border-b border-genesis-border">
      <button
        v-for="tab in tabs"
        :key="tab"
        @click="activeTab = tab"
        class="px-4 py-2 text-sm font-medium transition-colors"
        :class="activeTab === tab ? 'text-genesis-accent border-b-2 border-genesis-accent' : 'text-genesis-muted hover:text-genesis-text'"
      >{{ tab }}</button>
    </div>

    <!-- Profile tab -->
    <div v-if="activeTab === 'Profile'" class="genesis-card">
      <h3 class="font-semibold mb-3">Current Location</h3>
      <p class="text-genesis-muted text-sm">{{ agent.location_id ? `Location ID: ${agent.location_id.slice(0, 8)}...` : 'Not in world' }}</p>
    </div>

    <!-- Behavior Log tab -->
    <div v-if="activeTab === 'Behavior Log'" class="genesis-card" style="height: 500px; overflow-y: auto;">
      <div v-if="logs.length === 0" class="text-center text-genesis-muted py-8">No behavior logs yet.</div>
      <div v-for="log in logs" :key="log.id" class="border-b border-genesis-border/50 py-2">
        <div class="flex items-center gap-2 text-xs">
          <span class="text-genesis-muted font-mono">Tick {{ log.world_tick }}</span>
          <span :class="logTypeColor(log.log_type)" class="uppercase text-[10px]">{{ log.log_type }}</span>
        </div>
        <p class="text-sm mt-0.5">{{ log.message }}</p>
      </div>
    </div>
  </div>

  <div v-else class="text-center py-12 text-genesis-muted">Loading agent...</div>
</template>

<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import type { Agent, BehaviorLog } from '~/types/api'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const api = useApi()
const agent = ref<Agent | null>(null)
const logs = ref<BehaviorLog[]>([])
const activeTab = ref('Profile')
const tabs = ['Profile', 'Behavior Log']

onMounted(async () => {
  const id = route.params.id as string
  try {
    const resp = await api.get(`/agents/${id}`)
    agent.value = resp.data
    const logsResp = await api.get(`/agents/${id}/logs`)
    logs.value = logsResp.data
  } catch (e) {
    console.error(e)
  }
})

function statusClass(status: string) {
  const map: Record<string, string> = {
    online: 'status-online', offline: 'status-offline', proxy: 'status-proxy', busy: 'status-busy',
  }
  return map[status] || 'status-offline'
}

function logTypeColor(type: string) {
  const map: Record<string, string> = {
    observation: 'text-blue-400', intent: 'text-amber-400',
    action: 'text-green-400', result: 'text-purple-400', error: 'text-red-400',
  }
  return map[type] || 'text-genesis-muted'
}

function formatDate(d: string) {
  return new Date(d).toLocaleString()
}
</script>
