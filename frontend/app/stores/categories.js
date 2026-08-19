import { defineStore } from 'pinia'
import api from '~/utils/api'

const DEFAULT_ICON = 'heroicons:archive-box'

const ICONS = {
  informatique: 'heroicons:computer-desktop',
  bureau: 'heroicons:printer',
  nettoyage: 'heroicons:sparkles',
  immobilier: 'heroicons:building-office-2',
}

function pickIcon(name) {
  const lower = name.toLowerCase()
  for (const key of Object.keys(ICONS)) {
    if (lower.includes(key)) return ICONS[key]
  }
  return DEFAULT_ICON
}

const DEFAULT_FIELDS = [
  { key: 'marque', label: 'Marque', type: 'text', placeholder: 'ex: Dell, HP, Lenovo' },
  { key: 'modele', label: 'Modèle', type: 'text', placeholder: 'ex: PowerEdge R750' },
  { key: 'numero_serie', label: 'Numéro de série', type: 'text', placeholder: 'SN-XXXX-XXXX' },
  { key: 'date_acquisition', label: "Date d'acquisition", type: 'date' },
]

const FIELDS_BY_CATEGORY = {
  informatique: [
    { key: 'modele', label: "Nom du modèle", type: 'text', placeholder: 'ex: PowerEdge R750, Latitude 5420' },
    { key: 'date_acquisition', label: "Date d'acquisition", type: 'date' },
    { key: 'marque', label: 'Marque', type: 'text', placeholder: 'ex: Dell, HP, Lenovo' },
    { key: 'description', label: 'Caractéristiques', type: 'textarea', placeholder: 'ex: 32 Go RAM, SSD 1 To, i7' },
    { key: 'numero_serie', label: 'Numéro de série', type: 'text', placeholder: 'SN-XXXX-XXXX' },
  ],
  immobilier: [
    { key: 'modele', label: "Nom du modèle", type: 'text', placeholder: 'ex: Fauteuil ergonomique, bureau 160cm, climatiseur mural' },
    { key: 'marque', label: 'Marque', type: 'text', placeholder: 'ex: IKEA, Steelcase, Daikin' },
    { key: 'numero_serie', label: 'Numéro de série', type: 'text', placeholder: 'SN-XXXX-XXXX' },
    { key: 'date_acquisition', label: "Date d'acquisition", type: 'date' },
    { key: 'description', label: 'Caractéristiques', type: 'textarea', placeholder: 'ex: Mobilier de bureau, localisation, surface couverte' },
  ],
}

export const useCategoriesStore = defineStore('categories', {
  state: () => ({
    categories: [],
    statuts: [],
    emplacements: [],
    loading: false,
    _loaded: false,
  }),
  actions: {
    fieldsFor(categoryId) {
      const id = Number(categoryId)
      const category = this.categories.find((c) => c.id === id)
      if (!category) return DEFAULT_FIELDS
      const key = category.nom.toLowerCase()
      return FIELDS_BY_CATEGORY[key] || DEFAULT_FIELDS
    },
    async fetchCategories() {
      const { data } = await api.get('/categories')
      this.categories = data.map((c) => ({
        ...c,
        name: c.nom,
        icon: pickIcon(c.nom),
      }))
    },
    async fetchStatuts() {
      const { data } = await api.get('/statuts')
      this.statuts = data
    },
    async fetchEmplacements() {
      const { data } = await api.get('/emplacements')
      this.emplacements = data
    },
    async fetchReferentiels(force = false) {
      if (this._loaded && !force) return
      this.loading = true
      try {
        await Promise.all([
          this.fetchCategories(),
          this.fetchStatuts(),
          this.fetchEmplacements(),
        ])
        this._loaded = true
      } finally {
        this.loading = false
      }
    },
  },
})