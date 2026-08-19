import { defineStore } from 'pinia'
import api from '~/utils/api'

export const useHistoriqueStore = defineStore('historique', {
  state: () => ({
    historique: [],
    loading: false,
    _loaded: false,
  }),
  actions: {
    async fetchHistorique(force = false) {
      if (this._loaded && !force) return
      this.loading = true
      try {
        const { data } = await api.get('/historique', { params: { limit: 200 } })
        this.historique = data
        this._loaded = true
      } finally {
        this.loading = false
      }
    },
    async fetchEquipementHistorique(id) {
      const { data } = await api.get(`/equipements/${id}/historique`)
      return data
    },
  },
})