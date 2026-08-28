<template>
  <NuxtLayout name="dashboard">
    <header class="flex items-center justify-between mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Nouvelle affectation</h1>
      <NuxtLink to="/affectations" class="text-sm font-medium text-blue-600 hover:text-blue-500 flex items-center gap-1.5">
        <Icon name="heroicons:arrow-left" class="h-4 w-4" /> Affectations
      </NuxtLink>
    </header>
    <p class="text-gray-500 -mt-4 mb-8 text-sm">Affectez un ou plusieurs matériels à un collaborateur — opération atomique (une seule transaction).</p>

    <div class="bg-white p-6 sm:p-8 rounded-xl shadow-md border border-gray-100">
      <form @submit.prevent="submit" class="space-y-6">
        <!-- Collaborateur -->
        <div>
          <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Collaborateur *</label>
          <select v-model="employeId" required class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm bg-white outline-none focus:ring-2 focus:ring-blue-900">
            <option :value="null" disabled>— Sélectionner un collaborateur —</option>
            <option v-for="e in employesActifs" :key="e.id" :value="e.id">
              {{ e.nom_complet }} ({{ e.matricule }}){{ e.departement ? ` — ${e.departement}` : '' }}
            </option>
          </select>
        </div>

        <!-- Matériels groupés par catégorie -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide">Matériels à affecter *</label>
            <span class="text-xs font-semibold text-blue-900 bg-blue-50 px-3 py-1 rounded-full">{{ itemsSelectionnes.length }} sélectionné(s)</span>
          </div>

          <!-- Filtre par catégorie -->
          <div class="flex flex-wrap gap-2 mb-3">
            <button type="button" @click="filtreCat = null" class="px-3 py-1.5 rounded-full text-xs font-semibold transition" :class="filtreCat === null ? 'bg-blue-900 text-white shadow-sm' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
              Toutes
            </button>
            <button v-for="grp in groupesMateriels" :key="grp.categorie_id" type="button" @click="filtreCat = filtreCat === grp.categorie_id ? null : grp.categorie_id" class="px-3 py-1.5 rounded-full text-xs font-semibold transition" :class="filtreCat === grp.categorie_id ? 'bg-blue-900 text-white shadow-sm' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
              {{ grp.nom }} ({{ grp.items.length }})
            </button>
          </div>

          <!-- Groupes dépliables -->
          <div class="space-y-3">
            <div v-for="grp in groupesAffiches" :key="grp.categorie_id" class="border border-gray-100 rounded-xl overflow-hidden">
              <button type="button" @click="toggleGrp(grp.categorie_id)" class="w-full bg-gray-50 px-4 py-2.5 flex items-center justify-between hover:bg-gray-100 transition">
                <span class="flex items-center gap-2 text-sm font-bold text-gray-800">
                  <Icon :name="grpOuverts.includes(grp.categorie_id) ? 'heroicons:chevron-down' : 'heroicons:chevron-right'" class="h-4 w-4 text-gray-400" />
                  {{ grp.nom }}
                </span>
                <span class="text-xs text-gray-500">{{ grp.items.length }} matériel(s) · {{ selectionDansGrp(grp) }} sélectionné(s)</span>
              </button>
              <div v-show="grpOuverts.includes(grp.categorie_id)" class="divide-y divide-gray-50">
                <div v-for="eq in grp.items" :key="eq.id" class="px-4 py-3 flex flex-wrap sm:flex-nowrap items-center gap-3" :class="coches[eq.id] ? 'bg-blue-50/40' : 'hover:bg-gray-50/60'">
                  <input v-model="coches[eq.id]" type="checkbox" class="rounded border-gray-300 text-blue-900 focus:ring-blue-900 h-4 w-4 shrink-0" />
                  <div class="flex-1 min-w-[180px]">
                    <p class="text-sm font-medium text-gray-900 truncate">{{ eq.nom }}</p>
                    <p class="text-xs text-gray-500"><span class="font-mono">{{ eq.reference }}</span> · dispo : {{ eq.quantite_disponible }}</p>
                  </div>
                  <div class="flex items-center gap-2 shrink-0">
                    <input v-model.number="qtes[eq.id]" type="number" min="1" :max="eq.quantite_disponible" :disabled="!coches[eq.id]" class="w-20 border border-gray-200 rounded-xl px-2.5 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900 disabled:bg-gray-50 disabled:text-gray-400" />
                    <select v-model="etats[eq.id]" :disabled="!coches[eq.id]" class="w-32 border border-gray-200 rounded-xl px-2 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900 disabled:bg-gray-50 disabled:text-gray-400">
                      <option value="neuf">Neuf</option>
                      <option value="tres_bon">Très bon</option>
                      <option value="bon">Bon</option>
                      <option value="a_verifier">À vérifier</option>
                      <option value="endommage">Endommagé</option>
                    </select>
                  </div>
                  <p v-if="erreurPour(eq)" class="w-full text-xs text-red-600">{{ erreurPour(eq) }}</p>
                </div>
              </div>
            </div>
            <p v-if="groupesAffiches.length === 0" class="text-center text-sm text-gray-400 py-8">Aucun matériel disponible dans cette catégorie.</p>
          </div>
        </div>

        <!-- Dates -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Date d'affectation</label>
            <input v-model="dateAffectation" type="date" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Date prévue de retour</label>
            <input v-model="dateRetourPrevue" type="date" :min="dateAffectation || today" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Motif</label>
          <input v-model="motif" maxlength="200" placeholder="Ex. : équipement de poste de travail" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Commentaire</label>
          <textarea v-model="commentaire" rows="3" maxlength="10000" placeholder="Contexte de la remise…" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-900"></textarea>
        </div>

        <div v-if="itemsSelectionnes.length > 0" class="bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm">
          <p class="font-semibold text-blue-900 mb-2">Récapitulatif par catégorie</p>
          <div v-for="grp in recapGroupes" :key="grp.nom" class="mb-2 last:mb-0">
            <p class="text-xs font-bold uppercase tracking-wide text-blue-800 mb-1">{{ grp.nom }}</p>
            <ul class="list-disc list-inside text-gray-700 space-y-0.5 ml-1">
              <li v-for="eq in grp.items" :key="eq.id">{{ eq.nom }} <span class="font-mono text-xs text-gray-500">({{ eq.reference }})</span> ×{{ qtes[eq.id] }}</li>
            </ul>
          </div>
        </div>

        <p v-if="errorMessage" class="text-red-600 text-sm font-medium bg-red-50 border border-red-100 rounded-xl px-3.5 py-2.5">{{ errorMessage }}</p>

        <div class="flex justify-end gap-3 pt-2">
          <NuxtLink to="/affectations" class="px-5 py-2.5 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-xl transition">Annuler</NuxtLink>
          <button type="submit" :disabled="saving" class="px-6 py-2.5 bg-blue-900 text-white rounded-xl text-sm font-semibold hover:bg-blue-800 transition shadow-sm disabled:opacity-40 disabled:cursor-not-allowed">
            {{ saving ? 'Enregistrement…' : 'Valider l\'affectation' }}
          </button>
        </div>
      </form>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import api from '~/utils/api'
