<template>
  <NuxtLayout name="dashboard">
    <!-- En-tête identique Dashboard -->
    <header class="flex items-center justify-between mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Collaborateurs</h1>
      <button
        v-if="can('employes:write')"
        @click="openCreate"
        class="px-6 py-2.5 bg-blue-900 text-white rounded-xl text-sm font-semibold hover:bg-blue-800 transition shadow-sm"
      >
        + Nouvel collaborateur
      </button>
    </header>
    <p class="text-gray-500 -mt-4 mb-8">Gérez les fiches collaborateurs et leurs matériels attribués.</p>

    <!-- Indicateurs -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <SummaryCard title="EMPLOYÉS ENREGISTRÉS" :value="employesStore.employes.length" subtext="Actifs et inactifs" icon="heroicons:user-group" />
      <SummaryCard title="EMPLOYÉS ACTIFS" :value="actifsCount" subtext="Peuvent recevoir du matériel" icon="heroicons:check-circle" />
      <SummaryCard title="EMPLOYÉS INACTIFS" :value="inactifsCount" subtext="Suspendus" icon="heroicons:no-symbol" />
    </div>

    <!-- Liste -->
    <div class="bg-white p-4 sm:p-6 rounded-xl shadow-md border border-gray-100 mt-8">
      <div class="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
        <table class="w-full border-collapse min-w-[640px]">
          <thead>
            <tr>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Collaborateur</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Matricule</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide hidden md:table-cell">Département</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide hidden md:table-cell">Fonction</th>
              <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">Statut</th>
              <th class="text-xs text-gray-500 text-right p-4 uppercase tracking-wide">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="employe in employesStore.employes" :key="employe.id" class="border-t border-gray-100 hover:bg-gray-50">
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-full bg-blue-900 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {{ employe.nom_complet.split(' ').map(w=>w[0]).slice(0,2).join('').toUpperCase() }}
                  </div>
                  <div>
                    <p class="font-semibold text-gray-900 text-sm">{{ employe.nom_complet }}</p>
                    <p v-if="employe.email" class="text-gray-400 text-xs">{{ employe.email }}</p>
                  </div>
                </div>
              </td>
              <td class="p-4 font-mono text-xs font-semibold text-gray-700">{{ employe.matricule }}</td>
              <td class="p-4 text-sm text-gray-600 hidden md:table-cell">{{ employe.departement || '—' }}</td>
              <td class="p-4 text-sm text-gray-600 hidden md:table-cell">{{ employe.fonction || '—' }}</td>
              <td class="p-4">
                <span class="px-3 py-1 rounded-full text-xs font-medium" :class="employe.actif ? 'bg-teal-50 text-teal-700' : 'bg-gray-100 text-gray-500'">
                  {{ employe.actif ? 'Actif' : 'Inactif' }}
                </span>
              </td>
              <td class="p-4 text-right whitespace-nowrap">
                <NuxtLink :to="`/employes/${employe.id}`" class="text-blue-600 hover:text-blue-500 text-sm font-medium mr-3">Fiche</NuxtLink>
                <button v-if="can('employes:write')" @click="openEdit(employe)" class="text-gray-600 hover:text-gray-900 text-sm font-medium">Modifier</button>
              </td>
            </tr>
            <tr v-if="!employesStore.loading && employesStore.employes.length === 0">
              <td colspan="6" class="p-12 text-center text-sm text-gray-400">Aucun collaborateur enregistré.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal création / modification -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40" @click.self="showModal = false">
      <div class="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 border border-gray-100">
        <h3 class="text-lg font-semibold text-gray-900 mb-5">{{ editMode ? 'Modifier' : 'Nouvel' }} collaborateur</h3>
        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Nom complet *</label>
            <input v-model="form.nom_complet" required maxlength="150" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-blue-900 focus:border-blue-900 outline-none" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Matricule *</label>
              <input v-model="form.matricule" required maxlength="50" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-blue-900 outline-none font-mono" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Date d'arrivée</label>
              <input v-model="form.date_arrivee" type="date" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-blue-900 outline-none" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Département</label>
              <input v-model="form.departement" maxlength="100" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-blue-900 outline-none" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Fonction</label>
              <input v-model="form.fonction" maxlength="100" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-blue-900 outline-none" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Téléphone</label>
              <input v-model="form.telephone" maxlength="50" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-blue-900 outline-none" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Email</label>
              <input v-model="form.email" type="email" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-blue-900 outline-none" />
            </div>
          </div>
          <label v-if="editMode" class="flex items-center gap-2 text-sm font-medium text-gray-700 pt-1">
            <input v-model="form.actif" type="checkbox" class="rounded border-gray-300 text-blue-900 focus:ring-blue-900" />
            Collaborateur actif (peut recevoir du matériel)
          </label>

          <!-- Création de compte de connexion (collaborateur) -->
          <div v-if="!editMode" class="border border-blue-100 bg-blue-50/50 rounded-xl p-4 space-y-3">
            <label class="flex items-center gap-2 text-sm font-semibold text-blue-900">
              <input v-model="createAccount" type="checkbox" class="rounded border-blue-300 text-blue-900 focus:ring-blue-900" />
              Créer un compte de connexion pour cet collaborateur
            </label>
            <p class="text-xs text-blue-700/80">L'collaborateur pourra se connecter sur <span class="font-mono">/connexion</span> avec son email et accéder à <span class="font-semibold">Mon matériel</span>.</p>
            <div v-if="createAccount" class="space-y-3 pt-2">
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Nom d'utilisateur</label>
                <input v-model="accountForm.username" placeholder="ex: j.dupont" maxlength="50" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-blue-900 outline-none" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Mot de passe *</label>
                <input v-model="accountForm.password" type="password" placeholder="min. 8 caractères" class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-blue-900 outline-none" />
              </div>
              <p class="text-xs text-gray-500">Rôle : <span class="font-semibold text-gray-700">Collaborateur (manager)</span> — accès limité à Mon matériel.</p>
            </div>
          </div>
          <div v-else-if="employeHasNoAccount" class="border border-amber-100 bg-amber-50/50 rounded-xl p-4">
            <p class="text-xs font-semibold text-amber-800">Cet collaborateur n'a pas de compte.</p>
            <button type="button" @click="openCreateAccount" class="mt-2 text-xs font-semibold text-amber-700 hover:underline">→ Créer son compte maintenant</button>
          </div>

          <p v-if="errorMessage" class="text-red-600 text-sm bg-red-50 border border-red-100 rounded-xl px-3.5 py-2.5">{{ errorMessage }}</p>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="showModal = false" class="px-4 py-2.5 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-xl transition">Annuler</button>
            <button type="submit" :disabled="saving" class="px-6 py-2.5 bg-blue-900 text-white rounded-xl text-sm font-semibold hover:bg-blue-800 transition shadow-sm disabled:opacity-50">
              {{ saving ? 'Enregistrement…' : 'Enregistrer' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useEmployesStore } from '~/stores/employes'
import { useToast } from '~/composables/useToast'
import SummaryCard from '~/components/dashboard/SummaryCard.vue'

const employesStore = useEmployesStore()
const { can } = useRole()
const toast = useToast()

const showModal = ref(false)
const editMode = ref(false)
const editingId = ref(null)
const saving = ref(false)
const errorMessage = ref('')
const createAccount = ref(false)
const accountForm = reactive({ username: '', password: '' })
const editingEmploye = ref(null)

const actifsCount = computed(() => employesStore.employes.filter(e => e.actif).length)
const inactifsCount = computed(() => employesStore.employes.filter(e => !e.actif).length)
const employeHasNoAccount = computed(() => editMode.value && editingEmploye.value && !editingEmploye.value.user_id)

const emptyForm = {
  nom_complet: '', matricule: '', departement: '', fonction: '',
  telephone: '', email: '', date_arrivee: null, actif: true,
}
const form = reactive({ ...emptyForm })

onMounted(() => employesStore.fetchEmployes(true))

function openCreate() {
  Object.assign(form, emptyForm)
  createAccount.value = false
  accountForm.username = ''
  accountForm.password = ''
  editMode.value = false
  editingId.value = null
  editingEmploye.value = null
  errorMessage.value = ''
  showModal.value = true
}

function openEdit(employe) {
  Object.assign(form, {
    nom_complet: employe.nom_complet,
    matricule: employe.matricule,
    departement: employe.departement || '',
    fonction: employe.fonction || '',
    telephone: employe.telephone || '',
    email: employe.email || '',
    date_arrivee: employe.date_arrivee,
    actif: employe.actif,
  })
  editMode.value = true
  editingId.value = employe.id
  editingEmploye.value = employe
  errorMessage.value = ''
  showModal.value = true
}

function openCreateAccount() {
  // Pré-remplit depuis la fiche collaborateur et repasse en mode création avec compte
  const emp = editingEmploye.value
  if (!emp) return
  showModal.value = false
  setTimeout(() => {
    Object.assign(form, {
      nom_complet: emp.nom_complet,
      matricule: emp.matricule + '-compte',
      departement: emp.departement || '',
      fonction: emp.fonction || '',
      telephone: emp.telephone || '',
      email: emp.email || '',
      date_arrivee: emp.date_arrivee,
      actif: true,
    })
    // On informe l'admin qu'il faut recréer via avec-compte
    toast.success('Renseignez un nouvel collaborateur lié ou utilisez la mise à jour avec compte (à venir).')
  }, 100)
}

async function submit() {
  saving.value = true
  errorMessage.value = ''
  try {
    const payload = { ...form }
    if (!payload.email) delete payload.email
    if (!payload.date_arrivee) delete payload.date_arrivee
    if (editMode.value) {
      await employesStore.updateEmploye(editingId.value, payload)
      toast.success('Collaborateur modifié')
    } else {
      if (createAccount.value) {
        if (!payload.email) throw new Error('Email requis pour créer le compte')
        if (!accountForm.password || accountForm.password.length < 8) throw new Error('Mot de passe ≥ 8 caractères requis')
        const withAccount = {
          ...payload,
          username: accountForm.username || undefined,
          password: accountForm.password,
          role: 'manager',
        }
        await employesStore.createEmployeAvecCompte(withAccount)
        toast.success('Collaborateur et compte créés — il peut se connecter sur /connexion')
      } else {
        await employesStore.createEmploye(payload)
        toast.success('Collaborateur créé')
      }
    }
    showModal.value = false
  } catch (err) {
    const detail = err.response?.data?.detail
    if (Array.isArray(detail)) {
      errorMessage.value = detail
        .map((e) => `${(e.loc || []).slice(-1)[0] ?? 'champ'} : ${e.msg}`)
        .join(' · ')
    } else {
      errorMessage.value = detail || err.message || 'Erreur lors de l\'enregistrement'
    }
  } finally {
    saving.value = false
  }
}
</script>
