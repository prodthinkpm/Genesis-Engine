import { defineStore } from 'pinia'
import type { WorldEvent } from '~/types/api'

const MAX_EVENTS = 100

export const useEventsStore = defineStore('events', {
  state: () => ({
    events: [] as WorldEvent[],
    isStreaming: false,
  }),

  actions: {
    addEvent(event: WorldEvent) {
      this.events.unshift(event)
      if (this.events.length > MAX_EVENTS) {
        this.events = this.events.slice(0, MAX_EVENTS)
      }
    },
    setEvents(events: WorldEvent[]) {
      this.events = events
    },
    setStreaming(v: boolean) {
      this.isStreaming = v
    },
  },
})