import { useEmployesStore } from '~/stores/employes'
import { useEquipementsStore } from '~/stores/equipements'
import { useCategoriesStore } from '~/stores/categories'
import { useToast } from '~/composables/useToast'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const employesStore = useEmployesStore()
const equipementsStore = useEquipementsStore()
const catStore = useCategoriesStore()

const employeId = ref(route.query.employe_id ? Number(route.query.employe_id) : null)
const dateAffectation = ref('')
const dateRetourPrevue = ref('')
const motif = ref('')
const commentaire = ref('')
const saving = ref(false)
const errorMessage = ref('')
const today = new Date().toISOString().slice(0, 10)

const filtreCat = ref(null)
const grpOuverts = ref([])
const coches = reactive({})
const qtes = reactive({})
const etats = reactive({})

const materielsDisponibles = computed(() => equipementsStore.equipements.filter(eq => eq.quantite_disponible > 0))
const employesActifs = computed(() => employesStore.employes.filter(e => e.actif))

function nomCategorie(id) {
  return catStore.categories.find(c => c.id === id)?.nom || 'Autres'
}

const groupesMateriels = computed(() => {
  const parCat = new Map()
  for (const eq of materielsDisponibles.value) {
    if (!parCat.has(eq.categorie_id)) {
      parCat.set(eq.categorie_id, { categorie_id: eq.categorie_id, nom: nomCategorie(eq.categorie_id), items: [] })
    }
    parCat.get(eq.categorie_id).items.push(eq)
  }
  return [...parCat.values()].sort((a, b) => a.nom.localeCompare(b.nom))
})

const groupesAffiches = computed(() =>
  filtreCat.value ? groupesMateriels.value.filter(g => g.categorie_id === filtreCat.value) : groupesMateriels.value
)

watch(groupesMateriels, (gs) => {
  for (const g of gs) {
    if (!grpOuverts.value.includes(g.categorie_id)) grpOuverts.value.push(g.categorie_id)
  }
}, { immediate: true })

function toggleGrp(id) {
  const i = grpOuverts.value.indexOf(id)
  if (i === -1) grpOuverts.value.push(id)
  else grpOuverts.value.splice(i, 1)
}

function erreurPour(eq) {
  if (!coches[eq.id]) return null
  const q = Number(qtes[eq.id])
  if (!q || q < 1) return 'Quantité minimale : 1'
  if (q > eq.quantite_disponible) return `Seulement ${eq.quantite_disponible} disponible(s)`
  return null
}

const itemsSelectionnes = computed(() =>
  materielsDisponibles.value.filter(eq => coches[eq.id] && !erreurPour(eq))
)

const aUneErreur = computed(() => materielsDisponibles.value.some(eq => erreurPour(eq)))

function selectionDansGrp(grp) {
  return grp.items.filter(eq => coches[eq.id]).length
}

const recapGroupes = computed(() => {
  const map = new Map()
  for (const eq of itemsSelectionnes.value) {
    const nom = nomCategorie(eq.categorie_id)
    if (!map.has(nom)) map.set(nom, [])
    map.get(nom).push(eq)
  }
  return [...map.entries()].map(([nom, items]) => ({ nom, items }))
})

const formulaireValide = computed(() => employeId.value !== null && itemsSelectionnes.value.length > 0 && !aUneErreur)

async function submit() {
  saving.value = true; errorMessage.value = ''
  try {
    const payload = {
      employe_id: employeId.value,
      date_affectation: dateAffectation.value || undefined,
      date_retour_prevue: dateRetourPrevue.value || undefined,
      motif: motif.value || undefined,
      commentaire: commentaire.value || undefined,
      items: itemsSelectionnes.value.map(eq => ({
        equipement_id: eq.id,
        quantite: Number(qtes[eq.id]) || 1,
        etat_affectation: etats[eq.id] || 'bon',
      })),
    }
    const { data } = await api.post('/affectations', payload)
    toast.success(`Affectation #${data.id} créée (${data.items.length} matériel(s))`)
    router.push('/affectations')
  } catch (err) { errorMessage.value = err.response?.data?.detail || "Erreur lors de l'affectation" }
  finally { saving.value = false }
}

onMounted(() => {
  employesStore.fetchEmployes(true)
  equipementsStore.fetchEquipements(true)
  catStore.fetchReferentiels()
})
</script>
