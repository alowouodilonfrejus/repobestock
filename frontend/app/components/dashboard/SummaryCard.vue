<template>
  <div class="bg-white p-6 rounded-xl shadow-md border border-gray-100 flex flex-col transition-transform duration-200 hover:-translate-y-0.5">
    <div class="flex justify-between items-start mb-4">
      <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider max-w-[80%]">{{ title }}</span>
      <span class="flex"><Icon :name="icon" class="h-6 w-6 text-blue-900" /></span>
    </div>
    <div class="text-3xl font-bold text-gray-900 mb-2">{{ value }}</div>
    <div class="text-green-500 text-sm font-medium" v-if="subtext">{{ subtext }}</div>
    <div class="mt-auto pt-4" v-if="link">
      <NuxtLink :to="linkTo" class="text-blue-600 no-underline text-sm font-medium hover:text-blue-500">{{ link }} →</NuxtLink>
    </div>
  </div>
</template>

<script setup>
defineProps(['title', 'value', 'subtext', 'icon', 'link', 'linkTo']);
</script>
