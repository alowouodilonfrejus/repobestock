<template>
  <div class="layout">
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<script setup>
</script>

<style>
/* Reset de base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #333;
}
</style>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background-color: #f8fafc;
}
.main-content {
  flex: 1;
}
</style>
