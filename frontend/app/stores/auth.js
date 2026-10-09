import { defineStore } from 'pinia'
import api from '~/utils/api'

// Marqueur non sensible : il dit seulement "une session a existe sur cet
// appareil" pour deciding s'il faut valider les cookies au demarrage.
// Les tokens eux-memes sont en cookies httpOnly, jamais en JS/localStorage.
const SESSION_FLAG = 'bestock_session'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    permissions: [],
    authenticated: false,
    sessionReady: false,
  }),
  getters: {
    isAuthenticated: (state) => state.authenticated,
    can: (state) => (perm) => (state.permissions || []).includes(perm) || (state.permissions || []).includes('*'),
    isSuperAdmin: (state) => state.user?.role === 'superadmin',
  },
  actions: {
    setUser(user) {
      this.user = user
      if (typeof localStorage !== 'undefined') {
        try { localStorage.setItem('bestock_user', JSON.stringify(user)) } catch {}
      }
    },
    async login(email, password) {
      const { data } = await api.post('/auth/login/json', { email, password })
      if (typeof localStorage !== 'undefined') {
        try { localStorage.setItem(SESSION_FLAG, '1') } catch {}
      }
      await this.fetchMe()
      return data
    },
    async registerEmploye(payload) {
      const { data } = await api.post('/employes/inscription', payload)
      return data
    },
    async refresh() {
      const { data } = await api.post('/auth/refresh', {})
      await this.fetchMe()
      return data
    },
    async fetchMe() {
      const { data } = await api.get('/auth/me')
      this.setUser(data)
      this.permissions = data.permissions || []
      this.authenticated = true
      if (typeof localStorage !== 'undefined') {
        try { localStorage.setItem('bestock_permissions', JSON.stringify(this.permissions)) } catch {}
        try { localStorage.setItem(SESSION_FLAG, '1') } catch {}
      }
      return data
    },
    clearLocal() {
      this.user = null
      this.permissions = []
      this.authenticated = false
      if (typeof localStorage !== 'undefined') {
        try {
          localStorage.removeItem(SESSION_FLAG)
          localStorage.removeItem('bestock_user')
          localStorage.removeItem('bestock_permissions')
        } catch {}
      }
    },
    async hydrate() {
      if (typeof localStorage === 'undefined') {
        this.sessionReady = true
        return
      }
      // Cache local pour un affichage immediat (non sensible)...
      const user = localStorage.getItem('bestock_user')
      const perms = localStorage.getItem('bestock_permissions')
      const hadSession = localStorage.getItem(SESSION_FLAG)
      if (user) {
        try {
          this.user = JSON.parse(user)
        } catch {
          this.user = null
        }
      }
      if (perms) {
        try { this.permissions = JSON.parse(perms) } catch { this.permissions = [] }
      }
      if (!hadSession) {
        // Pas de session precedente : on reste anonyme sans appels inutiles
        // (un 401 ici declencherait un refresh inutile puis une redirection)
        this.authenticated = false
        this.sessionReady = true
        return
      }
      try {
        // Validation des cookies ; l'intercepteur api.js tente le refresh
        // automatiquement si l'access cookie est expire
        await this.fetchMe()
      } catch (e) {
        const status = e?.response?.status
        if (status === 401) {
          // Refresh refuse : session terminee
          this.clearLocal()
        } else if (!e?.response) {
          // Erseau/reseau : on garde le cache, revalidation ulterieure
          this.authenticated = true
        }
      } finally {
        this.sessionReady = true
      }
    },
    async logout() {
      try {
        await api.post('/auth/logout', {})
      } catch {
        // les cookies seront purges par expiration ; on continue
      }
      this.clearLocal()
    }
  }
})
