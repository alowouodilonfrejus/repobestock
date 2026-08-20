<template>
  <div class="bg-white p-4 sm:p-6 rounded-xl shadow-md border border-gray-100 mt-8">
    <h3 class="text-lg font-semibold text-gray-700 mb-6 ml-1 sm:ml-0">Matériaux ajoutés récemment</h3>
    <div class="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
      <table class="w-full border-collapse min-w-[560px]">
        <thead>
          <tr>
            <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">NOM</th>
            <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">CATÉGORIE</th>
            <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide hidden md:table-cell">CARACTÉRISTIQUES</th>
            <th class="text-xs text-gray-500 text-left p-4 uppercase tracking-wide">ÉTAT</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in materials" :key="item.id">
            <td class="font-medium text-gray-800 flex items-center gap-3 p-4 border-t border-gray-100">
              <Icon :name="item.icon" class="h-6 w-6 text-blue-900" /> {{ item.nom }}
            </td>
            <td class="p-4 border-t border-gray-100">{{ item.categoryName }}</td>
            <td class="p-4 border-t border-gray-100 hidden md:table-cell">{{ item.characteristics }}</td>
            <td class="p-4 border-t border-gray-100">
              <span :class="['px-3 py-1 rounded-full text-sm font-medium', item.statusClass]">
                {{ item.statut }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { useCategoriesStore } from '@/stores/categories';
import { useEquipementsStore } from '@/stores/equipements';

const catStore = useCategoriesStore();
const eqStore = useEquipementsStore();

const materials = computed(() => {
  return eqStore.recentMaterials.map((m) => {
    const category = catStore.categories.find((c) => c.id === m.categorie_id);
    const statut = catStore.statuts.find((s) => s.id === m.statut_id);
    const icon = category?.icon || 'heroicons:archive-box';
    const categoryName = category?.name || '—';
    const characteristics = [m.marque, m.modele, m.numero_serie]
      .filter(Boolean)
      .join(' • ') || '—';
    return {
      ...m,
      icon,
      categoryName,
      characteristics,
      statut: statut?.nom || '—',
      statusClass: statut?.nom?.toLowerCase().includes('maintenance') ? 'bg-orange-50 text-orange-800' : statut?.nom?.toLowerCase().includes('défectueux') || statut?.nom?.toLowerCase().includes('defectueux') ? 'bg-red-50 text-red-700' : 'bg-teal-50 text-teal-700',
    };
  });
});
</script>