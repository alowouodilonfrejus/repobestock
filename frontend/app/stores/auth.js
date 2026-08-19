import { defineStore } from 'pinia'
import api from '~/utils/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    refreshToken: null,
    user: null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  actions: {
    setTokens(accessToken, refreshToken) {
      this.token = accessToken
      this.refreshToken = refreshToken
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('bestock_token', accessToken)
        localStorage.setItem('bestock_refresh', refreshToken)
      }
    },
    setUser(user) {
      this.user = user
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('bestock_user', JSON.stringify(user))
      }
    },
    async login(email, password) {
      const { data } = await api.post('/auth/login/json', { email, password })
      this.setTokens(data.access_token, data.refresh_token)
      await this.fetchMe()
      return data
    },
    async register(payload) {
      const { data } = await api.post('/auth/register', payload)
      return data
    },
    async refresh() {
      const refreshToken = this.refreshToken
      if (!refreshToken) throw new Error('No refresh token')
      const { data } = await api.post('/auth/refresh', { refresh_token: refreshToken })
      this.setTokens(data.access_token, data.refresh_token)
      return data
    },
    async fetchMe() {
      const { data } = await api.get('/auth/me')
      this.setUser(data)
      return data
    },
    hydrate() {
      if (typeof localStorage === 'undefined') return
      const token = localStorage.getItem('bestock_token')
      const refresh = localStorage.getItem('bestock_refresh')
      const user = localStorage.getItem('bestock_user')
      if (token) this.token = token
      if (refresh) this.refreshToken = refresh
      if (user) {
        try {
          this.user = JSON.parse(user)
        } catch {
          this.user = null
        }
      }
    },
    async logout() {
      if (this.refreshToken) {
        try {
          await api.post('/auth/logout', { refresh_token: this.refreshToken })
        } catch {
          // le refresh token sera révoqué par expiration ; on continue
        }
      }
      this.token = null
      this.refreshToken = null
      this.user = null
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem('bestock_token')
        localStorage.removeItem('bestock_refresh')
        localStorage.removeItem('bestock_user')
      }
    }
  }
})