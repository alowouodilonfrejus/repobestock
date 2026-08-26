<template>
  <NuxtLayout name="dashboard">
    <header class="flex items-center justify-between mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Maintenance</h1>
      <button v-if="can('maintenances:write')" @click="openDemarrage" class="px-6 py-2.5 bg-blue-900 text-white rounded-xl text-sm font-semibold hover:bg-blue-800 transition shadow-sm">
        + Nouvelle maintenance
      </button>
    </header>
    <p class="text-gray-500 -mt-4 mb-8 text-sm">Les matériels en maintenance ne sont plus affectables.</p>

    <!-- Indicateurs -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <SummaryCard title="MAINTENANCES EN COURS" :value="enCoursCount" subtext="Matériels immobilisés" icon="heroicons:wrench-screwdriver" />
      <SummaryCard title="MAINTENANCES TERMINÉES" :value="termineesCount" subtext="Historique complet" icon="heroicons:check-circle" />
      <SummaryCard title="TOTAL MAINTENANCES" :value="maintenancesStore.total" subtext="Toutes opérations" icon="heroicons:clipboard-document-list" />
    </div>

    <!-- Liste -->
    <div class="bg-white p-4 sm:p-6 rounded-xl shadow-md border border-gray-100">
      <div class="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
        <table class="w-full border-collapse min-w-[720px]">
          <thead>
            <tr>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Matériel</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Motif</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Début</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Fin</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide hidden md:table-cell">Technicien</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide hidden md:table-cell">Coût</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Statut</th>
              <th class="text-xs text-gray-500 text-right p-4 uppercase tracking-wide">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in maintenancesStore.maintenances" :key="m.id" class="border-t border-gray-100 hover:bg-gray-50">
              <td class="p-4">
                <p class="font-mono text-xs text-gray-400">{{ m.equipement_reference }}</p>
                <p class="text-sm font-semibold text-gray-900">{{ m.equipement_nom }}</p>
              </td>
              <td class="p-4 text-sm text-gray-600 max-w-[200px] truncate">{{ m.motif || '—' }}</td>
              <td class="p-4 text-sm text-gray-500 whitespace-nowrap">{{ formatDate(m.date_debut) }}</td>
              <td class="p-4 text-sm text-gray-500 whitespace-nowrap">{{ formatDate(m.date_fin) || '—' }}</td>
              <td class="p-4 text-sm text-gray-500 hidden md:table-cell">{{ m.technicien || '—' }}</td>
              <td class="p-4 text-sm text-gray-500 hidden md:table-cell">{{ formatCout(m.cout) }}</td>
              <td class="p-4">
                <span class="px-3 py-1 rounded-full text-xs font-medium" :class="m.statut === 'en_cours' ? 'bg-orange-50 text-orange-700' : 'bg-teal-50 text-teal-700'">
                  {{ m.statut === 'en_cours' ? 'En cours' : 'Terminée' }}
                </span>
              </td>
              <td class="p-4 text-right">
                <button v-if="m.statut === 'en_cours' && can('maintenances:write')" @click="openCloture(m)" class="text-teal-700 hover:bg-teal-50 px-3 py-1.5 rounded-xl text-sm font-semibold transition">Clôturer</button>
              </td>
            </tr>
            <tr v-if="!maintenancesStore.loading && maintenancesStore.maintenances.length === 0">
              <td colspan="8" class="p-12 text-center text-sm text-gray-400">Aucune maintenance enregistrée.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal démarrage -->
    <div v-if="showDemarrage" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="showDemarrage = false">
      <div class="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-900 mb-5">Nouvelle maintenance</h3>
        <form @submit.prevent="submitDemarrage" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Matériel *</label>
            <select v-model="form.equipement_id" required class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm bg-white outline-none focus:ring-2 focus:ring-blue-900">
              <option :value="null" disabled>— Choisir un matériel —</option>
              <option v-for="eq in equipementsStore.equipements" :key="eq.id" :value="eq.id">{{ eq.reference }} — {{ eq.nom }}</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Date de début *</label>
              <input v-model="form.date_debut" type="date" required class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Technicien</label>
              <input v-model="form.technicien" maxlength="100" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Motif</label>
            <input v-model="form.motif" maxlength="200" placeholder="Ex. : écran cassé, panne alim." class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Description</label>
            <textarea v-model="form.description" rows="3" maxlength="10000" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900"></textarea>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Coût estimé (FCFA)</label>
            <input v-model.number="form.cout" type="number" min="0" step="0.01" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900" />
          </div>
          <p v-if="errorMessage" class="text-red-600 text-sm bg-red-50 border border-red-100 rounded-xl px-3.5 py-2.5">{{ errorMessage }}</p>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="showDemarrage = false" class="px-4 py-2.5 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-xl transition">Annuler</button>
            <button type="submit" :disabled="saving" class="px-6 py-2.5 bg-blue-900 text-white rounded-xl text-sm font-semibold hover:bg-blue-800 transition shadow-sm disabled:opacity-50">Démarrer</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal clôture -->
    <div v-if="clotureCible" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="clotureCible = null">
      <div class="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-900 mb-1">Clôturer la maintenance</h3>
        <p class="text-sm text-gray-500 mb-5">{{ clotureCible.equipement_reference }} — {{ clotureCible.equipement_nom }}</p>
        <form @submit.prevent="submitCloture" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Date de fin *</label>
            <input v-model="clotureForm.date_fin" type="date" required class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Commentaire</label>
            <textarea v-model="clotureForm.commentaire" rows="3" maxlength="10000" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900"></textarea>
          </div>
          <p v-if="errorMessage" class="text-red-600 text-sm bg-red-50 border border-red-100 rounded-xl px-3.5 py-2.5">{{ errorMessage }}</p>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="clotureCible = null" class="px-4 py-2.5 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-xl transition">Annuler</button>
            <button type="submit" :disabled="saving" class="px-6 py-2.5 bg-teal-700 text-white rounded-xl text-sm font-semibold hover:bg-teal-800 transition shadow-sm disabled:opacity-50">Clôturer</button>
          </div>
        </form>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useMaintenancesStore } from '~/stores/maintenances'
