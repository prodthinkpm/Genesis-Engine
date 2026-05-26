<template>
  <div class="relative w-full h-full bg-genesis-bg rounded-lg overflow-hidden border border-genesis-border select-none">
    <!-- Background grid -->
    <svg class="absolute inset-0 w-full h-full opacity-10" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#374151" stroke-width="0.5"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />
    </svg>

    <!-- Edges -->
    <svg v-if="mapData" class="absolute inset-0 w-full h-full pointer-events-none">
      <line
        v-for="(edge, i) in mapData.edges"
        :key="`edge-${i}`"
        :x1="nodePos(edge.from).x * containerW"
        :y1="nodePos(edge.from).y * containerH"
        :x2="nodePos(edge.to).x * containerW"
        :y2="nodePos(edge.to).y * containerH"
        stroke="#1f2937"
        stroke-width="1.5"
      />
    </svg>

    <!-- Nodes -->
    <div
      v-for="node in mapData?.nodes"
      :key="node.id"
      class="absolute transform -translate-x-1/2 -translate-y-1/2 group"
      :style="{ left: `${node.x * 100}%`, top: `${node.y * 100}%` }"
      @click="$emit('locationClick', node)"
    >
      <!-- Location circle -->
      <div
        class="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer transition-all border-2"
        :class="locationClass(node.type)"
        :title="node.name"
      >
        <span class="text-sm">{{ locationIcon(node.type) }}</span>
      </div>
      <!-- Label -->
      <div class="absolute top-11 left-1/2 -translate-x-1/2 whitespace-nowrap text-[10px] text-genesis-muted opacity-0 group-hover:opacity-100 transition-opacity bg-genesis-card px-1 py-0.5 rounded">
        {{ node.name }}
      </div>
      <!-- Agent count dot -->
      <div
        v-if="agentCountAt(node.id) > 0"
        class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-genesis-accent text-black text-[9px] font-bold flex items-center justify-center"
      >
        {{ agentCountAt(node.id) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useWorldStore } from '~/stores/world'
import type { MapData } from '~/types/api'

const props = defineProps<{ mapData: MapData | null }>()
defineEmits<{ locationClick: [node: { id: string; name: string; type: string }] }>()

const worldStore = useWorldStore()
const containerW = ref(600)
const containerH = ref(400)

const nodeIndex = computed(() => {
  const idx: Record<string, { x: number; y: number }> = {}
  for (const n of props.mapData?.nodes || []) idx[n.id] = { x: n.x, y: n.y }
  return idx
})

function nodePos(id: string) {
  return nodeIndex.value[id] || { x: 0.5, y: 0.5 }
}

function agentCountAt(locationId: string): number {
  return worldStore.worldAgents.filter(a => a.location_id === locationId && a.status !== 'offline').length
}

function locationClass(type: string) {
  const map: Record<string, string> = {
    plaza: 'border-amber-500 bg-amber-900/30',
    market: 'border-green-500 bg-green-900/30',
    tavern: 'border-orange-500 bg-orange-900/30',
    guild: 'border-blue-500 bg-blue-900/30',
    park: 'border-emerald-500 bg-emerald-900/30',
    library: 'border-purple-500 bg-purple-900/30',
    workshop: 'border-gray-500 bg-gray-900/30',
    council: 'border-indigo-500 bg-indigo-900/30',
    harbor: 'border-cyan-500 bg-cyan-900/30',
  }
  return map[type] || 'border-genesis-border bg-genesis-card'
}

function locationIcon(type: string) {
  const map: Record<string, string> = {
    plaza: '⬡', market: '🏪', tavern: '🍺', guild: '⚔️',
    park: '🌿', library: '📚', workshop: '⚒️', council: '🏛️', harbor: '⚓',
  }
  return map[type] || '●'
}
</script>
