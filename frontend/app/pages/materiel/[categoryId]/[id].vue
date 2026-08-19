<template>
  <NuxtLayout name="dashboard">
    <div v-if="category && material" class="max-w-6xl mx-auto">
      <div class="mb-10">
        <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">Modification du matériel</h2>
        <p class="text-gray-500 mt-2 text-lg">Modifiez les informations de « {{ material.nom }} » ({{ category.name }}).</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-8">
        <div class="grid grid-cols-3 gap-10">
          <UiCard title="Identification principale" class="col-span-2 shadow-sm border border-gray-200">
            <div class="mb-4">
              <p class="block text-sm text-gray-700 mb-1">Catégorie</p>
              <p class="border border-gray-200 rounded p-2 text-sm bg-gray-50">{{ category.icon }} {{ category.name }}</p>
            </div>

            <UiInput label="Nom du matériel" type="text" v-model="form.name" />

            <div class="mt-6">
              <h4 class="font-semibold text-gray-800 mb-4">
                {{ category.icon }} Informations {{ category.name }}
              </h4>
              <div class="grid grid-cols-2 gap-4">
                <template v-for="field in fields" :key="field.key">
                  <UiSelect
                    v-if="field.type === 'select'"
                    :label="field.label"
                    v-model="form[field.key]"
                  >
                    <option value="">Sélectionner...</option>
                    <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
                  </UiSelect>
                  <UiTextarea
                    v-else-if="field.type === 'textarea'"
                    :label="field.label"
                    v-model="form[field.key]"
                    :placeholder="field.placeholder"
                  />
                  <UiInput
                    v-else
                    :label="field.label"
                    :type="field.type"
                    v-model="form[field.key]"
                    :placeholder="field.placeholder"
                  />
                </template>
              </div>
            </div>
          </UiCard>

          <UiCard title="État du matériel" class="shadow-sm border border-gray-200">
            <div class="space-y-4">
              <UiSelect label="État" v-model="form.statut_id">
                <option value="">Sélectionner...</option>
                <option v-for="statut in catStore.statuts" :key="statut.id" :value="statut.id">
                  {{ statut.nom }}
                </option>
              </UiSelect>

              <UiSelect label="Emplacement" v-model="form.emplacement_id">
                <option value="">Aucun</option>
                <option v-for="emp in catStore.emplacements" :key="emp.id" :value="emp.id">
                  {{ emp.nom }}
                </option>
              </UiSelect>
            </div>
          </UiCard>
        </div>

        <div class="mt-10 pt-8 border-t border-gray-200 flex justify-end gap-5">
          <button type="button" @click="router.push(`/categories/${category.id}`)" class="px-8 py-3 border border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-100 transition">
            Annuler
          </button>
          <button type="button" @click="handleDelete" class="px-8 py-3 border border-red-300 text-red-700 rounded-lg text-sm font-semibold hover:bg-red-50 transition">
            Supprimer
          </button>
          <button type="submit" class="px-8 py-3 bg-blue-900 text-white rounded-lg text-sm font-semibold hover:bg-blue-800 transition shadow-sm">
            Enregistrer les modifications
          </button>
        </div>
      </form>
    </div>
    <div v-else class="text-center py-10">
      <h2 class="text-xl text-gray-600">Matériel non trouvé.</h2>
      <NuxtLink to="/categories" class="text-blue-900 font-semibold hover:underline">Retour aux catégories</NuxtLink>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { reactive, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useCategoriesStore } from '@/stores/categories';
import { useEquipementsStore } from '@/stores/equipements';

const route = useRoute();
const router = useRouter();
const catStore = useCategoriesStore();
const eqStore = useEquipementsStore();

onMounted(() => {
  Promise.all([catStore.fetchReferentiels(), eqStore.fetchEquipements()]);
});

const category = computed(() => catStore.categories.find((c) => c.id === Number(route.params.categoryId)));
const material = computed(() => eqStore.equipements.find((m) => m.id === Number(route.params.id)));

const fields = computed(() => catStore.fieldsFor(category.value?.id));

const form = reactive({
  name: material.value?.nom || '',
  statut_id: material.value?.statut_id || '',
  emplacement_id: material.value?.emplacement_id || '',
});

watch(
  () => [category.value?.id, material.value?.id],
  () => {
    form.name = material.value?.nom || '';
    form.statut_id = material.value?.statut_id || '';
    form.emplacement_id = material.value?.emplacement_id || '';
    fields.value.forEach((field) => {
      form[field.key] = material.value?.[field.key] || '';
    });
  },
  { immediate: true }
);

const handleSubmit = async () => {
  if (!form.name.trim()) {
    alert('Veuillez renseigner le nom du matériel.');
    return;
  }
  try {
    await eqStore.updateMaterial(route.params.id, {
      name: form.name,
      statut_id: form.statut_id,
      emplacement_id: form.emplacement_id,
      ...Object.fromEntries(
        fields.value.map((f) => [f.key, form[f.key] || undefined])
      ),
    });
    alert('Matériel modifié avec succès.');
    router.push(`/categories/${route.params.categoryId}`);
  } catch (error) {
    alert(error.response?.data?.detail || 'Erreur lors de la modification.');
  }
};

const handleDelete = async () => {
  if (confirm(`Supprimer « ${material.value.nom} » ?`)) {
    try {
      await eqStore.removeMaterial(route.params.id);
      alert('Matériel supprimé.');
      router.push(`/categories/${route.params.categoryId}`);
    } catch (error) {
      alert(error.response?.data?.detail || 'Erreur lors de la suppression.');
    }
  }
};
</script>