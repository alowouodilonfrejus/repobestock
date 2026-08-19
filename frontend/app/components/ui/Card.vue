<template>
  <div class="bg-white p-6 rounded-lg border border-gray-200">
    <h3 v-if="title" class="font-semibold mb-4 text-gray-800">{{ title }}</h3>
    <slot />
  </div>
</template>

<script setup>
defineProps(['title']);
</script>
