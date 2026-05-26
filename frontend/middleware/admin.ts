import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware(() => {
  const authStore = useAuthStore()
  authStore.loadFromStorage()
  if (!authStore.isAdmin) {
    return navigateTo('/dashboard')
  }
})
