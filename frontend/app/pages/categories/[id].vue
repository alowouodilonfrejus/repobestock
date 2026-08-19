<template>
  <NuxtLayout name="dashboard">
    <div v-if="category" class="max-w-6xl mx-auto">
      <div class="mb-10">
        <div class="flex items-center gap-4">
          <Icon :name="category.icon" class="h-10 w-10 text-blue-900" />
          <div>
            <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">{{ category.name }}</h2>
            <p class="text-gray-500 mt-1 text-lg">{{ category.description }}</p>
          </div>
        </div>
      </div>

      <UiCard title="Matériels associés" class="shadow-sm border border-gray-200">
        <div v-if="materials.length > 0" class="divide-y divide-gray-100">
          <div v-for="material in materials" :key="material.id" class="py-4 flex items-center justify-between gap-4">
            <div class="flex items-center gap-4">
              <Icon :name="category.icon" class="h-6 w-6 text-blue-900" />
              <div>
                <p class="font-semibold text-gray-900">{{ material.nom }}</p>
                <p class="text-sm text-gray-500">
                  <span v-if="material.reference" class="mr-2 text-xs font-mono bg-gray-100 px-1.5 py-0.5 rounded">{{ material.reference }}</span>
                  {{ summary(material) }}
                </p>
                <p class="text-xs text-gray-400 mt-1">
                  <Icon name="heroicons:map-pin" class="h-4 w-4 inline-block text-gray-400" /> {{ emplacementName(material.emplacement_id) }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span :class="['px-3 py-1 rounded-full text-xs font-semibold', statusClass(material.statut_id)]">
                {{ statutName(material.statut_id) }}
              </span>
              <NuxtLink
                :to="`/equipements/${material.id}`"
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-semibold hover:bg-gray-100 transition"
              >
                Historique
              </NuxtLink>
              <NuxtLink
                :to="`/materiel/${category.id}/${material.id}`"
                class="px-4 py-2 border border-blue-900 text-blue-900 rounded-lg text-sm font-semibold hover:bg-blue-900 hover:text-white transition"
              >
                Modifier
              </NuxtLink>
            </div>
          </div>
        </div>
        <p v-else class="text-gray-500 py-4">Aucun matériel dans cette catégorie.</p>
      </UiCard>
    </div>
    <div v-else class="text-center py-10">
      <h2 class="text-xl text-gray-600">Catégorie non trouvée.</h2>
      <NuxtLink to="/categories" class="text-blue-900 font-semibold hover:underline">Retour aux catégories</NuxtLink>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { onMounted } from 'vue';
import { useCategoriesStore } from '@/stores/categories';
import { useEquipementsStore } from '@/stores/equipements';

const route = useRoute();
const catStore = useCategoriesStore();
const eqStore = useEquipementsStore();

onMounted(() => {
  Promise.all([catStore.fetchReferentiels(), eqStore.fetchEquipements()]);
});

const category = computed(() => catStore.categories.find((c) => c.id === Number(route.params.id)));
const materials = computed(() => eqStore.getMaterials(route.params.id));

const summary = (material) => {
  const parts = [];
  if (material.marque) parts.push(material.marque);
  if (material.modele) parts.push(material.modele);
  if (material.numero_serie) parts.push(`SN: ${material.numero_serie}`);
  if (parts.length === 0) return 'Aucune caractéristique renseignée';
  return parts.join(' • ');
};

const statutName = (statutId) => {
  const st = catStore.statuts.find((s) => s.id === statutId);
  return st?.nom || '—';
};

const statusClass = (statutId) => {
  const nom = statutName(statutId).toLowerCase();
  if (nom.includes('maintenance')) return 'bg-amber-100 text-amber-800';
  if (nom.includes('défectueux') || nom.includes('defectueux')) return 'bg-red-100 text-red-800';
  return 'bg-green-100 text-green-800';
};

const emplacementName = (id) => {
  const emp = catStore.emplacements.find((e) => e.id === id);
  return emp?.nom || 'Non affecté';
};
</script>