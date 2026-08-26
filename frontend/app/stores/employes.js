import { defineStore } from 'pinia'
import api from '~/utils/api'

export const useEmployesStore = defineStore('employes', {
  state: () => ({
    employes: [],
    loading: false,
    _loaded: false,
  }),
  actions: {
    async fetchEmployes(force = false) {
      if (!force && this._loaded) return
      this.loading = true
      try {
        const { data } = await api.get('/employes', { params: { limit: 500 } })
        this.employes = data
        this._loaded = true
      } finally {
        this.loading = false
      }
    },
    async fetchEmploye(id) {
      const { data } = await api.get(`/employes/${id}`)
      return data
    },
    async fetchMateriels(id) {
      const { data } = await api.get(`/employes/${id}/materiels`)
      return data
    },
    async fetchMesMateriels() {
      const { data } = await api.get('/employes/moi')
      return data
    },
    async createEmploye(payload) {
      const { data } = await api.post('/employes', payload)
      this.employes.unshift(data)
      return data
    },
    async createEmployeAvecCompte(payload) {
      const { data } = await api.post('/employes/avec-compte', payload)
      this.employes.unshift(data)
      return data
    },
    async updateEmploye(id, payload) {
      const { data } = await api.put(`/employes/${id}`, payload)
      const idx = this.employes.findIndex((e) => e.id === Number(id))
      if (idx !== -1) this.employes[idx] = data
      return data
    },
  },
})
