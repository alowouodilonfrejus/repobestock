import { defineStore } from 'pinia'
import api from '~/utils/api'

export const useAffectationsStore = defineStore('affectations', {
  state: () => ({
    affectations: [],
    total: 0,
    loading: false,
    _loaded: false,
  }),
  actions: {
    async fetchAffectations(force = false) {
      if (!force && this._loaded) return
      this.loading = true
      try {
        const { data } = await api.get('/affectations', { params: { limit: 200 } })
        this.affectations = data.items
        this.total = data.total
        this._loaded = true
      } finally {
        this.loading = false
      }
    },
    async fetchAffectation(id) {
      const { data } = await api.get(`/affectations/${id}`)
      return data
    },
    // Affectation multi-materiels : une seule requete, transaction cote serveur.
    async createAffectation(payload) {
      const { data } = await api.post('/affectations', payload)
      this._loaded = false
      return data
    },
    async retourMateriel(affectationId, payload) {
      const { data } = await api.post(`/affectations/${affectationId}/retour`, payload)
      this._loaded = false
      return data
    },
  },
})
