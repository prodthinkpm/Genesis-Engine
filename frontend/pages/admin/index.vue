<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Admin</h1>

    <!-- Tabs -->
    <div class="flex gap-1 mb-6 border-b border-genesis-border">
      <button v-for="tab in tabs" :key="tab" @click="activeTab = tab"
        class="px-4 py-2 text-sm font-medium transition-colors"
        :class="activeTab === tab ? 'text-genesis-accent border-b-2 border-genesis-accent' : 'text-genesis-muted hover:text-genesis-text'"
      >{{ tab }}</button>
    </div>

    <!-- System stats -->
    <div v-if="activeTab === 'System'" class="space-y-4">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="genesis-card text-center">
          <p class="text-2xl font-bold text-white">{{ stats.total_users ?? '—' }}</p>
          <p class="text-xs text-genesis-muted mt-1">Users</p>
        </div>
        <div class="genesis-card text-center">
          <p class="text-2xl font-bold text-genesis-accent">{{ stats.total_agents ?? '—' }}</p>
          <p class="text-xs text-genesis-muted mt-1">Agents</p>
        </div>
        <div class="genesis-card text-center">
          <p class="text-2xl font-bold text-genesis-accent2">{{ stats.total_events ?? '—' }}</p>
          <p class="text-xs text-genesis-muted mt-1">Events</p>
        </div>
        <div class="genesis-card text-center">
          <p class="text-2xl font-bold text-green-400">{{ stats.ws_connections ?? '—' }}</p>
          <p class="text-xs text-genesis-muted mt-1">WS Connections</p>
        </div>
      </div>
      <div class="genesis-card">
        <h3 class="font-semibold mb-2">Health</h3>
        <p class="text-sm">Redis: <span :class="stats.redis_ok ? 'text-green-400' : 'text-red-400'">{{ stats.redis_ok ? 'OK' : 'Error' }}</span></p>
      </div>

      <!-- Create world -->
      <div class="genesis-card">
        <h3 class="font-semibold mb-3">Create World</h3>
        <div class="flex gap-3">
          <input v-model="newWorldName" placeholder="World name" class="flex-1 bg-genesis-bg border border-genesis-border rounded px-3 py-2 text-sm" />
          <button @click="createWorld" class="genesis-btn-primary text-sm">Create</button>
        </div>
      </div>
    </div>

    <!-- Agents tab -->
    <div v-if="activeTab === 'Agents'" class="genesis-card overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-genesis-muted border-b border-genesis-border">
            <th class="text-left pb-2">Name</th>
            <th class="text-left pb-2">Type</th>
            <th class="text-left pb-2">Status</th>
            <th class="text-left pb-2">Permission</th>
            <th class="text-left pb-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in adminAgents" :key="a.id" class="border-b border-genesis-border/30">
            <td class="py-2">{{ a.display_name }}</td>
            <td class="py-2 text-genesis-muted">{{ a.agent_type }}</td>
            <td class="py-2">
              <span :class="a.status === 'online' ? 'text-green-400' : 'text-genesis-muted'">{{ a.status }}</span>
            </td>
            <td class="py-2">L{{ a.permission_level }}</td>
            <td class="py-2">
              <button @click="banAgent(a.id)" class="text-xs text-red-400 hover:underline">Ban</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useApi } from '~/composables/useApi'

definePageMeta({ middleware: ['auth', 'admin'] })

const api = useApi()
const activeTab = ref('System')
const tabs = ['System', 'Agents']
const stats = ref<Record<string, any>>({})
const adminAgents = ref<any[]>([])
const newWorldName = ref('')

onMounted(async () => {
  await loadStats()
  await loadAgents()
})

async function loadStats() {
  try {
    const resp = await api.get('/admin/stats')
    stats.value = resp.data
  } catch {}
}

async function loadAgents() {
  try {
    const resp = await api.get('/admin/agents')
    adminAgents.value = resp.data
  } catch {}
}

async function banAgent(id: string) {
  if (!confirm('Ban this agent?')) return
  try {
    await api.post(`/admin/agents/${id}/ban`)
    await loadAgents()
  } catch {}
}

async function createWorld() {
  if (!newWorldName.value) return
  try {
    const resp = await api.post(`/admin/worlds?name=${encodeURIComponent(newWorldName.value)}`)
    alert(`World created: ${resp.data.id}`)
    newWorldName.value = ''
  } catch {}
}
</script>
