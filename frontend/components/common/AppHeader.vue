<template>
  <header class="border-b border-genesis-border bg-genesis-card/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
      <NuxtLink to="/" class="text-genesis-accent font-bold text-lg tracking-wide">
        ⬡ Genesis Engine
      </NuxtLink>
      <nav class="flex items-center gap-6 text-sm">
        <NuxtLink to="/observe" class="text-genesis-muted hover:text-genesis-text transition-colors">
          Observe
        </NuxtLink>
        <NuxtLink v-if="authStore.isAuthenticated" to="/dashboard" class="text-genesis-muted hover:text-genesis-text transition-colors">
          My Agents
        </NuxtLink>
        <NuxtLink v-if="authStore.isAdmin" to="/admin" class="text-genesis-muted hover:text-genesis-text transition-colors">
          Admin
        </NuxtLink>
        <button v-if="authStore.isAuthenticated" @click="handleLogout" class="genesis-btn-secondary text-sm">
          Logout
        </button>
        <NuxtLink v-else to="/login" class="genesis-btn-primary text-sm">
          Sign In
        </NuxtLink>
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useAuth } from '~/composables/useAuth'

const authStore = useAuthStore()
const { logout } = useAuth()

async function handleLogout() {
  await logout()
}
</script>
