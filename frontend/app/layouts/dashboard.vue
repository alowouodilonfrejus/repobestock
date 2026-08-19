<template>
  <div class="min-h-screen flex bg-gray-50 text-gray-900 font-sans">
    <!-- Sidebar -->
    <aside class="w-64 bg-blue-900 text-white flex-shrink-0 flex flex-col">
      <div class="p-8">
        <h1 class="text-2xl font-bold tracking-tight">BeStock</h1>
      </div>

      <nav class="flex-1">
        <NuxtLink
          to="/"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': route.path === '/' }"
        >
          <Icon name="heroicons:home" class="h-5 w-5" /> Accueil
        </NuxtLink>
        <NuxtLink
          to="/dashboard"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': isActive('/dashboard') }"
        >
          <Icon name="heroicons:chart-bar" class="h-5 w-5" /> Dashboard
        </NuxtLink>
        <NuxtLink
          to="/categories"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': isActive('/categories') }"
        >
          <Icon name="heroicons:folder" class="h-5 w-5" /> Catégories
        </NuxtLink>
        <NuxtLink
          to="/materiel/nouveau"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': isActive('/materiel') }"
        >
          <Icon name="heroicons:plus" class="h-5 w-5" /> Ajouter un matériel
        </NuxtLink>
        <NuxtLink
          to="/historique"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': isActive('/historique') }"
        >
          <Icon name="heroicons:clock" class="h-5 w-5" /> Historique
        </NuxtLink>
        <NuxtLink
          v-if="isSuperAdmin"
          to="/users"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': isActive('/users') }"
        >
          <Icon name="heroicons:users" class="h-5 w-5" /> Utilisateurs
        </NuxtLink>
      </nav>

      <button
        @click="logout"
        class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4 border-t border-blue-800"
      >
        <Icon name="heroicons:arrow-right-on-rectangle" class="h-5 w-5" /> Déconnexion
      </button>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col">
      <header class="bg-white border-b border-gray-200 h-20 flex items-center justify-between px-10">
        <div class="flex items-center gap-2 text-sm text-gray-500">
          <span class="font-medium text-gray-800">BeStock</span>
        </div>
        <div class="flex items-center gap-4">
          <NuxtLink to="/compte" class="flex items-center gap-2 border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-100 transition">
            <Icon name="heroicons:user-circle" class="h-5 w-5" /> {{ displayName }}
          </NuxtLink>
        </div>
      </header>

      <main class="flex-1 p-10">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '~/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const isActive = (path) => route.path.startsWith(path);

const displayName = computed(() => {
  const user = authStore.user;
  if (!user) return 'Compte Admin';
  return user.username || user.email || 'Compte Admin';
});

const isSuperAdmin = computed(() => authStore.user?.role === 'superadmin');

const logout = async () => {
  await authStore.logout();
  router.push('/connexion');
};
</script>