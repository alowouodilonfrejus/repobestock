<template>
  <div class="min-h-screen bg-slate-50 flex flex-col justify-between p-6 md:p-10 font-sans">
    
    <header class="w-full max-w-7xl mx-auto flex flex-col items-center sm:items-start">
      <h1 class="text-3xl md:text-4xl font-black tracking-tight text-blue-900">
        BESTOCK
      </h1>
      <p class="text-xs font-semibold text-orange-600 uppercase tracking-widest mt-1">
        Plateforme de gestion de matériaux
      </p>
    </header>

    <main class="w-full max-w-md mx-auto my-auto py-8">
      <div class="bg-white rounded-2xl border border-slate-200/80 p-8 sm:p-10 shadow-xl shadow-blue-950/5">
        
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-blue-950">
            {{ isSignUp ? 'Créer un compte' : 'Espace BeStock' }}
          </h2>
          <p class="text-slate-500 text-sm mt-1.5">
            {{ isSignUp ? 'Collaborateurs et administrateurs — remplissez les informations' : 'Collaborateurs et administrateurs — saisissez vos identifiants' }}
          </p>
          <p v-if="!isSignUp" class="text-xs text-slate-400 mt-2">Les collaborateurs se connectent avec l'email fourni par l'admin et accèdent à <span class="font-semibold text-slate-600">Mon matériel</span>.</p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-5">

          <div v-if="errorMessage" class="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
            {{ errorMessage }}
          </div>

          <div v-if="isSignUp">
            <label class="block text-sm font-semibold text-slate-700 mb-2">Nom complet</label>
            <input 
              v-model="form.fullName" 
              type="text" 
              required 
              placeholder="Nom" 
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all text-slate-800 text-sm bg-slate-50/50"
            />
          </div>

          <div v-if="isSignUp">
            <label class="block text-sm font-semibold text-slate-700 mb-2">Fonction (optionnel)</label>
            <input
              v-model="form.fonction"
              type="text"
              placeholder="ex: Technicien, Magasinier…"
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all text-slate-800 text-sm bg-slate-50/50"
            />
            <p class="text-xs text-slate-400 mt-2">Votre compte sera activé après validation par un administrateur, qui définira votre rôle.</p>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-2">Adresse Email</label>
            <input 
              v-model="form.email" 
              type="email" 
              required 
              placeholder="email" 
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all text-slate-800 text-sm bg-slate-50/50"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-2">Mot de passe</label>
            <input 
              v-model="form.password" 
              type="password" 
              required 
              placeholder="••••••••" 
              class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all text-slate-800 text-sm bg-slate-50/50"
            />
          </div>

          <button 
            type="submit" 
            :disabled="isSubmitting"
            class="w-full py-3.5 px-4 bg-orange-500 hover:bg-orange-600 active:bg-orange-700 text-white font-semibold rounded-xl shadow-lg shadow-orange-500/20 transition-all transform active:scale-[0.99] flex items-center justify-center text-sm mt-2 disabled:opacity-60"
          >
            {{ isSubmitting ? 'Patientez...' : (isSignUp ? "S'inscrire" : "Se connecter") }}
          </button>
        </form>

        <div class="text-center pt-6 mt-6 border-t border-slate-100">
          <p class="text-sm text-slate-600">
            {{ isSignUp ? 'Vous avez déjà un compte ?' : "Vous n'avez pas de compte ?" }}
            <button 
              @click="isSignUp = !isSignUp" 
              type="button" 
              class="text-blue-900 font-bold hover:text-orange-600 transition-colors ml-1 focus:outline-none"
            >
              {{ isSignUp ? 'Se connecter' : "S'inscrire" }}
            </button>
          </p>
        </div>

      </div>
    </main>

    <footer class="w-full text-center text-xs text-slate-400 py-4">
      © {{ new Date().getFullYear() }} <span class="font-bold text-blue-900">BESTOCK</span>. Tous droits réservés.
    </footer>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'

const props = defineProps({
  defaultMode: {
    type: String,
    default: 'login'
  }
})

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const isSignUp = ref(props.defaultMode === 'signup')
const isSubmitting = ref(false)
const errorMessage = ref('')

onMounted(() => {
  if (route.query.mode === 'signup') {
    isSignUp.value = true
  } else if (route.query.mode === 'login') {
    isSignUp.value = false
  }
})

const form = reactive({
  fullName: '',
  email: '',
  password: '',
  fonction: ''
})

const errors = reactive({
  fullName: '',
  email: '',
  password: ''
})

const clearErrors = () => {
  errors.fullName = ''
  errors.email = ''
  errors.password = ''
  errorMessage.value = ''
}

const toggleMode = () => {
  isSignUp.value = !isSignUp.value
  clearErrors()
}

const handleSubmit = async () => {
  clearErrors()
  let hasError = false

  if (isSignUp.value && !form.fullName.trim()) {
    errors.fullName = 'Veuillez renseigner votre nom complet.'
    hasError = true
  }

  if (!form.email.trim()) {
    errors.email = 'Veuillez renseigner votre adresse email.'
    hasError = true
  }

  if (!form.password.trim()) {
    errors.password = 'Veuillez renseigner votre mot de passe.'
    hasError = true
  }

  if (hasError) return

  isSubmitting.value = true
  try {
    if (isSignUp.value) {
      await authStore.registerEmploye({
        nom_complet: form.fullName,
        email: form.email,
        password: form.password,
        fonction: form.fonction || undefined
      })
      errorMessage.value = 'Inscription enregistrée. Votre compte sera actif après validation par un administrateur.'
      return
    } else {
      await authStore.login(form.email, form.password)
      const user = authStore.user
      // Collaborateurs (manager) → Mon matériel, Admins → Dashboard
      if (['manager', 'employe'].includes(user?.role)) {
        router.push('/mes-materiels')
      } else {
        router.push('/dashboard')
      }
      return
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Une erreur est survenue. Veuillez réessayer.'
  } finally {
    isSubmitting.value = false
  }
}
</script>