<template>
  <div class="min-h-screen flex bg-gray-50 text-gray-900 font-sans">
    <!-- Overlay mobile -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-30 bg-black/40 lg:hidden"
      @click="sidebarOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed z-40 inset-y-0 left-0 w-64 bg-blue-900 text-white flex flex-col transform transition-transform duration-200 lg:static lg:translate-x-0 flex-shrink-0',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div class="p-8">
        <h1 class="text-2xl font-bold tracking-tight">BeStock</h1>
      </div>

      <nav class="flex-1 overflow-y-auto">
        <NuxtLink
          to="/"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': route.path === '/' }"
          @click="sidebarOpen = false"
        >
          <Icon name="heroicons:home" class="h-5 w-5" /> Accueil
        </NuxtLink>
        <NuxtLink
          to="/dashboard"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': isActive('/dashboard') }"
          @click="sidebarOpen = false"
        >
          <Icon name="heroicons:chart-bar" class="h-5 w-5" /> Dashboard
        </NuxtLink>
        <NuxtLink
          to="/categories"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': isActive('/categories') }"
          @click="sidebarOpen = false"
        >
          <Icon name="heroicons:folder" class="h-5 w-5" /> Catégories
        </NuxtLink>
        <NuxtLink
          to="/materiel/nouveau"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': isActive('/materiel') }"
          @click="sidebarOpen = false"
        >
          <Icon name="heroicons:plus" class="h-5 w-5" /> Ajouter un matériel
        </NuxtLink>
        <NuxtLink
          to="/historique"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': isActive('/historique') }"
          @click="sidebarOpen = false"
        >
          <Icon name="heroicons:clock" class="h-5 w-5" /> Historique
        </NuxtLink>
        <NuxtLink
          v-if="isSuperAdmin"
          to="/users"
          class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4"
          :class="{ 'bg-blue-800': isActive('/users') }"
          @click="sidebarOpen = false"
        >
          <Icon name="heroicons:users" class="h-5 w-5" /> Utilisateurs
        </NuxtLink>
      </nav>

      <button
        @click="logout"
        class="flex items-center py-4 px-8 text-blue-100 hover:bg-blue-800 transition-colors gap-4 border-t border-blue-800 flex-shrink-0"
      >
        <Icon name="heroicons:arrow-right-on-rectangle" class="h-5 w-5" /> Déconnexion
      </button>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0">
      <header class="bg-white border-b border-gray-200 h-20 flex items-center justify-between px-4 sm:px-6 lg:px-10 gap-4">
        <div class="flex items-center gap-2 text-sm text-gray-500 min-w-0">
          <button
            @click="sidebarOpen = !sidebarOpen"
            class="lg:hidden p-2 -ml-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
            aria-label="Ouvrir le menu"
          >
            <Icon name="heroicons:bars-3" class="h-6 w-6" />
          </button>
          <span class="font-medium text-gray-800 truncate">BeStock</span>
        </div>
        <div class="flex items-center gap-4">
          <NuxtLink to="/compte" class="flex items-center gap-2 border border-gray-300 rounded-lg px-3 sm:px-4 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-100 transition">
            <Icon name="heroicons:user-circle" class="h-5 w-5 flex-shrink-0" />
            <span class="hidden sm:inline">{{ displayName }}</span>
          </NuxtLink>
        </div>
      </header>

      <main class="flex-1 p-4 sm:p-6 lg:p-10">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '~/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const sidebarOpen = ref(false);

watch(() => route.fullPath, () => {
  sidebarOpen.value = false;
});

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