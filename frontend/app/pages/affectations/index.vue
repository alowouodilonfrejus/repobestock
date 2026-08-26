<template>
  <NuxtLayout name="dashboard">
    <header class="flex items-center justify-between mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Affectations</h1>
      <NuxtLink
        v-if="can('affectations:write')"
        to="/affectations/nouvelle"
        class="px-6 py-2.5 bg-blue-900 text-white rounded-xl text-sm font-semibold hover:bg-blue-800 transition shadow-sm"
      >
        + Nouvelle affectation
      </NuxtLink>
    </header>
    <p class="text-gray-500 -mt-4 mb-8 text-sm">Suivez les matériels attribués aux collaborateurs et gérez les retours.</p>

    <!-- Indicateurs -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
      <SummaryCard title="TOTAL" :value="affectationsStore.total" subtext="Toutes affectations" icon="heroicons:clipboard-document-list" />
      <SummaryCard title="ACTIVES" :value="activesCount" subtext="En cours" icon="heroicons:check-circle" />
      <SummaryCard title="PARTIELLES" :value="partiellesCount" subtext="Retour partiel" icon="heroicons:clock" />
      <SummaryCard title="RETOURNÉES" :value="retourneesCount" subtext="Clôturées" icon="heroicons:arrow-uturn-left" />
    </div>

    <!-- Liste -->
    <div class="bg-white p-4 sm:p-6 rounded-xl shadow-md border border-gray-100">
      <div class="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
        <table class="w-full border-collapse min-w-[720px]">
          <thead>
            <tr>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">#</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Collaborateur</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Matériels</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Date</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Retour prévu</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Statut</th>
              <th class="text-xs text-gray-500 text-right p-4 uppercase tracking-wide">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in affectationsStore.affectations" :key="a.id" class="border-t border-gray-100 hover:bg-gray-50">
              <td class="p-4 font-mono text-xs text-gray-400">{{ a.id }}</td>
              <td class="p-4">
                <NuxtLink :to="`/employes/${a.employe_id}`" class="text-sm font-semibold text-blue-600 hover:text-blue-500">{{ a.employe_nom_complet }}</NuxtLink>
                <p class="text-xs text-gray-400 font-mono">{{ a.employe_matricule }}</p>
              </td>
              <td class="p-4">
                <ul class="space-y-1">
                  <li v-for="item in a.items" :key="item.id" class="text-sm flex items-center gap-1.5">
                    <span class="font-mono text-xs text-gray-500">{{ item.equipement_reference }}</span>
                    <span class="text-gray-700">{{ item.equipement_nom }}</span>
                    <span class="text-xs text-gray-500">×{{ item.quantite }}</span>
                    <span v-if="item.quantite_retournee > 0" class="px-2 py-0.5 rounded-full text-xs font-medium bg-teal-50 text-teal-700">{{ item.quantite_retournee }} rendu</span>
                  </li>
                </ul>
              </td>
              <td class="p-4 text-sm text-gray-500 whitespace-nowrap">{{ formatDate(a.date_affectation) }}</td>
              <td class="p-4 text-sm text-gray-500 whitespace-nowrap">{{ formatDate(a.date_retour_prevue) || '—' }}</td>
              <td class="p-4">
                <span class="px-3 py-1 rounded-full text-xs font-medium" :class="statutBadge(a.statut)">{{ statutLabel(a.statut) }}</span>
              </td>
              <td class="p-4 text-right">
                <button
                  v-if="a.statut === 'active' || a.statut === 'partielle'"
                  @click="openRetour(a)"
                  class="text-orange-600 hover:text-orange-700 text-sm font-semibold hover:bg-orange-50 px-3 py-1.5 rounded-xl transition"
                >
                  Retour
                </button>
              </td>
            </tr>
            <tr v-if="!affectationsStore.loading && affectationsStore.affectations.length === 0">
              <td colspan="7" class="p-12 text-center text-sm text-gray-400">Aucune affectation enregistrée.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal retour -->
    <div v-if="retourModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="retourModal = false">
      <div class="bg-white rounded-xl shadow-xl max-w-xl w-full max-h-[90vh] overflow-y-auto p-6 border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-900 mb-1">Retour de matériel</h3>
        <p class="text-sm text-gray-500 mb-5">{{ retourCible?.employe_nom_complet }} — affectation #{{ retourCible?.id }}</p>

        <form @submit.prevent="submitRetour" class="space-y-4">
          <div class="border border-gray-100 rounded-xl divide-y divide-gray-100 overflow-hidden">
            <div v-for="item in lignesRetour" :key="item.item.id" class="p-4">
              <label class="flex items-center gap-2 text-sm font-semibold text-gray-900">
                <input v-model="item.inclus" type="checkbox" class="rounded border-gray-300 text-blue-900 focus:ring-blue-900" />
                <span class="font-mono text-xs text-gray-500">{{ item.item.equipement_reference }}</span>
                {{ item.item.equipement_nom }}
                <span class="ml-auto text-xs text-gray-400">reste : {{ item.item.quantite - item.item.quantite_retournee }}</span>
              </label>
              <div v-if="item.inclus" class="grid grid-cols-2 gap-3 mt-3">
                <div>
                  <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Quantité retournée</label>
                  <input v-model.number="item.quantite_retournee" type="number" min="1" :max="item.item.quantite - item.item.quantite_retournee" class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900" />
                </div>
                <div>
                  <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">État au retour</label>
                  <select v-model="item.etat_retour" class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm bg-white outline-none focus:ring-2 focus:ring-blue-900">
                    <option value="neuf">Neuf</option>
                    <option value="tres_bon">Très bon</option>
                    <option value="bon">Bon</option>
                    <option value="a_verifier">À vérifier</option>
                    <option value="endommage">Endommagé</option>
                  </select>
                </div>
                <div class="col-span-2">
                  <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Problème constaté (optionnel)</label>
                  <input v-model="item.probleme_constate" maxlength="10000" class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900" />
                </div>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Date du retour</label>
            <input v-model="dateRetour" type="date" :max="today" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900" />
          </div>

          <p v-if="errorMessage" class="text-red-600 text-sm bg-red-50 border border-red-100 rounded-xl px-3.5 py-2.5">{{ errorMessage }}</p>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="retourModal = false" class="px-4 py-2.5 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-xl transition">Annuler</button>
            <button type="submit" :disabled="saving || !auMoinsUnInclus" class="px-6 py-2.5 bg-blue-900 text-white rounded-xl text-sm font-semibold hover:bg-blue-800 transition shadow-sm disabled:opacity-50">Valider le retour</button>
          </div>
        </form>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useAffectationsStore } from '~/stores/affectations'
