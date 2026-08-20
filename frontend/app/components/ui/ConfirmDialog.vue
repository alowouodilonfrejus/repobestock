<template>
  <div
    v-if="state.visible"
    class="fixed inset-0 z-[90] flex items-center justify-center bg-black/40 p-4"
    @click.self="closeConfirm(false)"
  >
    <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-8">
      <div class="flex items-start gap-4">
        <span
          class="flex-shrink-0 w-11 h-11 rounded-full flex items-center justify-center"
          :class="state.danger ? 'bg-red-50 text-red-600' : 'bg-blue-50 text-blue-900'"
        >
          <Icon name="heroicons:exclamation-triangle" class="h-6 w-6" />
        </span>
        <div class="flex-1">
          <h3 class="text-xl font-bold text-gray-900">{{ state.title }}</h3>
          <p class="text-gray-500 mt-2 text-sm leading-snug">{{ state.message }}</p>
        </div>
      </div>

      <div class="flex flex-wrap justify-end gap-4 pt-8">
        <button
          @click="closeConfirm(false)"
          class="px-6 py-2.5 border border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-100 transition"
        >
          Annuler
        </button>
        <button
          @click="closeConfirm(true)"
          class="px-6 py-2.5 rounded-lg text-sm font-semibold text-white transition shadow-sm"
          :class="state.danger ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-900 hover:bg-blue-800'"
        >
          {{ state.confirmLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useConfirm } from '@/composables/useConfirm'

const { state, closeConfirm } = useConfirm()
</script>