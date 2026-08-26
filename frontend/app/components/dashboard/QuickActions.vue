<template>
  <div class="flex flex-wrap gap-2.5">
    <NuxtLink v-if="can('stock:write')" to="/materiel/nouveau" class="inline-flex items-center gap-2 bg-[#0f2a4a] text-white rounded-xl px-4 py-2.5 text-sm font-semibold shadow-sm hover:bg-[#0d2340] transition">
      <Icon name="heroicons:plus" class="h-4 w-4" /> Ajouter un matériel
    </NuxtLink>
    <NuxtLink v-if="can('affectations:write')" to="/affectations/nouvelle" class="inline-flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-50 transition">
      <Icon name="heroicons:clipboard-document-list" class="h-4 w-4 text-blue-700" /> Affecter un matériel
    </NuxtLink>
    <NuxtLink v-if="can('employes:write')" to="/employes" class="inline-flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-50 transition">
      <Icon name="heroicons:user-plus" class="h-4 w-4 text-gray-600" /> Ajouter un collaborateur
    </NuxtLink>
    <NuxtLink to="/affectations" class="inline-flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-4 py-2.5 text-sm font-semibold text-gray-800 hover:bg-gray-50 transition">
      <Icon name="heroicons:arrow-uturn-left" class="h-4 w-4 text-gray-600" /> Enregistrer un retour
    </NuxtLink>
  </div>
</template>

<script setup>
const { can } = useRole()
</script>
