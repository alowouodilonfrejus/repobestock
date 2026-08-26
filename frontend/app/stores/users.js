import { defineStore } from 'pinia'
import api from '~/utils/api'

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [],
    loading: false,
    total: 0,
  }),
  actions: {
    async fetchUsers() {
      this.loading = true
      try {
        const { data } = await api.get('/users', { params: { limit: 500 } })
        this.users = data.items
        this.total = data.total
      } finally {
        this.loading = false
      }
    },
    async createUser(payload) {
      const { data } = await api.post('/users', payload)
      this.users.unshift(data)
      this.total += 1
      return data
    },
    async updateUser(id, payload) {
      const { data } = await api.put(`/users/${id}`, payload)
      const idx = this.users.findIndex((u) => u.id === Number(id))
      if (idx !== -1) this.users[idx] = data
      return data
    },
    async validerUser(id, payload = {}) {
      const { data } = await api.post(`/users/${id}/valider`, payload)
      const idx = this.users.findIndex((u) => u.id === Number(id))
      if (idx !== -1) this.users[idx] = data
      return data
    },
    async rejeterUser(id) {
      await api.post(`/users/${id}/rejeter`)
      this.users = this.users.filter((u) => u.id !== Number(id))
      this.total = Math.max(0, this.total - 1)
    },
    async deleteUser(id) {
      await api.delete(`/users/${id}`)
      this.users = this.users.filter((u) => u.id !== Number(id))
      this.total = Math.max(0, this.total - 1)
    },
  },
})