import { useEquipementsStore } from '~/stores/equipements'
import { useToast } from '~/composables/useToast'
import SummaryCard from '~/components/dashboard/SummaryCard.vue'

const maintenancesStore = useMaintenancesStore()
const { can } = useRole()
const equipementsStore = useEquipementsStore()
const toast = useToast()

const showDemarrage = ref(false)
const clotureCible = ref(null)
const saving = ref(false)
const errorMessage = ref('')

const enCoursCount = computed(() => maintenancesStore.maintenances.filter(m => m.statut === 'en_cours').length)
const termineesCount = computed(() => maintenancesStore.maintenances.filter(m => m.statut === 'terminee').length)

const form = reactive({ equipement_id: null, date_debut: new Date().toISOString().slice(0, 10), motif: '', description: '', cout: null, technicien: '' })
const clotureForm = reactive({ date_fin: new Date().toISOString().slice(0, 10), commentaire: '' })

function formatDate(dateStr) { if (!dateStr) return null; return new Date(dateStr).toLocaleDateString('fr-FR') }
function formatCout(cout) { if (cout === null || cout === undefined) return '—'; return Number(cout).toLocaleString('fr-FR') }
function openDemarrage() {
  Object.assign(form, { equipement_id: null, date_debut: new Date().toISOString().slice(0, 10), motif: '', description: '', cout: null, technicien: '' })
  errorMessage.value = ''; showDemarrage.value = true
}
function openCloture(maintenance) {
  clotureCible.value = maintenance; clotureForm.date_fin = new Date().toISOString().slice(0, 10); clotureForm.commentaire = ''; errorMessage.value = ''
}
async function submitDemarrage() {
  saving.value = true; errorMessage.value = ''
  try {
    const payload = { ...form }; if (!payload.cout) delete payload.cout
    await maintenancesStore.demarrer(form.equipement_id, payload)
    toast.success('Maintenance démarrée'); showDemarrage.value = false
  } catch (err) { errorMessage.value = err.response?.data?.detail || "Erreur lors du démarrage" }
  finally { saving.value = false }
}
async function submitCloture() {
  saving.value = true; errorMessage.value = ''
  try {
    await maintenancesStore.cloturer(clotureCible.value.id, { date_fin: clotureForm.date_fin, commentaire: clotureForm.commentaire || undefined })
    toast.success('Maintenance clôturée — matériel de nouveau disponible'); clotureCible.value = null
  } catch (err) { errorMessage.value = err.response?.data?.detail || "Erreur lors de la clôture" }
  finally { saving.value = false }
}

onMounted(() => { maintenancesStore.fetchMaintenances(true); equipementsStore.fetchEquipements() })
</script>
