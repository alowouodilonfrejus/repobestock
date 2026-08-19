<template>
  <NuxtLayout name="dashboard">
    <div v-if="equipement" class="max-w-6xl mx-auto">
      <div class="mb-10 flex items-start justify-between">
        <div class="flex items-center gap-4">
          <Icon :name="category?.icon || 'heroicons:archive-box'" class="h-10 w-10 text-blue-900" />
          <div>
            <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">{{ equipement.nom }}</h2>
            <p class="text-gray-500 mt-1 text-lg">
              <span class="font-mono text-sm bg-gray-100 px-1.5 py-0.5 rounded mr-2">{{ equipement.reference }}</span>
              {{ category?.name || '—' }}
            </p>
          </div>
        </div>
        <NuxtLink
          :to="`/materiel/${equipement.categorie_id}/${equipement.id}`"
          class="px-5 py-2.5 bg-blue-900 text-white rounded-lg text-sm font-semibold hover:bg-blue-800 transition"
        >
          Modifier
        </NuxtLink>
      </div>

      <div class="grid grid-cols-3 gap-8">
        <div class="col-span-1 space-y-6">
          <UiCard title="Informations" class="shadow-sm border border-gray-200">
            <dl class="space-y-4 text-sm">
              <div>
                <dt class="text-gray-500">Statut</dt>
                <dd>
                  <span :class="['px-3 py-1 rounded-full text-xs font-semibold', statusClass(equipement.statut_id)]">
                    {{ statutName(equipement.statut_id) }}
                  </span>
                </dd>
              </div>
              <div>
                <dt class="text-gray-500">Emplacement</dt>
                <dd class="font-semibold text-gray-800">{{ emplacementName(equipement.emplacement_id) }}</dd>
              </div>
              <div>
                <dt class="text-gray-500">Marque</dt>
                <dd class="font-semibold text-gray-800">{{ equipement.marque || '—' }}</dd>
              </div>
              <div>
                <dt class="text-gray-500">Modèle</dt>
                <dd class="font-semibold text-gray-800">{{ equipement.modele || '—' }}</dd>
              </div>
              <div>
                <dt class="text-gray-500">Numéro de série</dt>
                <dd class="font-semibold text-gray-800">{{ equipement.numero_serie || '—' }}</dd>
              </div>
              <div>
                <dt class="text-gray-500">Date d'acquisition</dt>
                <dd class="font-semibold text-gray-800">{{ equipement.date_acquisition || '—' }}</dd>
              </div>
              <div v-if="equipement.description">
                <dt class="text-gray-500">Description</dt>
                <dd class="font-semibold text-gray-800">{{ equipement.description }}</dd>
              </div>
            </dl>
          </UiCard>
        </div>

        <div class="col-span-2">
          <UiCard title="Historique de cet équipement" class="shadow-sm border border-gray-200">
            <div v-if="loadingHistorique" class="text-center py-10 text-gray-500">Chargement...</div>
            <div v-else-if="historique.length === 0" class="text-center py-10 text-gray-500">
              Aucune action enregistrée pour cet équipement.
            </div>
            <div v-else class="divide-y divide-gray-100">
              <div v-for="entry in historique" :key="entry.id" class="py-4 flex items-start gap-4">
                <Icon :name="actionIcon(entry.action)" class="h-6 w-6 mt-1 text-gray-500" />
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <span :class="['px-2 py-0.5 rounded-full text-xs font-semibold', actionClass(entry.action)]">
                      {{ actionLabel(entry.action) }}
                    </span>
                  </div>
                  <p class="text-sm text-gray-600 mt-1">
                    <template v-if="entry.ancienne_valeur && entry.nouvelle_valeur">
                      {{ entry.ancienne_valeur }} → {{ entry.nouvelle_valeur }}
                    </template>
                    <template v-else-if="entry.nouvelle_valeur">
                      {{ entry.nouvelle_valeur }}
                    </template>
                    <template v-else-if="entry.ancienne_valeur">
                      {{ entry.ancienne_valeur }}
                    </template>
                  </p>
                  <p class="text-xs text-gray-400 mt-1">{{ formatDate(entry.date_action) }}</p>
                  <p class="text-xs text-gray-500 mt-0.5">
                    <Icon name="heroicons:user-circle" class="h-3.5 w-3.5 inline-block mr-1 -mt-0.5" />
                    {{ entry.utilisateur_nom || 'Utilisateur inconnu' }}
                  </p>
                </div>
              </div>
            </div>
          </UiCard>
        </div>
      </div>
    </div>
    <div v-else class="text-center py-10">
      <h2 class="text-xl text-gray-600">Équipement non trouvé.</h2>
      <NuxtLink to="/categories" class="text-blue-900 font-semibold hover:underline">Retour aux catégories</NuxtLink>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import { useEquipementsStore } from '@/stores/equipements'
import { useHistoriqueStore } from '@/stores/historique'

const route = useRoute()
const catStore = useCategoriesStore()
const eqStore = useEquipementsStore()
const histStore = useHistoriqueStore()

const historique = ref([])
const loadingHistorique = ref(false)

onMounted(async () => {
  await Promise.all([catStore.fetchReferentiels(), eqStore.fetchEquipements()])
  await loadHistorique()
})

const equipement = computed(() => eqStore.equipements.find((e) => e.id === Number(route.params.id)))
const category = computed(() => catStore.categories.find((c) => c.id === equipement.value?.categorie_id))

const loadHistorique = async () => {
  if (!equipement.value) return
  loadingHistorique.value = true
  try {
    historique.value = await histStore.fetchEquipementHistorique(equipement.value.id)
  } catch {
    historique.value = []
  } finally {
    loadingHistorique.value = false
  }
}

const statutName = (statutId) => {
  const st = catStore.statuts.find((s) => s.id === statutId)
  return st?.nom || '—'
}

const statusClass = (statutId) => {
  const nom = statutName(statutId).toLowerCase()
  if (nom.includes('maintenance')) return 'bg-amber-100 text-amber-800'
  if (nom.includes('défectueux') || nom.includes('defectueux')) return 'bg-red-100 text-red-800'
  return 'bg-green-100 text-green-800'
}

const emplacementName = (id) => {
  const emp = catStore.emplacements.find((e) => e.id === id)
  return emp?.nom || 'Non affecté'
}

const actionLabel = (action) => {
  const labels = { creation: 'Création', modification: 'Modification', suppression: 'Suppression' }
  return labels[action] || action
}

const actionIcon = (action) => {
  const icons = {
    creation: 'heroicons:plus-circle',
    modification: 'heroicons:pencil-square',
    suppression: 'heroicons:trash',
  }
  return icons[action] || 'heroicons:clock'
}

const actionClass = (action) => {
  if (action === 'creation') return 'bg-green-100 text-green-800'
  if (action === 'modification') return 'bg-blue-100 text-blue-800'
  if (action === 'suppression') return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
}

const formatDate = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}
</script>
