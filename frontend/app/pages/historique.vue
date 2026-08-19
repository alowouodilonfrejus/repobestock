<template>
  <NuxtLayout name="dashboard">
    <div class="max-w-6xl mx-auto">
      <div class="mb-10 flex items-center justify-between">
        <div>
          <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Historique des actions</h2>
          <p class="text-gray-500 mt-2 text-lg">Toutes les modifications effectuées sur les équipements.</p>
        </div>
        <button
          @click="load"
          class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-100 transition"
        >
          ↻ Rafraîchir
        </button>
      </div>

      <UiCard title="Journal d'activité" class="shadow-sm border border-gray-200">
        <div v-if="histStore.loading" class="text-center py-10 text-gray-500">Chargement...</div>
        <div v-else-if="histStore.historique.length === 0" class="text-center py-10 text-gray-500">
          Aucune action enregistrée pour le moment.
        </div>
        <div v-else class="divide-y divide-gray-100">
          <div v-for="entry in histStore.historique" :key="entry.id" class="py-4 flex items-start gap-4">
            <Icon :name="actionIcon(entry.action)" class="h-6 w-6 mt-1 text-gray-500" />
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span class="font-semibold text-gray-900">{{ equipementName(entry.equipement_id) }}</span>
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
                <template v-else>
                  — 
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
  </NuxtLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import { useHistoriqueStore } from '@/stores/historique'
import { useEquipementsStore } from '@/stores/equipements'

const histStore = useHistoriqueStore()
const eqStore = useEquipementsStore()

const load = () => {
  Promise.all([
    histStore.fetchHistorique().catch(() => {}),
    eqStore.fetchStats().catch(() => {}),
  ])
}

onMounted(load)

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

const equipementName = (id) => {
  if (!id) return 'Équipement supprimé'
  const eq = eqStore.equipements.find((e) => e.id === id)
  if (eq) return eq.nom
  const recent = eqStore.stats.recent.find((e) => e.id === id)
  return recent?.nom || 'Équipement supprimé'
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
