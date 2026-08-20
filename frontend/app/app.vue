<template>
  <NuxtLayout>
    <NuxtPage/>
  </NuxtLayout>
  <UiToast />
  <UiConfirmDialog />
</template>

<script setup>
useHead({
  htmlAttrs: {
    class: 'scroll-smooth scroll-pt-20'
  }
})
</script>
