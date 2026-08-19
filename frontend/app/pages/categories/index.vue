<template>
  <NuxtLayout name="dashboard">
    <div class="max-w-6xl mx-auto">
      <div class="mb-10">
        <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Catégories de matériel</h2>
        <p class="text-gray-500 mt-2 text-lg">Gérez et consultez les différentes catégories d'inventaire.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <NuxtLink
          v-for="category in catStore.categories"
          :key="category.id"
          :to="`/categories/${category.id}`"
          class="block bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow hover:border-blue-200"
        >
          <div class="flex items-center justify-between mb-4">
            <Icon :name="category.icon" class="h-8 w-8 text-blue-900" />
            <span class="text-xs font-semibold text-blue-900 bg-blue-50 px-2 py-1 rounded-full">
              {{ eqStore.getMaterials(category.id).length }}
            </span>
          </div>
          <h3 class="font-semibold text-gray-900 mb-2">{{ category.name }}</h3>
          <p class="text-sm text-gray-600 mb-4">{{ category.description }}</p>
          <span class="text-blue-900 font-semibold hover:underline">Voir les articles →</span>
        </NuxtLink>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import { useCategoriesStore } from '@/stores/categories';
import { useEquipementsStore } from '@/stores/equipements';
const catStore = useCategoriesStore();
const eqStore = useEquipementsStore();

onMounted(() => {
  Promise.all([catStore.fetchReferentiels(), eqStore.fetchEquipements()]);
});
</script>