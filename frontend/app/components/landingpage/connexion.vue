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
            {{ isSignUp ? 'Créer un compte Admin' : 'Espace Admin' }}
          </h2>
          <p class="text-slate-500 text-sm mt-1.5">
            {{ isSignUp ? 'Remplissez les informations ci-dessous' : 'Veuillez saisir vos identifiants' }}
          </p>
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
            <label class="block text-sm font-semibold text-slate-700 mb-2">Rôle demandé</label>
            <div class="grid grid-cols-2 gap-3">
              <button
                type="button"
                @click="form.role = 'admin'"
                class="px-4 py-3 rounded-xl border text-sm font-semibold transition-all"
                :class="form.role === 'admin' ? 'bg-blue-900 text-white border-blue-900 shadow-md' : 'border-slate-200 text-slate-600 hover:border-blue-300'"
              >
                Admin
              </button>
              <button
                type="button"
                @click="form.role = 'manager'"
                class="px-4 py-3 rounded-xl border text-sm font-semibold transition-all"
                :class="form.role === 'manager' ? 'bg-blue-900 text-white border-blue-900 shadow-md' : 'border-slate-200 text-slate-600 hover:border-blue-300'"
              >
                Manager
              </button>
            </div>
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
import { useRouter } from 'vue-router'
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
  role: 'manager'
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
      await authStore.register({
        email: form.email,
        username: form.fullName,
        password: form.password,
        role: form.role
      })
      errorMessage.value = 'Compte créé avec succès. Il sera actif après validation par le super admin.'
      return
    } else {
      await authStore.login(form.email, form.password)
    }
    router.push('/dashboard')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Une erreur est survenue. Veuillez réessayer.'
  } finally {
    isSubmitting.value = false
  }
}
</script>