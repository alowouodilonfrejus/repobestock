<template>
  <div class="min-h-screen flex bg-[#f8fafc] text-gray-900 font-sans">
    <!-- Overlay mobile -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-30 bg-slate-900/40 backdrop-blur-sm lg:hidden"
      @click="sidebarOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed z-40 inset-y-0 left-0 w-[264px] bg-[#0f2a4a] text-white flex flex-col transform transition-transform duration-200 lg:static lg:translate-x-0 flex-shrink-0 border-r border-white/10',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div class="px-6 pt-7 pb-6 flex items-center gap-3">
        <div class="h-9 w-9 rounded-xl bg-white text-[#0f2a4a] flex items-center justify-center font-extrabold text-sm">B</div>
        <div>
          <h1 class="text-[17px] font-extrabold tracking-tight leading-none">BeStock</h1>
          <p class="text-[11px] font-medium text-blue-200/80 tracking-wide">Gestion de matériel</p>
        </div>
      </div>

      <div v-if="canWrite" class="px-4 pb-4">
        <NuxtLink
          to="/materiel/nouveau"
          class="flex items-center justify-center gap-2 bg-white text-[#0f2a4a] rounded-xl px-4 py-3 text-sm font-bold shadow-sm hover:bg-blue-50 transition"
          @click="sidebarOpen = false"
        >
          <Icon name="heroicons:plus" class="h-4 w-4" /> Ajouter un matériel
        </NuxtLink>
      </div>

      <nav class="flex-1 overflow-y-auto px-3 py-2 space-y-6">
        <div v-if="menuPrincipal.length">
          <p class="px-3 mb-2 text-[11px] font-semibold tracking-widest text-blue-200/60 uppercase">Principal</p>
          <div class="space-y-1">
            <NuxtLink
              v-for="item in menuPrincipal"
              :key="item.to"
              :to="item.to"
              class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition"
              :class="isActive(item.to) ? 'bg-white/10 text-white' : 'text-blue-100/80 hover:bg-white/10 hover:text-white'"
              @click="sidebarOpen = false"
            >
              <Icon :name="item.icon" class="h-5 w-5 shrink-0" /> {{ item.label }}
            </NuxtLink>
          </div>
        </div>

        <div>
          <p class="px-3 mb-2 text-[11px] font-semibold tracking-widest text-blue-200/60 uppercase">Mon espace</p>
          <div class="space-y-1">
            <NuxtLink
              to="/mes-materiels"
              class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition"
              :class="isActive('/mes-materiels') ? 'bg-white text-[#0f2a4a] shadow-sm' : 'text-blue-100/80 hover:bg-white/10 hover:text-white'"
              @click="sidebarOpen = false"
            >
              <Icon name="heroicons:archive-box" class="h-5 w-5 shrink-0" /> Mon matériel
            </NuxtLink>
          </div>
        </div>

        <div>
          <p class="px-3 mb-2 text-[11px] font-semibold tracking-widest text-blue-200/60 uppercase">Administration</p>
          <div class="space-y-1">
            <NuxtLink
              v-if="menuUtilisateurs.length"
              to="/users"
              class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition"
              :class="isActive('/users') ? 'bg-white/10 text-white' : 'text-blue-100/80 hover:bg-white/10 hover:text-white'"
              @click="sidebarOpen = false"
            >
              <Icon name="heroicons:users" class="h-5 w-5 shrink-0" /> Utilisateurs
            </NuxtLink>
            <NuxtLink
              to="/compte"
              class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition"
              :class="isActive('/compte') ? 'bg-white/10 text-white' : 'text-blue-100/80 hover:bg-white/10 hover:text-white'"
              @click="sidebarOpen = false"
            >
              <Icon name="heroicons:cog-6-tooth" class="h-5 w-5 shrink-0" /> Paramètres
            </NuxtLink>
          </div>
        </div>
      </nav>

      <div class="p-3 border-t border-white/10">
        <div class="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-white/5 mb-2">
          <div class="h-8 w-8 rounded-full bg-white/15 flex items-center justify-center text-xs font-bold">{{ initials }}</div>
          <div class="min-w-0">
            <p class="text-sm font-semibold leading-none truncate">{{ displayName }}</p>
            <p class="text-xs text-blue-200/70 truncate">{{ authStore.user?.email || 'Connecté' }}</p>
          </div>
        </div>
        <button
          @click="logout"
          class="w-full flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-blue-100/80 hover:bg-white/10 hover:text-white transition"
        >
          <Icon name="heroicons:arrow-right-on-rectangle" class="h-5 w-5 shrink-0" /> Déconnexion
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0">
      <header class="sticky top-0 z-20 bg-white/80 backdrop-blur border-b border-gray-200 h-[64px] flex items-center justify-between px-4 sm:px-6 lg:px-8 gap-4">
        <div class="flex items-center gap-3 min-w-0 flex-1 max-w-[640px]">
          <button
            @click="sidebarOpen = !sidebarOpen"
            class="lg:hidden p-2 -ml-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
            aria-label="Ouvrir le menu"
          >
            <Icon name="heroicons:bars-3" class="h-6 w-6" />
          </button>
          <div class="hidden sm:flex items-center gap-2 text-sm text-gray-500">
            <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
            <span class="font-medium text-gray-700">BeStock</span>
            <span class="text-gray-300">/</span>
            <span class="text-gray-900 font-semibold capitalize">{{ route.path === '/' ? 'Accueil' : route.path.split('/')[1] || 'Dashboard' }}</span>
          </div>
          <div class="sm:hidden font-semibold text-gray-900 truncate">BeStock</div>
          <div class="hidden md:flex items-center flex-1 ml-4">
            <div class="relative w-full">
              <Icon name="heroicons:magnifying-glass" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                v-model="globalSearch"
                @keydown.enter="onSearch"
                type="text"
                placeholder="Rechercher un matériel, collaborateur..."
                class="w-full pl-9 pr-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 focus:bg-white transition"
              />
            </div>
          </div>
        </div>
        <div class="flex items-center gap-1 sm:gap-2">
          <button class="relative p-2.5 text-gray-500 hover:text-gray-900 hover:bg-gray-50 rounded-xl transition" aria-label="Notifications">
            <Icon name="heroicons:bell" class="h-5 w-5" />
            <span v-if="hasAlerts" class="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 bg-amber-500 rounded-full ring-2 ring-white"></span>
          </button>
          <div class="h-6 w-px bg-gray-200 hidden sm:block"></div>
          <NuxtLink to="/compte" class="flex items-center gap-2.5 pl-1 pr-3 py-1.5 rounded-full border border-gray-200 bg-white hover:bg-gray-50 transition">
            <span class="h-7 w-7 rounded-full bg-[#0f2a4a] text-white flex items-center justify-center text-xs font-bold">{{ initials }}</span>
            <span class="hidden sm:block text-sm font-semibold text-gray-700 max-w-[120px] truncate">{{ displayName }}</span>
            <Icon name="heroicons:chevron-down" class="hidden sm:block h-4 w-4 text-gray-400" />
          </NuxtLink>
        </div>
      </header>

      <main class="flex-1 p-4 sm:p-6 lg:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { useAuthStore } from '~/stores/auth';
