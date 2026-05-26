<template>
  <div class="w-full max-w-sm">
    <div class="genesis-card">
      <h2 class="text-xl font-bold mb-6 text-center">Sign In</h2>
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm text-genesis-muted mb-1">Email</label>
          <input v-model="email" type="email" required class="w-full bg-genesis-bg border border-genesis-border rounded-md px-3 py-2 text-sm focus:outline-none focus:border-genesis-accent" />
        </div>
        <div>
          <label class="block text-sm text-genesis-muted mb-1">Password</label>
          <input v-model="password" type="password" required class="w-full bg-genesis-bg border border-genesis-border rounded-md px-3 py-2 text-sm focus:outline-none focus:border-genesis-accent" />
        </div>
        <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>
        <button type="submit" :disabled="loading" class="w-full genesis-btn-primary py-2">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>
      <p class="mt-4 text-center text-sm text-genesis-muted">
        No account?
        <NuxtLink to="/register" class="text-genesis-accent hover:underline">Register</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

definePageMeta({ layout: 'public' })

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const route = useRoute()
const { login } = useAuth()

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await login(email.value, password.value)
    const redirect = (route.query.redirect as string) || '/dashboard'
    await navigateTo(redirect)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
