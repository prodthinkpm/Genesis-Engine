<template>
  <div class="flex flex-col h-full">
    <div class="flex items-center justify-between mb-2 flex-shrink-0">
      <h3 class="text-sm font-semibold text-genesis-text">Live Events</h3>
      <span v-if="isStreaming" class="flex items-center gap-1 text-xs text-green-400">
        <span class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
        Live
      </span>
    </div>

    <div ref="scrollEl" class="flex-1 overflow-y-auto space-y-1.5 pr-1 scrollbar-thin">
      <TransitionGroup name="event-list" tag="div" class="space-y-1.5">
        <div
          v-for="event in events"
          :key="event.id"
          class="bg-genesis-bg rounded p-2 text-xs border border-genesis-border/50"
        >
          <div class="flex items-start gap-2">
            <span :class="eventTypeColor(event.event_type)" class="text-[10px] font-mono uppercase shrink-0 mt-0.5">
              {{ event.event_type }}
            </span>
            <p class="text-genesis-muted leading-relaxed">{{ describeEvent(event) }}</p>
          </div>
          <p class="text-genesis-border mt-1 text-[10px]">Tick {{ event.world_tick }}</p>
        </div>
      </TransitionGroup>

      <div v-if="events.length === 0" class="text-center text-genesis-muted py-8 text-sm">
        No events yet...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useEventsStore } from '~/stores/events'
import type { WorldEvent } from '~/types/api'

const eventsStore = useEventsStore()
const events = computed(() => eventsStore.events)
const isStreaming = computed(() => eventsStore.isStreaming)

function eventTypeColor(type: string): string {
  const map: Record<string, string> = {
    speech: 'text-blue-400',
    move: 'text-gray-400',
    trade: 'text-green-400',
    vote: 'text-purple-400',
    brawl: 'text-red-400',
    festival_start: 'text-amber-400',
    join_org: 'text-cyan-400',
  }
  return map[type] || 'text-genesis-muted'
}

function describeEvent(event: WorldEvent): string {
  const content = (event.payload as Record<string, string>)?.content
  if (content) return content
  const agent = event.source_agent_id?.slice(0, 8) || 'Unknown'
  return `${agent}... performed ${event.event_type}`
}
</script>

<style scoped>
.event-list-enter-active {
  transition: all 0.3s ease;
}
.event-list-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