import { useToast } from '~/composables/useToast'
import SummaryCard from '~/components/dashboard/SummaryCard.vue'

const affectationsStore = useAffectationsStore()
const { can } = useRole()
const toast = useToast()

const activesCount = computed(() => affectationsStore.affectations.filter(a => a.statut === 'active').length)
const partiellesCount = computed(() => affectationsStore.affectations.filter(a => a.statut === 'partielle').length)
const retourneesCount = computed(() => affectationsStore.affectations.filter(a => a.statut === 'retournee').length)

const retourModal = ref(false)
const retourCible = ref(null)
const saving = ref(false)
const errorMessage = ref('')
const dateRetour = ref('')
const today = new Date().toISOString().slice(0, 10)
const lignesRetour = reactive([])
const auMoinsUnInclus = computed(() => lignesRetour.some(l => l.inclus))

function formatDate(dateStr) { if (!dateStr) return null; return new Date(dateStr).toLocaleDateString('fr-FR') }
function statutBadge(statut) {
  const badges = { active: 'bg-blue-50 text-blue-700', partielle: 'bg-amber-50 text-amber-700', retournee: 'bg-teal-50 text-teal-700', annulee: 'bg-gray-100 text-gray-500' }
  return badges[statut] || 'bg-gray-100 text-gray-500'
}
function statutLabel(statut) {
  return { active: 'Active', partielle: 'Retour partiel', retournee: 'Retournée', annulee: 'Annulée' }[statut] || statut
}

function openRetour(affectation) {
  retourCible.value = affectation
  dateRetour.value = today
  errorMessage.value = ''
  lignesRetour.splice(0)
  for (const item of affectation.items) {
    if (item.quantite - item.quantite_retournee > 0) {
      lignesRetour.push({ item, inclus: true, quantite_retournee: item.quantite - item.quantite_retournee, etat_retour: 'bon', probleme_constate: '' })
    }
  }
  retourModal.value = true
}

async function submitRetour() {
  saving.value = true; errorMessage.value = ''
  try {
    await affectationsStore.retourMateriel(retourCible.value.id, {
      date_retour: dateRetour.value || undefined,
      commentaire: null,
      items: lignesRetour.filter(l => l.inclus).map(l => ({ affectation_item_id: l.item.id, quantite_retournee: l.quantite_retournee, etat_retour: l.etat_retour, probleme_constate: l.probleme_constate || undefined })),
    })
    toast.success('Retour enregistré'); retourModal.value = false
    await affectationsStore.fetchAffectations(true)
  } catch (err) { errorMessage.value = err.response?.data?.detail || 'Erreur lors du retour' }
  finally { saving.value = false }
}

onMounted(() => affectationsStore.fetchAffectations(true))
</script>
