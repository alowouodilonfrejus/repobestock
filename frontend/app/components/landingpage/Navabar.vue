<template>
  <nav class="sticky top-0 z-[1000] bg-white/95 backdrop-blur-md border-b-2 border-slate-200 py-3.5 px-5">
    <div class="max-w-[1200px] mx-auto flex items-center justify-between gap-3">

      <NuxtLink to="/" class="text-2xl font-extrabold text-[#23418e] no-underline flex-shrink-0">
        <span class="text-[#f77b07]">Be</span>Stock
      </NuxtLink>

      <div class="hidden md:flex gap-6">
        <NuxtLink 
          to="#accueil" 
          class="no-underline text-slate-700 font-semibold hover:text-[#f77b07] transition-colors duration-200"
        >
          Accueil
        </NuxtLink>
        <NuxtLink 
          to="#objectifs" 
          class="no-underline text-slate-700 font-semibold hover:text-[#f77b07] transition-colors duration-200"
        >
          Objectifs
        </NuxtLink>
        <NuxtLink 
          to="#fonctionnalites" 
          class="no-underline text-slate-700 font-semibold hover:text-[#f77b07] transition-colors duration-200"
        >
          Fonctionnalités
        </NuxtLink>
        <NuxtLink 
          to="#equipe" 
          class="no-underline text-slate-700 font-semibold hover:text-[#f77b07] transition-colors duration-200"
        >
          Équipe
        </NuxtLink>
      </div>

      <div class="flex items-center gap-2 sm:gap-3 min-w-0">
        <div v-if="authStore.isAuthenticated" class="flex items-center gap-2 sm:gap-3">
          <div class="hidden sm:flex items-center gap-2 text-sm text-slate-600">
            <span class="w-8 h-8 rounded-full bg-[#23418e] text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
              {{ initials }}
            </span>
            <span class="font-semibold text-slate-800 truncate max-w-[120px]">{{ displayName }}</span>
          </div>

          <NuxtLink 
            to="/dashboard" 
            class="no-underline border-2 border-[#23418e] text-[#23418e] hover:bg-[#23418e] hover:text-white py-1.5 px-3 sm:px-4 rounded-md font-semibold transition-colors duration-200 text-sm"
          >
            Tableau de bord
          </NuxtLink>

          <button 
            @click="handleLogout"
            class="no-underline border-2 border-red-500 text-red-500 hover:bg-red-500 hover:text-white py-1.5 px-3 sm:px-4 rounded-md font-semibold transition-colors duration-200 text-sm cursor-pointer"
          >
            Déconnexion
          </button>
        </div>

        <div v-else class="flex items-center gap-2 sm:gap-3">
          <NuxtLink 
            to="/connexion" 
            class="no-underline border-2 border-[#23418e] text-[#23418e] hover:bg-[#23418e] hover:text-white py-1.5 px-3 sm:px-4 rounded-md font-semibold transition-colors duration-200 text-sm"
          >
            Connexion
          </NuxtLink>

          <NuxtLink 
            to="/inscription" 
            class="no-underline bg-[#f77b07] hover:bg-[#23418e] text-white py-2 px-3 sm:px-4 rounded-md font-semibold transition-colors duration-200 text-sm shadow-md hover:shadow-none"
          >
            Inscription
          </NuxtLink>
        </div>

        <button
          @click="menuOpen = !menuOpen"
          class="md:hidden p-2 -mr-1 text-slate-700 hover:text-[#f77b07] transition-colors cursor-pointer"
          :aria-label="menuOpen ? 'Fermer le menu' : 'Ouvrir le menu'"
          :aria-expanded="menuOpen"
        >
          <Icon v-if="!menuOpen" name="heroicons:bars-3" class="h-6 w-6" />
          <Icon v-else name="heroicons:x-mark" class="h-6 w-6" />
        </button>
      </div>

    </div>

    <div
      v-if="menuOpen"
      class="md:hidden max-w-[1200px] mx-auto flex flex-col gap-1 pt-4 pb-2"
    >
      <NuxtLink 
        to="#accueil" 
        class="no-underline text-slate-700 font-semibold hover:text-[#f77b07] transition-colors duration-200 py-2 px-2 rounded-md hover:bg-slate-50"
        @click="menuOpen = false"
      >
        Accueil
      </NuxtLink>
      <NuxtLink 
        to="#objectifs" 
        class="no-underline text-slate-700 font-semibold hover:text-[#f77b07] transition-colors duration-200 py-2 px-2 rounded-md hover:bg-slate-50"
        @click="menuOpen = false"
      >
        Objectifs
      </NuxtLink>
      <NuxtLink 
        to="#fonctionnalites" 
        class="no-underline text-slate-700 font-semibold hover:text-[#f77b07] transition-colors duration-200 py-2 px-2 rounded-md hover:bg-slate-50"
        @click="menuOpen = false"
      >
        Fonctionnalités
      </NuxtLink>
      <NuxtLink 
        to="#equipe" 
        class="no-underline text-slate-700 font-semibold hover:text-[#f77b07] transition-colors duration-200 py-2 px-2 rounded-md hover:bg-slate-50"
        @click="menuOpen = false"
      >
        Équipe
      </NuxtLink>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const menuOpen = ref(false)

const displayName = computed(() => {
  const user = authStore.user
  if (!user) return 'Compte'
  return user.username || user.email || 'Compte'
})

const initials = computed(() => {
  const user = authStore.user
  const name = user?.username || user?.email || 'C'
  return name.split(/[.\s@]/).filter(Boolean).slice(0, 2).map((p) => p[0]).join('').toUpperCase()
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/')
}
</script>