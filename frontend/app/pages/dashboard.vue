<template>
  <NuxtLayout name="dashboard">
    <DashboardHeader />
    <div class="cards-grid">
      <SummaryCard title="TOTAL DES ARTICLES EN STOCK" :value="eqStore.totalStock" subtext="Stock actuel" icon="heroicons:archive-box" />
      <SummaryCard title="MATÉRIAUX NÉCESSITANT UNE MAINTENANCE" :value="eqStore.maintenanceCount" subtext="Action requise" icon="heroicons:wrench-screwdriver" />
      <SummaryCard title="LES TYPES DE MATÉRIAUX" :value="catStore.categories.length" icon="heroicons:cube" link="Voir le tableau" link-to="/categories" />
    </div>
    <MaterialTable />
  </NuxtLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import { useCategoriesStore } from '@/stores/categories';
import { useEquipementsStore } from '@/stores/equipements';
import DashboardHeader from '@/components/dashboard/DashboardHeader.vue';
import SummaryCard from '@/components/dashboard/SummaryCard.vue';
import MaterialTable from '@/components/dashboard/MaterialTable.vue';

const catStore = useCategoriesStore();
const eqStore = useEquipementsStore();

onMounted(() => {
  Promise.all([catStore.fetchReferentiels(), eqStore.fetchStats()]);
});
</script>

<style scoped>
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}
</style>