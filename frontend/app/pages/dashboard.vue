<template>
  <NuxtLayout name="dashboard">
    <!-- Header section -->
    <div class="mb-6">
      <h1 class="text-[26px] font-extrabold tracking-tight text-gray-900">Dashboard</h1>
      <p class="text-sm text-gray-500 mt-1">Vue d'ensemble de votre gestion de matériel.</p>
    </div>

    <QuickActions class="mb-6" />

    <!-- Loading skeletons for primary stats -->
    <div v-if="isLoadingStats" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="bg-white rounded-2xl border border-gray-200 p-5 animate-pulse">
        <div class="h-9 w-9 bg-gray-100 rounded-xl"></div>
        <div class="h-3 bg-gray-100 rounded w-1/2 mt-4"></div>
        <div class="h-7 bg-gray-100 rounded w-1/3 mt-3"></div>
      </div>
    </div>

    <!-- 4 primary stats -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <DashboardStatCard
        title="Articles en stock"
        :value="stats.total ?? eqStore.totalStock"
        :subtitle="stats.total ? `${stats.total} matériels au total` : 'Aucun matériel'"
        hint="Parc global"
        icon="heroicons:archive-box"
        variant="default"
      />
      <DashboardStatCard
        title="Disponibles"
        :value="stats.disponibles ?? 0"
        :subtitle="disponiblesHint"
        hint="Prêts à affecter"
        icon="heroicons:check-circle"
        variant="success"
        to="/affectations/nouvelle"
      />
      <DashboardStatCard
        title="Affectés"
        :value="stats.affectes ?? 0"
        :subtitle="affectesHint"
        hint="Sous responsabilité"
        icon="heroicons:user-group"
        variant="info"
        to="/affectations"
      />
      <DashboardStatCard
        title="En maintenance"
        :value="stats.maintenance ?? eqStore.maintenanceCount"
        :subtitle="maintenanceHint"
        hint="Non affectables"
        icon="heroicons:wrench-screwdriver"
        variant="warning"
        to="/maintenance"
      />
    </div>

    <!-- Analyse + Activité -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6 mt-6">
      <!-- Affectations récentes -->
      <UiCard class="rounded-2xl border border-gray-200 shadow-sm p-5 xl:col-span-1">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-gray-900">Affectations récentes</h3>
          <NuxtLink to="/affectations" class="text-xs font-semibold text-blue-700 hover:underline">Tout voir</NuxtLink>
        </div>
        <div v-if="isLoadingStats" class="space-y-3 animate-pulse">
          <div v-for="i in 3" :key="i" class="h-14 bg-gray-50 rounded-xl"></div>
        </div>
        <ul v-else class="divide-y divide-gray-100">
          <li v-for="a in stats.affectations_recentes || []" :key="a.id" class="py-3 flex items-center justify-between gap-3">
            <div class="min-w-0">
              <p class="font-semibold text-sm text-gray-900 truncate">{{ a.employe_nom }}</p>
              <p class="text-xs text-gray-500">{{ formatDate(a.date_affectation) }} · {{ a.nombre_items }} matériel(s)</p>
            </div>
            <span class="text-xs font-semibold px-2.5 py-1 rounded-full shrink-0" :class="statutBadge(a.statut)">{{ statutLabel(a.statut) }}</span>
          </li>
          <li v-if="(stats.affectations_recentes || []).length === 0" class="py-10 text-center">
            <Icon name="heroicons:clipboard-document-list" class="h-8 w-8 text-gray-300 mx-auto" />
            <p class="text-sm text-gray-500 mt-2">Aucune affectation récente.</p>
            <NuxtLink to="/affectations/nouvelle" class="mt-3 inline-flex text-xs font-semibold text-blue-700 hover:underline">Créer une affectation →</NuxtLink>
          </li>
        </ul>
        <NuxtLink to="/affectations/nouvelle" class="mt-4 flex items-center justify-center gap-2 px-4 py-2.5 bg-[#0f2a4a] text-white rounded-xl text-sm font-semibold hover:bg-[#0d2340] transition">
          <Icon name="heroicons:plus" class="h-4 w-4" /> Nouvelle affectation
        </NuxtLink>
      </UiCard>

      <div class="xl:col-span-2">
        <ActivityFeed :items="historiqueItems" :loading="histLoading" />
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useEquipementsStore } from '@/stores/equipements';
import { useHistoriqueStore } from '@/stores/historique';
import DashboardStatCard from '@/components/dashboard/DashboardStatCard.vue';
import QuickActions from '@/components/dashboard/QuickActions.vue';
import ActivityFeed from '@/components/dashboard/ActivityFeed.vue';

const eqStore = useEquipementsStore();
const histStore = useHistoriqueStore();

const histLoading = ref(false);

const stats = computed(() => eqStore.stats || {});

const isLoadingStats = computed(() => !eqStore._loadedStats && !stats.value.total && eqStore.loading);

const historiques = computed(() => histStore.historique || []);
const historiqueItems = computed(() => historiques.value.slice(0, 6));

const disponiblesHint = computed(() => {
  const v = stats.value.disponibles ?? 0;
  if (v === 0) return 'Aucun disponible';
  return `${v} prêts à être attribués`;
});
const affectesHint = computed(() => {
  const v = stats.value.affectes ?? 0;
  return v ? `${v} sous responsabilité` : 'Aucun affecté';
});
const maintenanceHint = computed(() => {
  const v = stats.value.maintenance ?? 0;
  return v ? `${v} non affectables` : 'Aucune maintenance';
});

function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('fr-FR');
}
function statutBadge(statut) {
  const badges = {
    active: 'bg-sky-50 text-sky-700 border border-sky-200',
    partielle: 'bg-amber-50 text-amber-700 border border-amber-200',
    retournee: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    annulee: 'bg-gray-100 text-gray-500 border border-gray-200',
  };
  return badges[statut] || 'bg-gray-100 text-gray-500 border border-gray-200';
}
function statutLabel(statut) {
  const labels = { active: 'Active', partielle: 'Partielle', retournee: 'Retournée', annulee: 'Annulée' };
  return labels[statut] || statut;
}

onMounted(async () => {
  histLoading.value = true;
  try {
    await Promise.all([
      eqStore.fetchStats(true).catch(() => {}),
      histStore.fetchHistorique(true).catch(() => {}),
    ]);
  } finally {
    histLoading.value = false;
  }
});
</script>
