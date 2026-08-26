<template>
  <NuxtLayout name="dashboard">
    <header class="flex items-center justify-between mb-8">
      <NuxtLink to="/employes" class="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-500">
        <Icon name="heroicons:arrow-left" class="h-4 w-4" /> Collaborateurs
      </NuxtLink>
      <span class="text-xs font-semibold px-3 py-1 rounded-full" :class="employe && employe.actif ? 'bg-teal-50 text-teal-700' : 'bg-gray-100 text-gray-500'">
        {{ employe ? (employe.actif ? 'Actif' : 'Inactif') : '—' }}
      </span>
    </header>

    <!-- Fiche collaborateur -->
    <div v-if="employe" class="bg-white p-6 sm:p-8 rounded-xl shadow-md border border-gray-100 flex flex-col">
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 rounded-full bg-blue-900 text-white flex items-center justify-center text-xl font-bold flex-shrink-0">
          {{ initials }}
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ employe.nom_complet }}</h1>
          <p class="text-sm text-gray-500 font-mono">{{ employe.matricule }} · {{ employe.fonction || '—' }}</p>
        </div>
      </div>
      <dl class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-5 mt-6 pt-6 border-t border-gray-100">
        <div>
          <dt class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Département</dt>
          <dd class="text-sm font-semibold text-gray-900 mt-1">{{ employe.departement || '—' }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Fonction</dt>
          <dd class="text-sm font-semibold text-gray-900 mt-1">{{ employe.fonction || '—' }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Téléphone</dt>
          <dd class="text-sm font-semibold text-gray-900 mt-1">{{ employe.telephone || '—' }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Email</dt>
          <dd class="text-sm font-semibold text-gray-900 mt-1 break-all">{{ employe.email || '—' }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Date d'arrivée</dt>
          <dd class="text-sm font-semibold text-gray-900 mt-1">{{ formatDate(employe.date_arrivee) || '—' }}</dd>
        </div>
      </dl>
    </div>

    <!-- Matériels attribués -->
    <div class="flex items-center justify-between mt-8 mb-4">
      <h3 class="text-lg font-semibold text-gray-700">Matériels attribués</h3>
      <NuxtLink
        v-if="employe && can('affectations:write')"
        :to="`/affectations/nouvelle?employe_id=${route.params.id}`"
        class="px-4 py-2 bg-blue-900 text-white rounded-xl text-sm font-semibold hover:bg-blue-800 transition shadow-sm"
      >
        + Affecter du matériel
      </NuxtLink>
    </div>

    <div class="bg-white p-4 sm:p-6 rounded-xl shadow-md border border-gray-100">
      <div class="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
        <table class="w-full border-collapse min-w-[520px]">
          <thead>
            <tr>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Référence</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Matériel</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Qté</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">État</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Affecté le</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Retour prévu</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="materiel in materiels" :key="materiel.affectation_item_id" class="border-t border-gray-100 hover:bg-gray-50">
              <td class="p-4 font-mono text-xs font-semibold text-gray-700">{{ materiel.reference }}</td>
              <td class="p-4 text-sm font-medium text-gray-900">{{ materiel.nom }}</td>
              <td class="p-4 text-sm text-gray-700">×{{ materiel.quantite }}</td>
              <td class="p-4">
                <span class="px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700">{{ etatLabel(materiel.etat_affectation) }}</span>
              </td>
              <td class="p-4 text-sm text-gray-500">{{ formatDate(materiel.date_affectation) }}</td>
              <td class="p-4 text-sm">
                <span class="text-gray-500">{{ formatDate(materiel.date_retour_prevue) || '—' }}</span>
                <span v-if="materiel.date_retour_prevue && isEnRetard(materiel.date_retour_prevue)" class="ml-2 px-2 py-0.5 rounded-full text-xs font-medium bg-red-50 text-red-700">En retard</span>
              </td>
            </tr>
            <tr v-if="!loading && materiels.length === 0">
              <td colspan="6" class="p-12 text-center text-sm text-gray-400">Aucun matériel actuellement attribué à cet collaborateur.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p v-if="error" class="text-center text-sm text-red-600 mt-8 bg-red-50 border border-red-100 rounded-xl px-4 py-3">{{ error }}</p>
  </NuxtLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useEmployesStore } from '~/stores/employes'

const route = useRoute()
const employesStore = useEmployesStore()
const { can } = useRole()

const employe = ref(null)
const materiels = ref([])
const loading = ref(true)
const error = ref('')

const ETATS = {
  neuf: 'Neuf',
  tres_bon: 'Très bon',
  bon: 'Bon',
  a_verifier: 'À vérifier',
  endommage: 'Endommagé',
}

const initials = computed(() =>
  (employe.value?.nom_complet || '?')
    .split(' ')
    .map((m) => m[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
)

function etatLabel(valeur) {
  return ETATS[valeur] || valeur
}

function formatDate(dateStr) {
  if (!dateStr) return null
  return new Date(dateStr).toLocaleDateString('fr-FR')
}

function isEnRetard(dateStr) {
  return new Date(dateStr) < new Date(new Date().toDateString())
}

onMounted(async () => {
  try {
    const id = route.params.id
    const [emp, mats] = await Promise.all([
      employesStore.fetchEmploye(id),
      employesStore.fetchMateriels(id),
    ])
    employe.value = emp
    materiels.value = mats
  } catch (err) {
    error.value = err.response?.data?.detail || 'Collaborateur introuvable'
  } finally {
    loading.value = false
  }
})
</script>
