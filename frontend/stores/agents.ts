import { defineStore } from 'pinia'
import type { Agent } from '~/types/api'

export const useAgentsStore = defineStore('agents', {
  state: () => ({
    agents: [] as Agent[],
    loading: false,
  }),

  actions: {
    setAgents(agents: Agent[]) {
      this.agents = agents
    },
    updateAgent(updated: Agent) {
      const idx = this.agents.findIndex(a => a.id === updated.id)
      if (idx >= 0) this.agents[idx] = updated
      else this.agents.push(updated)
    },
    removeAgent(id: string) {
      this.agents = this.agents.filter(a => a.id !== id)
    },
  },
})
