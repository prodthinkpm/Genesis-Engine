import { useAgentsStore } from '~/stores/agents'
import { useApi } from '~/composables/useApi'
import type { Agent } from '~/types/api'

export function useAgent() {
  const store = useAgentsStore()
  const api = useApi()

  async function fetchMyAgents(): Promise<Agent[]> {
    const resp = await api.get('/agents')
    store.setAgents(resp.data)
    return resp.data
  }

  async function createAgent(data: { display_name: string; bio?: string; permission_level?: number }): Promise<Agent> {
    const resp = await api.post('/agents', data)
    store.updateAgent(resp.data)
    return resp.data
  }

  async function updateAgent(id: string, data: Partial<Agent>): Promise<Agent> {
    const resp = await api.patch(`/agents/${id}`, data)
    store.updateAgent(resp.data)
    return resp.data
  }

  async function deleteAgent(id: string): Promise<void> {
    await api.delete(`/agents/${id}`)
    store.removeAgent(id)
  }

  async function joinWorld(agentId: string, worldId: string): Promise<Agent> {
    const resp = await api.post(`/agents/${agentId}/join-world/${worldId}`)
    store.updateAgent(resp.data)
    return resp.data
  }

  async function setManifest(agentId: string, manifest: object) {
    const resp = await api.put(`/agents/${agentId}/manifest`, manifest)
    return resp.data
  }

  async function generateApiKey(agentId: string): Promise<string> {
    const resp = await api.post(`/agents/${agentId}/api-key`)
    return resp.data.api_key
  }

  return { fetchMyAgents, createAgent, updateAgent, deleteAgent, joinWorld, setManifest, generateApiKey }
}
