import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '~/stores/auth'

type MessageHandler = (payload: Record<string, unknown>) => void

export function useWebSocket() {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  const state = ref<'disconnected' | 'connecting' | 'connected' | 'reconnecting'>('disconnected')
  const ws = ref<WebSocket | null>(null)
  const handlers = new Map<string, MessageHandler[]>()

  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let reconnectDelay = 1000
  let running = false
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null

  function on(type: string, handler: MessageHandler) {
    if (!handlers.has(type)) handlers.set(type, [])
    handlers.get(type)!.push(handler)
  }

  function off(type: string, handler: MessageHandler) {
    const list = handlers.get(type)
    if (list) {
      const idx = list.indexOf(handler)
      if (idx >= 0) list.splice(idx, 1)
    }
  }

  function send(data: object) {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(data))
    }
  }

  function connect(path: string) {
    if (!authStore.accessToken) return
    running = true
    reconnectDelay = 1000
    _connect(path)
  }

  function _connect(path: string) {
    state.value = 'connecting'
    const url = `${config.public.wsBase}${path}?token=${authStore.accessToken}`
    const socket = new WebSocket(url)
    ws.value = socket

    socket.onopen = () => {
      state.value = 'connected'
      reconnectDelay = 1000
      _startHeartbeat()
    }

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        const list = handlers.get(msg.type) || []
        for (const h of list) h(msg.payload || {})
      } catch {
        console.warn('WS: invalid JSON')
      }
    }

    socket.onerror = () => {
      state.value = 'reconnecting'
    }

    socket.onclose = () => {
      _stopHeartbeat()
      if (running) {
        state.value = 'reconnecting'
        reconnectTimer = setTimeout(() => {
          reconnectDelay = Math.min(reconnectDelay * 2, 30000)
          _connect(path)
        }, reconnectDelay)
      } else {
        state.value = 'disconnected'
      }
    }
  }

  function disconnect() {
    running = false
    _stopHeartbeat()
    if (reconnectTimer) clearTimeout(reconnectTimer)
    ws.value?.close()
    ws.value = null
    state.value = 'disconnected'
  }

  function _startHeartbeat() {
    heartbeatTimer = setInterval(() => {
      send({ type: 'agent.heartbeat', payload: { status: 'active' } })
    }, 30000)
  }

  function _stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  onUnmounted(() => disconnect())

  return { state, connect, disconnect, send, on, off }
}
