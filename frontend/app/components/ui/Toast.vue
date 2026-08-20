<template>
  <div class="fixed top-4 right-4 z-[100] flex flex-col gap-3 w-full max-w-sm px-4 sm:px-0 pointer-events-none">
    <TransitionGroup :css="false" @enter="onEnter" @leave="onLeave">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="pointer-events-auto flex items-start gap-3 rounded-lg bg-white p-4 shadow-lg border pointer-events-auto"
        :class="styles[t.type].border"
        role="status"
      >
        <span class="mt-0.5 flex-shrink-0">
          <Icon :name="styles[t.type].icon" class="h-5 w-5" :class="styles[t.type].text" />
        </span>
        <p class="text-sm text-gray-800 leading-snug flex-1 break-words">{{ t.message }}</p>
        <button @click="dismiss(t.id)" class="text-gray-400 hover:text-gray-600 flex-shrink-0" aria-label="Fermer">
          <Icon name="heroicons:x-mark" class="h-5 w-5" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from '@/composables/useToast'

const { toasts, dismiss } = useToast()

const styles = {
  success: {
    border: 'border-green-200',
    text: 'text-green-600',
    icon: 'heroicons:check-circle',
  },
  error: {
    border: 'border-red-200',
    text: 'text-red-600',
    icon: 'heroicons:x-circle',
  },
  warning: {
    border: 'border-amber-200',
    text: 'text-amber-600',
    icon: 'heroicons:exclamation-triangle',
  },
  info: {
    border: 'border-blue-200',
    text: 'text-blue-600',
    icon: 'heroicons:information-circle',
  },
}

function onEnter(el, done) {
  el.style.opacity = '0'
  el.style.transform = 'translateX(24px)'
  requestAnimationFrame(() => {
    el.style.transition = 'opacity .25s ease, transform .25s ease'
    el.style.opacity = '1'
    el.style.transform = 'translateX(0)'
  })
  setTimeout(done, 250)
}

function onLeave(el, done) {
  el.style.transition = 'opacity .2s ease, transform .2s ease'
  el.style.opacity = '0'
  el.style.transform = 'translateX(24px)'
  setTimeout(done, 200)
}
</script>