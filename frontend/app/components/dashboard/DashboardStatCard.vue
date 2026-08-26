<template>
  <div class="bg-white rounded-2xl border border-gray-200 p-5 flex flex-col hover:shadow-sm hover:border-gray-300 transition">
    <div class="flex items-start justify-between gap-3">
      <div class="h-9 w-9 rounded-xl flex items-center justify-center shrink-0" :class="iconBg">
        <Icon :name="icon" class="h-5 w-5" :class="iconColor" />
      </div>
      <span v-if="to" class="text-xs font-semibold text-blue-700 hover:text-blue-800">
        <NuxtLink :to="to" class="inline-flex items-center gap-1">Voir <Icon name="heroicons:arrow-top-right-on-square" class="h-3.5 w-3.5" /></NuxtLink>
      </span>
    </div>
    <p class="mt-4 text-[13px] font-semibold tracking-wide text-gray-500 uppercase">{{ title }}</p>
    <p class="mt-1 text-[28px] font-extrabold leading-none tracking-tight text-gray-900">{{ displayValue }}</p>
    <p v-if="subtitle" class="mt-2 text-xs font-medium" :class="subtitleClass">{{ subtitle }}</p>
    <div v-if="hint" class="mt-3 flex items-center gap-1.5 text-xs text-gray-500">
      <span class="h-1.5 w-1.5 rounded-full" :class="dotClass"></span> {{ hint }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  title: String,
  value: [Number, String],
  icon: String,
  subtitle: String,
  hint: String,
  to: String,
  variant: { type: String, default: 'default' }, // default, success, info, warning, danger
})

const displayValue = computed(() => {
  if (props.value === null || props.value === undefined) return '—'
  return props.value
})

const variantMap = {
  default: { bg: 'bg-slate-50', icon: 'text-slate-700', dot: 'bg-slate-400', sub: 'text-gray-500' },
  success: { bg: 'bg-emerald-50', icon: 'text-emerald-600', dot: 'bg-emerald-500', sub: 'text-emerald-700' },
  info: { bg: 'bg-sky-50', icon: 'text-sky-600', dot: 'bg-sky-500', sub: 'text-sky-700' },
  warning: { bg: 'bg-amber-50', icon: 'text-amber-600', dot: 'bg-amber-500', sub: 'text-amber-700' },
  danger: { bg: 'bg-rose-50', icon: 'text-rose-600', dot: 'bg-rose-500', sub: 'text-rose-700' },
}
const v = computed(() => variantMap[props.variant] || variantMap.default)
const iconBg = computed(() => v.value.bg)
const iconColor = computed(() => v.value.icon)
const dotClass = computed(() => v.value.dot)
const subtitleClass = computed(() => props.variant !== 'default' ? v.value.sub : 'text-gray-500')
</script>
