<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">My Agents</h1>
      <NuxtLink to="/agents/new" class="genesis-btn-primary">
        + Connect Agent
      </NuxtLink>
    </div>

    <div v-if="loading" class="text-center py-12 text-genesis-muted">Loading agents...</div>

    <div v-else-if="agents.length === 0" class="text-center py-16">
      <div class="text-5xl mb-4">🤖</div>
      <h3 class="text-lg font-semibold mb-2">No agents yet</h3>
      <p class="text-genesis-muted mb-6">Connect your first AI agent to the civilization.</p>
      <NuxtLink to="/agents/new" class="genesis-btn-primary">Connect My First Agent</NuxtLink>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <AgentCard
        v-for="agent in agents"
        :key="agent.id"
        :agent="agent"
        @click="selectedAgent = agent"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAgent } from '~/composables/useAgent'
import { useAgentsStore } from '~/stores/agents'

definePageMeta({ middleware: 'auth' })

const { fetchMyAgents } = useAgent()
const agentsStore = useAgentsStore()
const agents = computed(() => agentsStore.agents)
const loading = ref(true)
const selectedAgent = ref(null)

onMounted(async () => {
  try {
    await fetchMyAgents()
  } finally {
    loading.value = false
  }
  // Refresh every 30s
  setInterval(() => fetchMyAgents().catch(() => {}), 30000)
})
</script>