import { useEquipementsStore } from '~/stores/equipements';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const eqStore = useEquipementsStore();

const sidebarOpen = ref(false);
const globalSearch = ref('');

watch(() => route.fullPath, () => {
  sidebarOpen.value = false;
});

const isActive = (path) => route.path.startsWith(path);

const displayName = computed(() => {
  const user = authStore.user;
  if (!user) return 'Compte Admin';
  return user.username || user.email || 'Compte Admin';
});

const initials = computed(() => {
  const name = displayName.value || 'A';
  return name.slice(0, 2).toUpperCase();
});

const { role, isEmploye, isManager, isAdmin, isSuperAdmin, canWrite, can } = useRole();

const menuPrincipal = computed(() => {
  const items = [
    { to: '/', label: 'Accueil', icon: 'heroicons:home', perm: 'dashboard:view' },
    { to: '/dashboard', label: 'Dashboard', icon: 'heroicons:chart-bar', perm: 'dashboard:view' },
    { to: '/categories', label: 'Catégories', icon: 'heroicons:folder', perm: 'referentiels:read' },
    { to: '/employes', label: 'Collaborateurs', icon: 'heroicons:user-group', perm: 'employes:read' },
    { to: '/affectations', label: 'Affectations', icon: 'heroicons:clipboard-document-list', perm: 'affectations:read' },
    { to: '/maintenance', label: 'Maintenance', icon: 'heroicons:wrench-screwdriver', perm: 'maintenances:read' },
    { to: '/historique', label: 'Historique', icon: 'heroicons:clock', perm: 'historique:read' },
  ];
  return items.filter((i) => can(i.perm));
});

const menuUtilisateurs = computed(() => {
  return can('users:read')
    ? [{ to: '/users', label: 'Utilisateurs', icon: 'heroicons:users' }]
    : [];
});

const hasAlerts = computed(() => {
  const s = eqStore.stats || {};
  return (s.maintenance ?? 0) > 0 || (s.endommages ?? 0) > 0 || (s.perdus ?? 0) > 0;
});

const onSearch = () => {
  const q = globalSearch.value.trim();
  if (!q) return;
  router.push({ path: '/categories', query: { q } });
};

const logout = async () => {
  await authStore.logout();
  router.push('/connexion');
};
</script>