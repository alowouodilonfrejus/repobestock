<template>
  <div class="table-section">
    <h3 class="section-title">Matériaux ajoutés récemment</h3>
    <table class="table">
      <thead>
        <tr>
          <th>NOM</th>
          <th>CATÉGORIE</th>
          <th>CARACTÉRISTIQUES</th>
          <th>ÉTAT</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in materials" :key="item.id">
          <td class="name-cell">
            <Icon :name="item.icon" class="h-6 w-6 text-blue-900" /> {{ item.nom }}
          </td>
          <td>{{ item.categoryName }}</td>
          <td class="char-cell">{{ item.characteristics }}</td>
          <td class="status-cell">
            <span :class="['status-badge', item.statusClass]">
              {{ item.statut }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
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
      statusClass: statut?.nom?.toLowerCase().includes('maintenance') ? 'status-warning' : statut?.nom?.toLowerCase().includes('défectueux') || statut?.nom?.toLowerCase().includes('defectueux') ? 'status-error' : 'status-good',
    };
  });
});
</script>

<style scoped>
.table-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
  margin-top: 2rem;
  border: 1px solid #edf2f7;
}
.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1.5rem;
}
.table {
  width: 100%;
  border-collapse: collapse;
}
th {
  font-size: 0.75rem;
  color: #718096;
  text-align: left;
  padding: 1rem;
  text-transform: uppercase;
}
td {
  padding: 1rem;
  border-top: 1px solid #edf2f7;
}
.name-cell {
  font-weight: 500;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 12px;
}
.icon {
  font-size: 1.2rem;
  background-color: #f7fafc;
  padding: 0.5rem;
  border-radius: 8px;
}
.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 500;
}
.status-good {
  background-color: #e6fffa;
  color: #2c7a7b;
}
.status-warning {
  background-color: #fffaf0;
  color: #975a16;
}
.status-error {
  background-color: #fff5f5;
  color: #c53030;
}
</style>