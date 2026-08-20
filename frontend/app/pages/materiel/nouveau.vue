<template>
  <NuxtLayout name="dashboard">
    <div class="max-w-6xl mx-auto">
      <div class="mb-10">
        <h2 class="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">Enregistrement d'un nouveau matériel</h2>
        <p class="text-gray-500 mt-2 text-base sm:text-lg">Remplissez les détails techniques pour enregistrer une nouvelle unité dans le système d'inventaire.</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-10">
          <!-- Identification principale -->
          <UiCard title="Identification principale" class="md:col-span-2 shadow-sm border border-gray-200">
            <UiSelect label="Catégorie" v-model="form.categoryId" @change="onCategoryChange">
              <option value="">Sélectionner une catégorie</option>
              <option v-for="cat in catStore.categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </UiSelect>

            <UiInput label="Nom du matériel" type="text" v-model="form.name" placeholder="ex: Serveur Dell PowerEdge" />

            <UiInput label="Référence" type="text" v-model="form.reference" placeholder="ex: REF-001" />

            <div v-if="activeCategory" class="mt-6">
              <h4 class="font-semibold text-gray-800 mb-4">
                {{ activeCategory.icon }} Informations {{ activeCategory.name }}
              </h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <template v-for="field in catStore.fieldsFor(form.categoryId)" :key="field.key">
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

          <!-- Logistique Initiale -->
          <UiCard title="Logistique Initiale" class="shadow-sm border border-gray-200">
            <div class="space-y-4">
              <UiSelect label="État" v-model="form.statut_id">
                <option v-for="statut in catStore.statuts" :key="statut.id" :value="statut.id">
                  {{ statut.nom }}
                </option>
              </UiSelect>

              <UiSelect label="Emplacement" v-model="form.emplacement_id">
                <option value="">Sélectionner un emplacement</option>
                <option v-for="emp in catStore.emplacements" :key="emp.id" :value="emp.id">
                  {{ emp.nom }}
                </option>
              </UiSelect>
            </div>
          </UiCard>
        </div>

        <!-- Actions -->
        <div class="mt-10 pt-8 border-t border-gray-200 flex flex-wrap justify-end gap-5">
          <button type="button" @click="resetForm" class="px-6 sm:px-8 py-3 border border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-100 transition">
            Annuler
          </button>
          <button type="submit" class="px-6 sm:px-8 py-3 bg-blue-900 text-white rounded-lg text-sm font-semibold hover:bg-blue-800 transition shadow-sm w-full sm:w-auto">
            Enregistrer le matériel
          </button>
        </div>
      </form>
    </div>
  </NuxtLayout>
</template>

<script setup>
import { reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCategoriesStore } from '@/stores/categories';
import { useEquipementsStore } from '@/stores/equipements';

const router = useRouter();
const catStore = useCategoriesStore();
const eqStore = useEquipementsStore();

onMounted(async () => {
  await Promise.all([catStore.fetchReferentiels(), eqStore.fetchEquipements()]);
  form.statut_id = defaultStatutId;
});

const form = reactive({
  categoryId: '',
  name: '',
  reference: '',
  statut_id: '',
  emplacement_id: '',
});

const activeCategory = computed(() => catStore.categories.find((c) => c.id === Number(form.categoryId)));

const defaultStatutId = computed(() => {
  const fonctionnel = catStore.statuts.find((s) => s.nom.toLowerCase() === 'fonctionnel');
  return fonctionnel?.id || '';
});

const onCategoryChange = () => {
  catStore.fieldsFor(form.categoryId).forEach((field) => {
    form[field.key] = '';
  });
};

const resetForm = () => {
  form.categoryId = '';
  form.name = '';
  form.reference = '';
  form.statut_id = defaultStatutId.value;
  form.emplacement_id = '';
  catStore.fieldsFor(form.categoryId).forEach((field) => {
    form[field.key] = '';
  });
};

const handleSubmit = async () => {
  if (!form.categoryId) {
    alert('Veuillez sélectionner une catégorie.');
    return;
  }
  if (!form.name.trim()) {
    alert('Veuillez renseigner le nom du matériel.');
    return;
  }
  if (!form.statut_id) {
    alert('Veuillez sélectionner un statut.');
    return;
  }
  try {
    await eqStore.addMaterial(form.categoryId, {
      name: form.name,
      reference: form.reference,
      statut_id: form.statut_id,
      emplacement_id: form.emplacement_id || null,
      ...Object.fromEntries(
        catStore.fieldsFor(form.categoryId).map((f) => [f.key, form[f.key] || undefined])
      ),
    });
    alert('Matériel enregistré avec succès.');
    resetForm();
  } catch (error) {
    alert(error.response?.data?.detail || 'Erreur lors de l\'enregistrement.');
  }
};
</script>