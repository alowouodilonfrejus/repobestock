import { defineStore } from 'pinia'
import api from '~/utils/api'

export const useMaintenancesStore = defineStore('maintenances', {
  state: () => ({
    maintenances: [],
    total: 0,
    loading: false,
    _loaded: false,
  }),
  actions: {
    async fetchMaintenances(force = false) {
      if (!force && this._loaded) return
      this.loading = true
      try {
        const { data } = await api.get('/maintenances', { params: { limit: 200 } })
        this.maintenances = data.items
        this.total = data.total
        this._loaded = true
      } finally {
        this.loading = false
      }
    },
    async demarrer(equipementId, payload) {
      const { data } = await api.post(`/maintenances/equipement/${equipementId}`, payload)
      this._loaded = false
      return data
    },
    async cloturer(maintenanceId, payload) {
      const { data } = await api.post(`/maintenances/${maintenanceId}/cloture`, payload)
      this._loaded = false
      return data
    },
  },
})
