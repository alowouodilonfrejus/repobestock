<template>
  <UiCard class="rounded-2xl border border-gray-200 shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-bold text-gray-900">Activité récente</h3>
      <NuxtLink to="/historique" class="text-xs font-semibold text-blue-700 hover:underline">Voir l'historique →</NuxtLink>
    </div>
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="animate-pulse flex gap-3">
        <div class="h-8 w-8 rounded-full bg-gray-100"></div>
        <div class="flex-1 space-y-2"><div class="h-3 bg-gray-100 rounded w-3/4"></div><div class="h-3 bg-gray-100 rounded w-1/2"></div></div>
      </div>
    </div>
    <div v-else-if="!items.length" class="py-8 text-center">
      <Icon name="heroicons:clock" class="h-8 w-8 text-gray-300 mx-auto" />
      <p class="text-sm text-gray-500 mt-2">Aucune activité récente.</p>
    </div>
    <ul v-else class="space-y-1">
      <li v-for="e in items" :key="e.id" class="flex gap-3 py-3 -mx-2 px-2 rounded-xl hover:bg-gray-50 transition">
        <span class="h-8 w-8 rounded-full flex items-center justify-center shrink-0 mt-0.5" :class="iconWrap(e.action)">
          <Icon :name="iconFor(e.action)" class="h-4 w-4" :class="iconColor(e.action)" />
        </span>
        <div class="min-w-0 flex-1">
          <p class="text-sm leading-5 text-gray-900">
            <span class="font-semibold">{{ e.utilisateur_nom || 'Utilisateur' }}</span>
            <span class="text-gray-500"> — {{ labelFor(e.action) }}</span>
            <span class="font-medium"> {{ equipName(e.equipement_id) }}</span>
          </p>
          <p class="text-xs text-gray-500 mt-0.5 truncate">{{ e.nouvelle_valeur || e.ancienne_valeur || '—' }}</p>
          <p class="text-xs text-gray-400 mt-1 flex items-center gap-1.5"><Icon name="heroicons:clock" class="h-3.5 w-3.5" /> {{ fmt(e.date_action) }}</p>
        </div>
        <span class="shrink-0 self-center text-xs font-semibold px-2 py-1 rounded-full" :class="badgeFor(e.action)">{{ labelFor(e.action) }}</span>
      </li>
    </ul>
  </UiCard>
</template>

<script setup>
import { computed } from 'vue'
import { useEquipementsStore } from '~/stores/equipements'
const props = defineProps({ items: { type: Array, default: () => [] }, loading: Boolean })
const eqStore = useEquipementsStore()
const items = computed(() => (props.items || []).slice(0, 6))
function equipName(id){
  if(!id) return 'Équipement'
  const e = eqStore.equipements.find(x=>x.id===id) || eqStore.stats.recent?.find(x=>x.id===id)
  return e?.nom || `Matériel #${id}`
}
function labelFor(a){ return {creation:'a créé', modification:'a modifié', suppression:'a supprimé'}[a] || a }
function iconFor(a){ return {creation:'heroicons:plus-circle', modification:'heroicons:pencil-square', suppression:'heroicons:trash'}[a] || 'heroicons:clock' }
function iconWrap(a){ return {creation:'bg-emerald-50', modification:'bg-sky-50', suppression:'bg-rose-50'}[a] || 'bg-gray-100' }
function iconColor(a){ return {creation:'text-emerald-600', modification:'text-sky-600', suppression:'text-rose-600'}[a] || 'text-gray-500' }
function badgeFor(a){ return {creation:'bg-emerald-50 text-emerald-700', modification:'bg-sky-50 text-sky-700', suppression:'bg-rose-50 text-rose-700'}[a] || 'bg-gray-100 text-gray-600' }
function fmt(iso){ if(!iso) return ''; return new Date(iso).toLocaleString('fr-FR',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}) }
</script>
