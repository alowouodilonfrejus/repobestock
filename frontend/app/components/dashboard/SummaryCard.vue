<template>
  <div class="card">
    <div class="card-header">
      <span class="card-title">{{ title }}</span>
      <span class="card-icon"><Icon :name="icon" class="h-6 w-6 text-blue-900" /></span>
    </div>
    <div class="card-value">{{ value }}</div>
    <div class="card-subtext" v-if="subtext">{{ subtext }}</div>
    <div class="card-link" v-if="link">
      <NuxtLink :to="linkTo" class="">{{ link }} →</NuxtLink>
    </div>
  </div>
</template>

<script setup>
defineProps(['title', 'value', 'subtext', 'icon', 'link', 'linkTo']);
</script>

<style scoped>
.card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
  border: 1px solid #edf2f7;
  transition: transform 0.2s;
  display: flex;
  flex-direction: column;
}
.card:hover {
  transform: translateY(-2px);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}
.card-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  max-width: 80%;
}
.card-icon {
  display: flex;
}
.card-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.5rem;
}
.card-subtext {
  color: #48bb78;
  font-size: 0.85rem;
  font-weight: 500;
}
.card-link {
  margin-top: auto;
  padding-top: 1rem;
}
.card-link a {
  color: #3182ce;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
}
</style>
