<template>
  <div class="w-full max-w-sm">
    <div class="genesis-card">
      <h2 class="text-xl font-bold mb-6 text-center">Join Genesis Engine</h2>
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm text-genesis-muted mb-1">Email</label>
          <input v-model="email" type="email" required class="w-full bg-genesis-bg border border-genesis-border rounded-md px-3 py-2 text-sm focus:outline-none focus:border-genesis-accent" />
        </div>
        <div>
          <label class="block text-sm text-genesis-muted mb-1">Username</label>
          <input v-model="username" type="text" required pattern="[a-zA-Z0-9_-]{3,64}" class="w-full bg-genesis-bg border border-genesis-border rounded-md px-3 py-2 text-sm focus:outline-none focus:border-genesis-accent" />
        </div>
        <div>
          <label class="block text-sm text-genesis-muted mb-1">Password</label>
          <input v-model="password" type="password" required minlength="8" class="w-full bg-genesis-bg border border-genesis-border rounded-md px-3 py-2 text-sm focus:outline-none focus:border-genesis-accent" />
        </div>
        <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>
        <button type="submit" :disabled="loading" class="w-full genesis-btn-primary py-2">
          {{ loading ? 'Creating account...' : 'Create Account' }}
        </button>
      </form>
      <p class="mt-4 text-center text-sm text-genesis-muted">
        Already have an account?
        <NuxtLink to="/login" class="text-genesis-accent hover:underline">Sign in</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '~/composables/useAuth'

definePageMeta({ layout: 'public' })

const email = ref('')
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const { register } = useAuth()

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    await register(email.value, username.value, password.value)
    await navigateTo('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
