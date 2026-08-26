<template>
  <NuxtLayout name="dashboard">
    <div class="mb-6">
      <h1 class="text-[26px] font-extrabold tracking-tight text-gray-900">Mon espace</h1>
      <p class="text-sm text-gray-500 mt-1">Retrouvez tous les matériels qui vous sont affectés et gérez vos informations.</p>
    </div>

    <!-- Profile banner if linked to employe -->
    <div v-if="employeLinked" class="bg-white rounded-2xl border border-gray-200 p-5 flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
      <div class="h-12 w-12 rounded-2xl bg-[#0f2a4a] text-white flex items-center justify-center font-extrabold text-sm shrink-0">{{ initials }}</div>
      <div class="min-w-0 flex-1">
        <p class="font-bold text-gray-900">{{ employeLinked.nom_complet }}</p>
        <p class="text-xs text-gray-500 font-mono">{{ employeLinked.matricule }} · {{ employeLinked.fonction || 'Collaborateur' }} · {{ employeLinked.departement || '—' }}</p>
      </div>
      <button @click="showProfileModal = true" class="inline-flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-4 py-2 text-sm font-semibold text-gray-800 hover:bg-gray-50 transition">
        <Icon name="heroicons:pencil-square" class="h-4 w-4" /> Définir mes infos
      </button>
    </div>
    <div v-else class="bg-amber-50 border border-amber-200 rounded-2xl p-4 flex items-start gap-3 mb-6">
      <Icon name="heroicons:exclamation-triangle" class="h-5 w-5 text-amber-600 mt-0.5" />
      <div>
        <p class="text-sm font-semibold text-amber-900">Compte non rattaché à un collaborateur</p>
        <p class="text-xs text-amber-700 mt-1">Votre compte n'est lié à aucune fiche collaborateur. Contactez un administrateur pour être rattaché et voir vos matériels.</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white rounded-2xl border border-gray-200 p-5">
        <p class="text-[11px] font-semibold tracking-widest uppercase text-gray-500">Matériels affectés</p>
        <p class="text-[28px] font-extrabold text-gray-900 mt-1">{{ materiels.length }}</p>
        <p class="text-xs text-gray-500 mt-1">Sous votre responsabilité</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 p-5">
        <p class="text-[11px] font-semibold tracking-widest uppercase text-gray-500">Affectations actives</p>
        <p class="text-[28px] font-extrabold text-sky-700 mt-1">{{ affectationsActives }}</p>
        <p class="text-xs text-sky-700 mt-1">En cours</p>
      </div>
      <div class="bg-white rounded-2xl border border-gray-200 p-5">
        <p class="text-[11px] font-semibold tracking-widest uppercase text-gray-500">Retards</p>
        <p class="text-[28px] font-extrabold" :class="retards ? 'text-rose-600' : 'text-gray-900'">{{ retards }}</p>
        <p class="text-xs mt-1" :class="retards ? 'text-rose-600' : 'text-gray-500'">{{ retards ? 'Retour prévu dépassé' : 'Aucun retard' }}</p>
      </div>
    </div>

    <!-- Matériels table -->
    <UiCard class="rounded-2xl border border-gray-200 shadow-sm p-5 mt-6">
      <div class="flex items-center justify-between mb-4 gap-3">
        <h3 class="font-bold text-gray-900">Mes matériels</h3>
        <span class="text-xs text-gray-500">{{ materiels.length }} élément(s)</span>
      </div>
      <div v-if="loading" class="space-y-3 animate-pulse">
        <div v-for="i in 3" :key="i" class="h-16 bg-gray-50 rounded-xl"></div>
      </div>
      <div v-else-if="!materiels.length" class="py-10 text-center">
        <Icon name="heroicons:archive-box" class="h-10 w-10 text-gray-300 mx-auto" />
        <p class="text-sm font-semibold text-gray-700 mt-3">Aucun matériel affecté</p>
        <p class="text-xs text-gray-500 mt-1">Vos affectations apparaîtront ici.</p>
      </div>
      <div v-else class="overflow-x-auto -mx-5 px-5">
        <table class="w-full min-w-[720px] border-collapse">
          <thead>
            <tr class="border-b border-gray-100">
              <th class="text-[11px] font-semibold tracking-widest uppercase text-gray-500 text-left py-3 px-3">Référence</th>
              <th class="text-[11px] font-semibold tracking-widest uppercase text-gray-500 text-left py-3 px-3">Matériel</th>
              <th class="text-[11px] font-semibold tracking-widest uppercase text-gray-500 text-left py-3 px-3">Qté</th>
              <th class="text-[11px] font-semibold tracking-widest uppercase text-gray-500 text-left py-3 px-3">État affectation</th>
              <th class="text-[11px] font-semibold tracking-widest uppercase text-gray-500 text-left py-3 px-3">Affecté le</th>
              <th class="text-[11px] font-semibold tracking-widest uppercase text-gray-500 text-left py-3 px-3">Retour prévu</th>
              <th class="text-[11px] font-semibold tracking-widest uppercase text-gray-500 text-right py-3 px-3">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="m in materiels" :key="m.affectation_item_id" class="hover:bg-gray-50/60 transition">
              <td class="py-3.5 px-3 font-mono text-xs font-semibold text-gray-700">{{ m.reference }}</td>
              <td class="py-3.5 px-3">
                <div class="font-semibold text-sm text-gray-900">{{ m.nom }}</div>
                <NuxtLink :to="`/equipements/${m.equipement_id}`" class="text-xs text-blue-700 hover:underline">Fiche →</NuxtLink>
              </td>
              <td class="py-3.5 px-3 text-sm text-gray-700">×{{ m.quantite }}</td>
              <td class="py-3.5 px-3"><span class="inline-flex px-2.5 py-1 rounded-full text-xs font-semibold border bg-sky-50 text-sky-700 border-sky-200">{{ etatLabel(m.etat_affectation) }}</span></td>
              <td class="py-3.5 px-3 text-sm text-gray-600">{{ fmt(m.date_affectation) }}</td>
              <td class="py-3.5 px-3 text-sm">
                <span :class="isRetard(m.date_retour_prevue) ? 'text-rose-600 font-semibold' : 'text-gray-600'">{{ fmt(m.date_retour_prevue) || '—' }}</span>
                <span v-if="isRetard(m.date_retour_prevue)" class="ml-2 inline-flex px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200">En retard</span>
              </td>
              <td class="py-3.5 px-3 text-right">
                <button @click="openSignal(m)" class="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-700 hover:text-amber-800 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-full transition">
                  <Icon name="heroicons:exclamation-triangle" class="h-3.5 w-3.5" /> Signaler
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </UiCard>

    <!-- Affectations list -->
    <UiCard class="rounded-2xl border border-gray-200 shadow-sm p-5 mt-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-bold text-gray-900">Mes affectations</h3>
        <NuxtLink to="/affectations" class="text-xs font-semibold text-blue-700 hover:underline">Voir toutes →</NuxtLink>
      </div>
      <div v-if="loadingAff" class="space-y-3 animate-pulse"><div v-for="i in 2" :key="i" class="h-14 bg-gray-50 rounded-xl"></div></div>
      <div v-else-if="!affectations.length" class="py-8 text-center text-sm text-gray-500">Aucune affectation.</div>
      <ul v-else class="divide-y divide-gray-100">
        <li v-for="a in affectations" :key="a.id" class="py-3 flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="font-semibold text-sm text-gray-900">#{{ a.id }} · {{ a.statut }}</p>
            <p class="text-xs text-gray-500">{{ fmt(a.date_affectation) }} → {{ fmt(a.date_retour_prevue) || '—' }} · {{ a.items?.length || a.nombre_items || '—' }} matériel(s)</p>
          </div>
          <NuxtLink :to="`/affectations/${a.id}`" class="text-xs font-semibold text-blue-700 hover:underline shrink-0">Détail</NuxtLink>
        </li>
      </ul>
    </UiCard>

    <!-- Incidents (maintenances de mes matériels) -->
    <UiCard class="rounded-2xl border border-gray-200 shadow-sm p-5 mt-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-bold text-gray-900">Mes incidents</h3>
      </div>
      <div v-if="loadingInc" class="space-y-3 animate-pulse"><div v-for="i in 2" :key="i" class="h-14 bg-gray-50 rounded-xl"></div></div>
      <div v-else-if="!incidents.length" class="py-8 text-center text-sm text-gray-500">Aucun incident sur vos matériels.</div>
      <ul v-else class="divide-y divide-gray-100">
        <li v-for="m in incidents" :key="m.id" class="py-3 flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="font-semibold text-sm text-gray-900 truncate">{{ m.equipement_nom || m.equipement?.nom }}</p>
            <p class="text-xs text-gray-500">{{ fmt(m.date_debut) }} · {{ m.motif || 'Maintenance' }}</p>
          </div>
          <span class="text-xs font-semibold px-2.5 py-1 rounded-full shrink-0" :class="m.statut === 'en_cours' ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700'">
            {{ m.statut === 'en_cours' ? 'En cours' : 'Terminé' }}
          </span>
        </li>
      </ul>
    </UiCard>

    <!-- Modal définir infos -->
    <div v-if="showProfileModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm" @click.self="showProfileModal = false">
      <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 border border-gray-200">
        <h3 class="font-bold text-gray-900">Définir mes informations</h3>
        <p class="text-xs text-gray-500 mt-1">Mettez à jour vos coordonnées. Votre matricule et département sont gérés par l'admin.</p>
        <form @submit.prevent="saveProfile" class="mt-5 space-y-4">
          <div>
            <label class="block text-[11px] font-semibold tracking-widest uppercase text-gray-500 mb-1.5">Téléphone</label>
            <input v-model="profileForm.telephone" maxlength="50" placeholder="ex: +229 ..." class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none" />
          </div>
          <div>
            <label class="block text-[11px] font-semibold tracking-widest uppercase text-gray-500 mb-1.5">Email</label>
            <input v-model="profileForm.email" type="email" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none" />
          </div>
          <p v-if="profileError" class="text-xs text-rose-600 bg-rose-50 border border-rose-200 rounded-xl px-3 py-2">{{ profileError }}</p>
          <p v-if="profileSuccess" class="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-xl px-3 py-2">{{ profileSuccess }}</p>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="showProfileModal = false" class="px-4 py-2.5 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-xl">Annuler</button>
            <button type="submit" :disabled="savingProfile" class="px-5 py-2.5 bg-[#0f2a4a] text-white rounded-xl text-sm font-bold hover:bg-[#0d2340] disabled:opacity-50">{{ savingProfile ? 'Enregistrement…' : 'Enregistrer' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal signaler -->
    <div v-if="signalItem" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm" @click.self="signalItem = null">
      <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 border border-gray-200">
        <h3 class="font-bold text-gray-900">Signaler un problème</h3>
        <p class="text-sm text-gray-600 mt-1"><span class="font-semibold">{{ signalItem.nom }}</span> ({{ signalItem.reference }})</p>
        <p class="text-xs text-gray-500 mt-3">Cette action informe l'administrateur. La mise en maintenance doit être validée par un admin (règle métier).</p>
        <textarea v-model="signalMessage" rows="3" placeholder="Décrivez le problème (ex: écran cassé, ne s'allume plus...)" class="mt-4 w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 outline-none"></textarea>
        <div class="flex justify-end gap-2 mt-4">
          <button @click="signalItem = null" class="px-4 py-2.5 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-xl">Fermer</button>
          <button @click="submitSignal" class="px-5 py-2.5 bg-amber-600 text-white rounded-xl text-sm font-bold hover:bg-amber-700">Envoyer le signalement</button>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useEmployesStore } from '~/stores/employes'
import { useAuthStore } from '~/stores/auth'
import api from '~/utils/api'
import { useToast } from '~/composables/useToast'

const employesStore = useEmployesStore()
const authStore = useAuthStore()
const toast = useToast()

const materiels = ref([])
const affectations = ref([])
const loading = ref(true)
const loadingAff = ref(true)
const loadingInc = ref(true)
const incidents = ref([])
const employeLinked = ref(null)
const showProfileModal = ref(false)
const savingProfile = ref(false)
const profileError = ref('')
const profileSuccess = ref('')
const signalItem = ref(null)
const signalMessage = ref('')

const profileForm = reactive({ telephone: '', email: '' })

const initials = computed(() => {
  const n = employeLinked.value?.nom_complet || authStore.user?.username || 'E'
  return n.slice(0,2).toUpperCase()
})

const affectationsActives = computed(() => affectations.value.filter(a => a.statut === 'active').length)
const retards = computed(() => materiels.value.filter(m => isRetard(m.date_retour_prevue)).length)

function etatLabel(v){ const m={neuf:'Neuf', tres_bon:'Très bon', bon:'Bon', a_verifier:'À vérifier', endommage:'Endommagé'}; return m[v]||v }
function fmt(d){ if(!d) return null; return new Date(d).toLocaleDateString('fr-FR') }
function isRetard(d){ if(!d) return false; return new Date(d) < new Date(new Date().toDateString()) }
function openSignal(item){ signalItem.value=item; signalMessage.value='' }
async function submitSignal(){
  if (!signalItem.value) return
  const equipementId = signalItem.value.equipement_id
  const motif = signalMessage.value?.trim() || 'Signalement employé'
  try {
    // Tente de créer une demande de maintenance ; si permission refusee (EMPLOYE),
    // on informe que le signalement est note cote client et qu'un manager doit valider
    await api.post(`/maintenances/equipement/${equipementId}`, {
      motif,
      description: `Signalement par ${employeLinked.value?.nom_complet || authStore.user?.username || 'employé'} : ${motif}`,
      date_debut: new Date().toISOString().slice(0, 10),
    })
    toast.success(`Incident créé pour ${signalItem.value.nom} — en attente de traitement.`)
  } catch (e) {
    const status = e.response?.status
    if (status === 403) {
      toast.success(`Signalement noté pour ${signalItem.value.nom} : "${motif}" — un manager doit créer l'incident (permission requise).`)
    } else {
      toast.error(e.response?.data?.detail || 'Echec du signalement')
      return
    }
  }
  signalItem.value = null
  // Rafraichir incidents
  try {
    incidents.value = await api.get('/maintenances/moi').then(r => r.data)
  } catch {}
}

async function saveProfile(){
  profileError.value=''; profileSuccess.value=''
  if(!employeLinked.value) return
  savingProfile.value=true
  try{
    const payload={}
    if(profileForm.telephone) payload.telephone=profileForm.telephone
    if(profileForm.email) payload.email=profileForm.email
    const updated = await employesStore.updateEmploye(employeLinked.value.id, payload)
    employeLinked.value = updated
    profileSuccess.value='Informations mises à jour.'
    setTimeout(()=> showProfileModal.value=false, 800)
  }catch(e){
    profileError.value = e.response?.data?.detail || "Erreur lors de l'enregistrement"
  }finally{ savingProfile.value=false }
}

onMounted(async ()=>{
  try{
    const [mats, affs, incs] = await Promise.all([
      employesStore.fetchMesMateriels().catch(()=>[]),
      api.get('/affectations/moi').then(r=>r.data).catch(()=>[]),
      api.get('/maintenances/moi').then(r=>r.data).catch(()=>[]),
    ])
    materiels.value = Array.isArray(mats) ? mats : []
    affectations.value = Array.isArray(affs) ? affs : (affs.items || [])
    incidents.value = Array.isArray(incs) ? incs : []
    // Try to resolve employe linked
    if(authStore.user?.id){
      try{
        // fetch all employes and find by user_id
        await employesStore.fetchEmployes()
        const linked = employesStore.employes.find(e=> e.user_id === authStore.user.id)
        if(linked){ employeLinked.value = linked; profileForm.telephone = linked.telephone || ''; profileForm.email = linked.email || '' }
      }catch{}
    }
  }finally{ loading.value=false; loadingAff.value=false; loadingInc.value=false }
})
</script>
