import { defineStore } from 'pinia'
import type { User, TokenResponse } from '~/types/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    accessToken: null as string | null,
    refreshToken: null as string | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isAdmin: (state) => state.user?.role === 'admin',
  },

  actions: {
    setTokens(tokens: TokenResponse) {
      this.accessToken = tokens.access_token
      this.refreshToken = tokens.refresh_token
      if (process.client) {
        localStorage.setItem('genesis_access_token', tokens.access_token)
        localStorage.setItem('genesis_refresh_token', tokens.refresh_token)
      }
    },

    loadFromStorage() {
      if (process.client) {
        this.accessToken = localStorage.getItem('genesis_access_token')
        this.refreshToken = localStorage.getItem('genesis_refresh_token')
      }
    },

    logout() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      if (process.client) {
        localStorage.removeItem('genesis_access_token')
        localStorage.removeItem('genesis_refresh_token')
      }
    },
  },
})
