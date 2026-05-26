import { useEventsStore } from '~/stores/events'
import { useApi } from '~/composables/useApi'

export function useEventStream(worldId: string) {
  const eventsStore = useEventsStore()
  const api = useApi()
  let pollTimer: ReturnType<typeof setInterval> | null = null

  async function start() {
    eventsStore.setStreaming(true)
    await _fetchLatest()
    pollTimer = setInterval(_fetchLatest, 5000)
  }

  function stop() {
    eventsStore.setStreaming(false)
    if (pollTimer) clearInterval(pollTimer)
  }

  async function _fetchLatest() {
    try {
      const resp = await api.get('/events', { params: { world_id: worldId, limit: 30 } })
      eventsStore.setEvents(resp.data)
    } catch (e) {
      console.warn('Event stream fetch failed:', e)
    }
  }

  return { start, stop }
}
