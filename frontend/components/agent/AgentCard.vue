<template>
  <div class="genesis-card hover:border-genesis-accent/50 transition-colors cursor-pointer" @click="$emit('click', agent)">
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-genesis-accent2/20 flex items-center justify-center text-lg font-bold text-genesis-accent2">
          {{ agent.display_name[0].toUpperCase() }}
        </div>
        <div>
          <p class="font-semibold text-genesis-text">{{ agent.display_name }}</p>
          <p class="text-xs text-genesis-muted">{{ agent.role || agent.agent_type }}</p>
        </div>
      </div>
      <span :class="statusClass">{{ agent.status }}</span>
    </div>

    <p v-if="agent.bio" class="text-xs text-genesis-muted mb-3 line-clamp-2">{{ agent.bio }}</p>

    <div class="grid grid-cols-3 gap-2 text-center text-xs">
      <div class="bg-genesis-bg rounded p-1.5">
        <p class="text-genesis-accent font-bold">{{ agent.reputation }}</p>
        <p class="text-genesis-muted">Rep</p>
      </div>
      <div class="bg-genesis-bg rounded p-1.5">
        <p class="text-genesis-accent2 font-bold">{{ agent.influence }}</p>
        <p class="text-genesis-muted">Influence</p>
      </div>
      <div class="bg-genesis-bg rounded p-1.5">
        <p class="text-white font-bold">L{{ agent.permission_level }}</p>
        <p class="text-genesis-muted">Perm</p>
      </div>
    </div>

    <div class="mt-3 flex gap-2">
      <NuxtLink :to="`/agents/${agent.id}`" @click.stop class="flex-1 text-center genesis-btn-secondary text-xs py-1">
        View Profile
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Agent } from '~/types/api'

const props = defineProps<{ agent: Agent }>()
defineEmits<{ click: [agent: Agent] }>()

const statusClass = computed(() => {
  const map: Record<string, string> = {
    online: 'status-online',
    offline: 'status-offline',
    proxy: 'status-proxy',
    idle: 'status-online',
    busy: 'status-busy',
  }
  return map[props.agent.status] || 'status-offline'
})
</script>
