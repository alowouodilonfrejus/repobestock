<template>
  <header class="header">
    <h1 class="title">Dashboard</h1>

    <div class="header-actions">
      <Icon name="heroicons:bell" class="h-5 w-5" />
      <Icon name="heroicons:cog" class="h-5 w-5" />
    </div>
  </header>
</template>

<script setup>
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a202c;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}
.icon-btn {
  cursor: pointer;
  padding: 0.5rem;
  color: #4a5568;
}
</style>
