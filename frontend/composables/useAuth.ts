import { useAuthStore } from '~/stores/auth'
import { useApi } from '~/composables/useApi'

export function useAuth() {
  const authStore = useAuthStore()
  const api = useApi()

  async function login(email: string, password: string) {
    const resp = await api.post('/auth/login', { email, password })
    authStore.setTokens(resp.data)
    return resp.data
  }

  async function register(email: string, username: string, password: string) {
    const resp = await api.post('/auth/register', { email, username, password })
    authStore.setTokens(resp.data)
    return resp.data
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch {
      // ignore errors on logout
    }
    authStore.logout()
    await navigateTo('/login')
  }

  return { login, register, logout }
}
