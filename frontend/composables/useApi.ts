import axios from 'axios'
import { useAuthStore } from '~/stores/auth'

export function useApi() {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  const api = axios.create({
    baseURL: `${config.public.apiBase}/api/v1`,
  })

  api.interceptors.request.use((config) => {
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  })

  api.interceptors.response.use(
    (resp) => resp,
    async (error) => {
      if (error.response?.status === 401 && authStore.refreshToken) {
        try {
          const resp = await axios.post(`${config.public.apiBase}/api/v1/auth/refresh`, {
            refresh_token: authStore.refreshToken,
          })
          authStore.setTokens(resp.data)
          error.config.headers.Authorization = `Bearer ${resp.data.access_token}`
          return api.request(error.config)
        } catch {
          authStore.logout()
          navigateTo('/login')
        }
      }
      return Promise.reject(error)
    },
  )

  return api
}
