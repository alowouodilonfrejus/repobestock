import { defineStore } from 'pinia'
import api from '~/utils/api'
import { useCategoriesStore } from '~/stores/categories'

export const useEquipementsStore = defineStore('equipements', {
  state: () => ({
    equipements: [],
    stats: { total: 0, maintenance: 0, recent: [] },
    loading: false,
    _loaded: false,
    _loadedStats: false,
    _loadedCategoryId: null,
  }),
  getters: {
    totalStock(state) {
      return state.stats.total || state.equipements.length
    },
    maintenanceCount(state) {
      return state.stats.maintenance
    },
    recentMaterials(state) {
      if (state.stats.recent.length) return state.stats.recent
      return state.equipements.slice().reverse().slice(0, 8)
    },
  },
  actions: {
    getMaterials(categoryId) {
      const id = Number(categoryId)
      return this.equipements.filter((e) => e.categorie_id === id)
    },
    async fetchStats(force = false) {
      if (!force && this._loadedStats) return
      const { data } = await api.get('/equipements/stats')
      this.stats = data
      this._loadedStats = true
    },
    async fetchEquipements(force = false, categoryId = null) {
      const cid = categoryId ? Number(categoryId) : null
      if (!force && this._loaded && this._loadedCategoryId === cid) return
      this.loading = true
      try {
        const params = { limit: 500 }
        if (cid) params.categorie_id = cid
        const { data } = await api.get('/equipements', { params })
        this.equipements = data.items
        this._loaded = true
        this._loadedCategoryId = cid
      } finally {
        this.loading = false
      }
    },
    async addMaterial(categoryId, data) {
      const payload = {
        nom: data.name,
        reference: data.reference || `REF-${Date.now()}`,
        marque: data.marque || null,
        modele: data.modele || null,
        numero_serie: data.numero_serie || null,
        date_acquisition: data.date_acquisition || null,
        categorie_id: Number(categoryId),
        statut_id: Number(data.statut_id),
        emplacement_id: data.emplacement_id ? Number(data.emplacement_id) : null,
        description: data.description || null,
      }
      const { data: created } = await api.post('/equipements', payload)
      this.equipements.push(created)
      this._loadedStats = false
      return created
    },
    async updateMaterial(id, data) {
      const payload = {
        nom: data.name,
        marque: data.marque || null,
        modele: data.modele || null,
        numero_serie: data.numero_serie || null,
        date_acquisition: data.date_acquisition || null,
        statut_id: data.statut_id ? Number(data.statut_id) : undefined,
        emplacement_id: data.emplacement_id ? Number(data.emplacement_id) : null,
        description: data.description || null,
      }
      const { data: updated } = await api.put(`/equipements/${id}`, payload)
      const idx = this.equipements.findIndex((e) => e.id === Number(id))
      if (idx !== -1) this.equipements[idx] = updated
      this._loadedStats = false
      return updated
    },
    async removeMaterial(id) {
      await api.delete(`/equipements/${id}`)
      this.equipements = this.equipements.filter((e) => e.id !== Number(id))
      this._loadedStats = false
    },
  },
})