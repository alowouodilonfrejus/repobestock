<template>
  <NuxtLayout name="dashboard">
    <div class="max-w-2xl mx-auto">
      <div class="mb-10">
        <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Compte Admin</h2>
        <p class="text-gray-500 mt-2 text-lg">Informations du compte administrateur.</p>
      </div>

      <UiCard title="Profil" class="shadow-sm border border-gray-200">
        <div v-if="authStore.user" class="space-y-4">
          <div class="flex items-center gap-4 pb-6 border-b border-gray-100">
            <div class="w-16 h-16 rounded-full bg-blue-900 text-white flex items-center justify-center text-2xl">
              {{ initials }}
            </div>
            <div>
              <p class="text-xl font-bold text-gray-900">{{ displayName }}</p>
              <p class="text-sm text-gray-500">{{ authStore.user.email }}</p>
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-gray-500">Rôle</p>
              <p class="font-semibold text-gray-800">Administrateur</p>
            </div>
            <div>
              <p class="text-gray-500">Statut</p>
              <p class="font-semibold text-green-600">Connecté</p>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8">
          <p class="text-gray-500 mb-4">Aucune session active.</p>
          <NuxtLink to="/connexion" class="bg-blue-900 hover:bg-blue-800 text-white px-6 py-2.5 rounded-lg text-sm font-semibold transition-all">
            Se connecter
          </NuxtLink>
        </div>
      </UiCard>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from '~/stores/auth';

const authStore = useAuthStore();

onMounted(() => {
  if (authStore.isAuthenticated) {
    authStore.fetchMe().catch(() => {});
  }
});

const displayName = computed(() => {
  const u = authStore.user;
  if (!u) return 'Non connecté';
  return u.username || u.email || 'Administrateur';
});

const initials = computed(() => {
  const u = authStore.user;
  if (!u) return 'A';
  const name = u.username || u.email || 'Admin';
  return name.split(' ').map((p) => p[0]).slice(0, 2).join('').toUpperCase();
});
</script>